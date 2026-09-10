import os
import re
import json 
import logging
from typing import Dict, List, Optional

from groq import Groq

logger = logging.getLogger('ats_resume_scorer')

GROQ_PRIMARY_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
GROQ_FALLBACK_MODELS = ['llama-3.1-8b-instant', 'llama-3.1-70b-versatile', 'mixtral-8x7b-32768']

_client = None
_groq_available = True

def _get_client() -> Optional[Groq]:
    global _client, _groq_available
    if not _groq_available:
        return None
    if _client is not None:
        return _client
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        _groq_available = False
        return None
    try:
        _client = Groq(api_key=api_key)
        return _client
    except Exception as exc:
        logger.warning(f"Could not initialize Groq client: {exc}")
        _groq_available = False
        return None

RESUME_SYSTEM_PROMPT = (
    "You are a resume parser. Extract information from the resume "
    "and return ONLY a valid JSON object. No explanation, no markdown."
)

RESUME_USER_PROMPT = """Extract the following from this resume and return as JSON:
{{
  "name": "full name",
  "email": "email address",
  "phone": "phone number",
  "linkedin": "LinkedIn URL if present, otherwise null",
  "github": "GitHub URL if present, otherwise null",
  "professional_summary": "the full text of the Summary, Profile, About Me, Objective, or Professional Summary section at the top of the resume. Copy the ENTIRE paragraph exactly as written. If no such section exists, return an empty string.",
  "skills": ["list", "of", "skills"],
  "experience": [
    {{
      "job_title": "",
      "company": "",
      "start_date": "",
      "end_date": "",
      "duration_months": 0,
      "description": ""
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "year": ""
    }}
  ],
  "certifications": ["list of certifications"],
  "projects": [
    {{
      "title": "project name",
      "description": "what the project does and how it was built",
      "technologies": ["tech", "used"]
    }}
  ],
  "action_verbs": ["strong action verbs used in bullet points, e.g. developed, implemented, designed"],
  "keywords": ["important keywords and phrases from the resume for ATS matching"]
}}

Important instructions:
- For duration_months, calculate the number of months between start_date and end_date. If end_date is "Present" or "Current", calculate from start_date to now.
- For skills, extract ALL technical and soft skills mentioned anywhere in the resume.
- For action_verbs, find verbs that start bullet points or describe achievements.
- For keywords, extract noun phrases and technical terms relevant to ATS matching.
- Return ONLY valid JSON. No markdown code fences, no explanation.

Resume Text:
{raw_text}"""

JD_SYSTEM_PROMPT = (
    "You are a job description parser. Extract information and "
    "return ONLY a valid JSON object. No explanation, no markdown."
)

JD_USER_PROMPT = """Extract the following from this job description and return as JSON:
{{
  "job_title": "",
  "required_skills": ["list of must-have skills"],
  "preferred_skills": ["list of nice-to-have skills"],
  "experience_required": "",
  "education_required": "",
  "key_responsibilities": ["list of responsibilities"],
  "keywords": ["important keywords and phrases for ATS matching"]
}}

Important instructions:
- required_skills: skills explicitly stated as required or must-have.
- preferred_skills: skills stated as preferred, nice-to-have, or bonus.
- keywords: extract ALL important terms an ATS system would match against,
  including skills, technologies, certifications, and domain terms.
- Return ONLY valid JSON. No markdown code fences, no explanation.

Job Description Text:
{raw_text}"""


def _call_groq(client: Groq, system_prompt: str, user_prompt: str) -> str:
    global _groq_available
    if not _groq_available:
        raise RuntimeError("Groq disabled due to authentication or configuration error.")

    models_to_try = [GROQ_PRIMARY_MODEL] + [m for m in GROQ_FALLBACK_MODELS if m != GROQ_PRIMARY_MODEL]
    last_exc = None

    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name, 
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.0,
                max_tokens=4096,
                timeout=15.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            last_exc = exc
            err_str = str(exc).lower()
            if 'invalid_api_key' in err_str or '401' in err_str:
                logger.warning(f"Groq API key is invalid ({exc}) - switching to local parser fallback.")
                _groq_available = False
                raise exc
            if 'model_not_found' in err_str or '404' in err_str or 'does not exist' in err_str or 'decommissioned' in err_str:
                logger.warning(f"Groq model '{model_name}' not available ({exc}), trying fallback model...")
                continue
            raise exc

    raise last_exc or RuntimeError("All Groq model attempts failed.")


def _try_parse_json(text: str) -> Optional[dict]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.index("\n") if "\n" in cleaned else len(cleaned)
        cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


# Curated dictionary for rule-based / offline resume extraction
COMMON_SKILLS_CATALOG = [
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "ruby", "go", "golang", "rust", "php",
    "html", "css", "react", "angular", "vue", "next.js", "node.js", "express", "fastapi", "flask", "django",
    "spring", "spring boot", "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "nosql",
    "docker", "kubernetes", "aws", "azure", "gcp", "git", "github", "gitlab", "ci/cd", "jenkins",
    "linux", "bash", "rest api", "graphql", "microservices", "unit testing", "pytest", "machine learning",
    "deep learning", "nlp", "computer vision", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    "data science", "data analysis", "tableau", "power bi", "agile", "scrum", "jira", "figma"
]

COMMON_ACTION_VERBS = [
    "developed", "built", "designed", "implemented", "created", "engineered", "led", "managed",
    "deployed", "optimized", "architected", "analyzed", "automated", "collaborated", "integrated",
    "spearheaded", "improved", "launched", "maintained", "orchestrated", "refactored", "resolved"
]


def _fallback_parse_resume(raw_text: str) -> Dict:
    """Intelligent local heuristic & regex parser if Groq API is unavailable or down."""
    logger.info("Using local NLP/heuristic parser fallback for resume parsing.")
    text = raw_text or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Extract name (typically first line that isn't an email/URL/phone)
    name = ""
    for line in lines[:5]:
        if not re.search(r'[@\+0-9]|http|www|github|linkedin', line, re.I) and len(line.split()) <= 4:
            name = line
            break

    # Contact extraction
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0) if email_match else None

    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else None

    linkedin_match = re.search(r'https?://[w\.]*linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.I)
    linkedin = linkedin_match.group(0) if linkedin_match else None

    github_match = re.search(r'https?://[w\.]*github\.com/[a-zA-Z0-9_-]+', text, re.I)
    github = github_match.group(0) if github_match else None

    # Summary extraction
    summary = ""
    summary_match = re.search(r'(?:summary|profile|about me|objective)[\s:]*\n+(.*?)(?=\n+[A-Z\s]{3,}|\Z)', text, re.I | re.S)
    if summary_match:
        summary = summary_match.group(1).strip()
    elif len(lines) > 2:
        summary = " ".join(lines[1:3])

    # Skills extraction via catalog matching
    text_lower = text.lower()
    matched_skills = []
    for skill in COMMON_SKILLS_CATALOG:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            matched_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    # Action verbs
    matched_verbs = []
    for verb in COMMON_ACTION_VERBS:
        if re.search(r'\b' + verb + r'\b', text_lower):
            matched_verbs.append(verb)

    # Keywords (skills + significant technical tokens)
    keywords = list(set(matched_skills + [v for v in matched_verbs]))

    # Projects
    projects = []
    proj_matches = re.finditer(r'(?:project|developed|built)\s+([A-Za-z0-9\s_-]{3,40})[:\-]([^\n]+)', text, re.I)
    for p in proj_matches:
        projects.append({
            "title": p.group(1).strip(),
            "description": p.group(2).strip(),
            "technologies": [s for s in matched_skills if s.lower() in p.group(0).lower()]
        })

    if not projects and matched_skills:
        projects.append({
            "title": "Technical Projects",
            "description": f"Applied {', '.join(matched_skills[:4])} across engineering solutions.",
            "technologies": matched_skills[:4]
        })

    # Experience fallback
    experience = []
    exp_section = re.search(r'(?:experience|work history|employment)[\s:]*\n+(.*?)(?=\n+[A-Z\s]{3,}|\Z)', text, re.I | re.S)
    if exp_section:
        exp_lines = [l.strip() for l in exp_section.group(1).splitlines() if l.strip()]
        if exp_lines:
            experience.append({
                "job_title": exp_lines[0],
                "company": exp_lines[1] if len(exp_lines) > 1 else "Company",
                "start_date": "",
                "end_date": "Present",
                "duration_months": 12,
                "description": " ".join(exp_lines[2:5]) if len(exp_lines) > 2 else exp_lines[0]
            })

    # Education fallback
    education = []
    edu_match = re.search(r'(?:bachelor|master|b\.?tech|b\.?s\.?|m\.?s\.?|degree|university|college)[^\n]+', text, re.I)
    if edu_match:
        education.append({
            "degree": edu_match.group(0).strip(),
            "institution": "University / College",
            "year": ""
        })

    return _validate_resume_result({
        "name": name or "Candidate",
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github,
        "professional_summary": summary,
        "skills": matched_skills,
        "experience": experience,
        "education": education,
        "certifications": [],
        "projects": projects,
        "action_verbs": matched_verbs,
        "keywords": keywords,
    })


def _fallback_parse_job_description(raw_text: str) -> Dict:
    """Intelligent local heuristic parser for JD when Groq API is unavailable."""
    logger.info("Using local NLP/heuristic parser fallback for job description.")
    text = raw_text or ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    job_title = lines[0] if lines else "Target Role"

    text_lower = text.lower()
    matched_skills = []
    for skill in COMMON_SKILLS_CATALOG:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            matched_skills.append(skill.title() if len(skill) > 3 else skill.upper())

    responsibilities = [l for l in lines if l.startswith(("-", "•", "*", "–")) or len(l) > 40][:5]

    return _validate_jd_result({
        "job_title": job_title,
        "required_skills": matched_skills[:len(matched_skills)//2 + 1] if matched_skills else [],
        "preferred_skills": matched_skills[len(matched_skills)//2 + 1:] if matched_skills else [],
        "experience_required": "2+ years",
        "education_required": "Bachelor's Degree",
        "key_responsibilities": responsibilities,
        "keywords": matched_skills,
    })


def parse_resume(raw_text: str) -> Dict:
    client = _get_client()
    if client is None:
        return _fallback_parse_resume(raw_text)

    prompt = RESUME_USER_PROMPT.format(raw_text=raw_text)
    try:
        raw_response = _call_groq(client, RESUME_SYSTEM_PROMPT, prompt)
        result = _try_parse_json(raw_response)
        if result is not None:
            return _validate_resume_result(result)

        logger.warning("Groq resume parse: first attempt returned invalid JSON, retrying with strict prompt...")
        strict_prompt = (
            "Your previous response was not valid JSON. "
            "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
            + prompt
        )
        raw_response = _call_groq(client, RESUME_SYSTEM_PROMPT, strict_prompt)
        result = _try_parse_json(raw_response)
        if result is not None:
            return _validate_resume_result(result)
        
        logger.warning("Groq retry also returned non-JSON, falling back to local heuristic parser.")
        return _fallback_parse_resume(raw_text)
    except Exception as exc:
        logger.warning(f"Groq parse_resume failed ({exc}) - smoothly falling back to local NLP parser.")
        global _groq_available
        _groq_available = False
        return _fallback_parse_resume(raw_text)


def parse_job_description(raw_text: str) -> Dict:
    client = _get_client()
    if client is None:
        return _fallback_parse_job_description(raw_text)

    prompt = JD_USER_PROMPT.format(raw_text=raw_text)
    try:
        raw_response = _call_groq(client, JD_SYSTEM_PROMPT, prompt)
        result = _try_parse_json(raw_response)
        if result is not None:
            return _validate_jd_result(result)

        logger.warning("Groq JD parse: first attempt returned invalid JSON, retrying...")
        strict_prompt = (
            "Your previous response was not valid JSON. "
            "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
            + prompt
        )
        raw_response = _call_groq(client, JD_SYSTEM_PROMPT, strict_prompt)
        result = _try_parse_json(raw_response)
        if result is not None:
            return _validate_jd_result(result)

        logger.warning("Groq JD retry also returned non-JSON, falling back to local heuristic parser.")
        return _fallback_parse_job_description(raw_text)
    except Exception as exc:
        logger.warning(f"Groq parse_job_description failed ({exc}) - smoothly falling back to local NLP parser.")
        _groq_available = False
        return _fallback_parse_job_description(raw_text)


def _validate_jd_result(result: dict) -> dict:
    defaults = {
        "job_title": "",
        "required_skills": [],
        "preferred_skills": [],
        "experience_required": "",
        "education_required": "",
        "key_responsibilities": [],
        "keywords": [],
    }

    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default

    return result


def _validate_resume_result(result: dict) -> dict:
    defaults = {
        "name": "",
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "professional_summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
        "action_verbs": [],
        "keywords": [],
    }
    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default

    for exp in result.get("experience", []):
        if not isinstance(exp, dict):
            continue
        exp.setdefault("job_title", "")
        exp.setdefault("company", "")
        exp.setdefault("start_date", "")
        exp.setdefault("end_date", "")
        exp.setdefault("duration_months", 0)
        exp.setdefault("description", "")
        try:
            exp["duration_months"] = int(exp["duration_months"])
        except (ValueError, TypeError):
            exp["duration_months"] = 0

    for proj in result.get("projects", []):
        if not isinstance(proj, dict):
            continue
        proj.setdefault("title", "")
        proj.setdefault("description", "")
        proj.setdefault("technologies", [])

    return result