import re
import logging
from typing import List, Dict, Optional, Tuple, Any, Set, Union
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from rapidfuzz import fuzz

from backend.utils.matching import (
    fuzzy_match_keywords,
    normalize_skill,
    is_fuzzy_match,
    is_keyword_in_text,
)
from backend.core.config import JD_KEYWORD_WEIGHT, JD_SEMANTIC_WEIGHT
from backend.utils.file_utils import (
    get_default_jd_comparison_results,
    log_error,
    log_info,
    log_warning,
)

logger = logging.getLogger('ats_resume_scorer')


# ---------------------------------------------------------------------------
# 1. Semantic Similarity Calculation
# ---------------------------------------------------------------------------

def _chunk_text(text: str, max_words: int = 250) -> List[str]:
    """Splits a long text into overlapping chunks for embedding models."""
    words = text.split()
    if not words:
        return []
    if len(words) <= max_words:
        return [text]

    chunks = []
    step = int(max_words * 0.8)
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + max_words])
        if chunk:
            chunks.append(chunk)
    return chunks


def calculate_semantic_similarity(
    resume_text: str,
    jd_text: str,
    embedder: Optional[SentenceTransformer] = None,
    nlp: Optional[Any] = None,
) -> float:
    """
    Calculates semantic similarity percentage (0.0 to 100.0) between resume text and job description.
    Uses SentenceTransformer embeddings with cosine similarity and mean pooling across text chunks.
    Falls back to spaCy document vectors or token set similarity if embedder is unavailable.
    """
    if not resume_text or not jd_text or not resume_text.strip() or not jd_text.strip():
        return 0.0

    # Primary: SentenceTransformer embeddings with chunk pooling
    if embedder is not None:
        try:
            resume_chunks = _chunk_text(resume_text, max_words=250)
            jd_chunks = _chunk_text(jd_text, max_words=250)

            resume_embeddings = embedder.encode(resume_chunks, show_progress_bar=False, normalize_embeddings=True)
            jd_embeddings = embedder.encode(jd_chunks, show_progress_bar=False, normalize_embeddings=True)

            # Average pooled vectors
            vec_resume = np.mean(resume_embeddings, axis=0)
            vec_jd = np.mean(jd_embeddings, axis=0)

            norm_resume = np.linalg.norm(vec_resume)
            norm_jd = np.linalg.norm(vec_jd)

            if norm_resume == 0 or norm_jd == 0:
                return 0.0

            cosine_sim = float(np.dot(vec_resume, vec_jd) / (norm_resume * norm_jd))
            # Rescale / clamp to [0.0, 1.0]
            similarity = max(0.0, min(1.0, cosine_sim))
            return round(similarity * 100.0, 2)
        except Exception as e:
            log_warning(
                f"SentenceTransformer semantic similarity failed: {e}. Trying spaCy fallback...",
                context="calculate_semantic_similarity"
            )

    # Secondary: spaCy document similarity fallback
    if nlp is not None:
        try:
            doc_resume = nlp(resume_text[:20000])  # limit max characters for memory safety
            doc_jd = nlp(jd_text[:20000])
            if doc_resume.vector_norm and doc_jd.vector_norm:
                similarity = float(doc_resume.similarity(doc_jd))
                similarity = max(0.0, min(1.0, similarity))
                return round(similarity * 100.0, 2)
        except Exception as e:
            log_warning(
                f"spaCy semantic similarity fallback failed: {e}",
                context="calculate_semantic_similarity"
            )

    # Tertiary: Fuzzy token set similarity fallback
    try:
        ratio = fuzz.token_set_ratio(resume_text[:4000], jd_text[:4000])
        return round(float(ratio), 2)
    except Exception as e:
        log_error(e, context="calculate_semantic_similarity_fallback")
        return 0.0


# ---------------------------------------------------------------------------
# 2. Keyword Matching & Extraction
# ---------------------------------------------------------------------------

def identify_matched_keywords(
    resume_keywords_or_text: Union[List[str], Set[str], str],
    jd_keywords: List[str],
    threshold: float = 80.0,
) -> List[str]:
    """
    Identifies which keywords from the job description are present in the candidate's resume.
    """
    if not jd_keywords or not resume_keywords_or_text:
        return []

    result = fuzzy_match_keywords(
        pool_a=resume_keywords_or_text,
        pool_b=jd_keywords,
        threshold=threshold,
    )
    return result['matched']


def identify_missing_keywords(
    resume_keywords_or_text: Optional[Union[List[str], Set[str], str]] = None,
    jd_keywords: Optional[List[str]] = None,
    top_n: Optional[int] = 15,
    matched_keywords: Optional[List[str]] = None,
) -> List[str]:
    """
    Identifies which JD keywords are missing from the resume.
    Can be called either with (resume_keywords_or_text, jd_keywords) or (matched_keywords, jd_keywords).
    """
    if not jd_keywords:
        return []

    if matched_keywords is not None:
        matched_set = {str(m).strip().lower() for m in matched_keywords if m}
        missing = [k for k in jd_keywords if k and str(k).strip().lower() not in matched_set]
    elif resume_keywords_or_text is not None:
        result = fuzzy_match_keywords(
            pool_a=resume_keywords_or_text,
            pool_b=jd_keywords,
            threshold=80.0,
        )
        missing = result['missing']
    else:
        return []

    if top_n is not None:
        return missing[:top_n]
    return missing


def calculate_match_percentage(
    resume_keywords: List[str],
    jd_keywords: List[str],
    semantic_similarity: float,
) -> float:
    """
    Calculates overall match percentage combining keyword overlap (60%) and semantic similarity (40%).
    """
    if not jd_keywords:
        return 0.0
    matched = identify_matched_keywords(resume_keywords, jd_keywords)
    keyword_overlap = len(matched) / len(jd_keywords)
    sem_factor = semantic_similarity / 100.0 if semantic_similarity > 1.0 else semantic_similarity
    match_pct = (keyword_overlap * 0.6 + sem_factor * 0.4) * 100.0
    return float(np.clip(match_pct, 0.0, 100.0))


def compare_resume_with_jd(
    resume_text: str,
    resume_keywords: List[str],
    resume_skills: List[str],
    jd_text: str,
    jd_keywords: List[str],
    embedder: Optional[SentenceTransformer] = None,
    nlp: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Direct comparison between resume and job description text.
    Used by resume_analyzer.
    """
    raw_sim = calculate_semantic_similarity(resume_text, jd_text, embedder, nlp)
    semantic_similarity = round(raw_sim / 100.0 if raw_sim > 1.0 else raw_sim, 3)

    candidate_pool = list(dict.fromkeys((resume_keywords or []) + (resume_skills or [])))
    matched_keywords = identify_matched_keywords(candidate_pool, jd_keywords)
    missing_keywords = identify_missing_keywords(candidate_pool, jd_keywords, top_n=15)
    gap_result = analyze_skills_gap(resume_skills, jd_text, nlp)
    skills_gap = gap_result if isinstance(gap_result, list) else gap_result.get("skills_gap", [])
    match_percentage = calculate_match_percentage(
        candidate_pool, jd_keywords, semantic_similarity
    )

    return {
        'match_percentage':    round(float(match_percentage), 1),
        'semantic_similarity': semantic_similarity,
        'matched_keywords':    matched_keywords,
        'missing_keywords':    missing_keywords,
        'skills_gap':          skills_gap,
    }


# ---------------------------------------------------------------------------
# 3. Skills Gap Analysis
# ---------------------------------------------------------------------------

def analyze_skills_gap(
    resume_skills: List[str],
    jd_required_or_text: Optional[Union[List[str], str]] = None,
    jd_preferred_or_nlp: Optional[Any] = None,
    threshold: float = 80.0,
    *,
    jd_required_skills: Optional[List[str]] = None,
    jd_preferred_skills: Optional[List[str]] = None,
) -> Any:
    """
    Analyzes gaps between candidate skills and JD required/preferred skills or extracted JD skills.
    Supports:
      1. analyze_skills_gap(resume_skills, jd_text, nlp) -> List[str]
      2. analyze_skills_gap(resume_skills, jd_required_skills, jd_preferred_skills, threshold) -> Dict[str, Any]
      3. analyze_skills_gap(resume_skills, jd_required_skills=..., jd_preferred_skills=...) -> Dict[str, Any]
    """
    if jd_required_skills is not None:
        jd_required_or_text = jd_required_skills
    if jd_preferred_skills is not None:
        jd_preferred_or_nlp = jd_preferred_skills

    # Variant 1: Called with raw JD text string and optional spacy nlp model
    if isinstance(jd_required_or_text, str):
        jd_text = jd_required_or_text
        nlp = jd_preferred_or_nlp
        jd_skills = set()

        if nlp is not None:
            try:
                doc = nlp(jd_text[:5000])
                for ent in doc.ents:
                    if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
                        jd_skills.add(ent.text.lower())
                for chunk in doc.noun_chunks:
                    ct = chunk.text.lower().strip()
                    if 1 <= len(ct.split()) <= 4:
                        jd_skills.add(ct)
            except Exception:
                pass

        if not jd_skills:
            # Word regex extraction fallback
            words = re.findall(r'\b[A-Za-z\+\#\.\-]{2,}\b', jd_text)
            common_stops = {'and', 'the', 'for', 'with', 'you', 'will', 'are', 'our', 'team', 'work'}
            jd_skills = {w.lower() for w in words if len(w) > 2 and w.lower() not in common_stops}

        resume_normalized = {normalize_skill(s) for s in resume_skills if s}
        gap = []
        for jd_skill in jd_skills:
            jd_norm = normalize_skill(jd_skill)
            if not jd_norm or jd_norm in resume_normalized:
                continue
            best_score = max(
                (fuzz.token_sort_ratio(jd_norm, rs) for rs in resume_normalized),
                default=0,
            )
            if best_score < 75:
                gap.append(jd_skill)

        return sorted(gap)[:20]

    # Variant 2: Called with structured skills lists
    jd_required_skills = jd_required_or_text or []
    jd_preferred_skills = jd_preferred_or_nlp or []

    clean_resume_skills = [s.strip() for s in resume_skills if s and isinstance(s, str)]
    clean_req_skills = [s.strip() for s in jd_required_skills if s and isinstance(s, str)]
    clean_pref_skills = [s.strip() for s in jd_preferred_skills if s and isinstance(s, str)]

    res_req = fuzzy_match_keywords(clean_resume_skills, clean_req_skills, threshold=threshold)
    matched_required = res_req['matched']
    missing_required = res_req['missing']

    res_pref = fuzzy_match_keywords(clean_resume_skills, clean_pref_skills, threshold=threshold)
    matched_preferred = res_pref['matched']
    missing_preferred = res_pref['missing']

    skills_gap = list(dict.fromkeys(missing_required + missing_preferred))

    total_required = len(clean_req_skills)
    required_coverage = round((len(matched_required) / total_required * 100.0), 2) if total_required > 0 else 100.0

    total_all_skills = total_required + len(clean_pref_skills)
    matched_all_skills = len(matched_required) + len(matched_preferred)
    total_coverage = round((matched_all_skills / total_all_skills * 100.0), 2) if total_all_skills > 0 else 100.0

    return {
        "skills_gap": skills_gap,
        "missing_required_skills": missing_required,
        "matched_required_skills": matched_required,
        "missing_preferred_skills": missing_preferred,
        "matched_preferred_skills": matched_preferred,
        "required_skills_coverage_pct": required_coverage,
        "total_skills_coverage_pct": total_coverage,
    }


# ---------------------------------------------------------------------------
# 4. Experience & Education Matching
# ---------------------------------------------------------------------------

def analyze_experience_match(
    resume_experience: List[Dict[str, Any]],
    jd_experience_required: str,
) -> Dict[str, Any]:
    """
    Evaluates candidate's total experience in months/years against the JD experience requirement.
    """
    total_months = 0
    for exp in resume_experience:
        if isinstance(exp, dict):
            try:
                months = int(exp.get("duration_months", 0))
                total_months += max(0, months)
            except (ValueError, TypeError):
                pass

    total_years = round(total_months / 12.0, 1)

    # Extract required years using regex from JD string
    req_years = 0.0
    if jd_experience_required:
        match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:to\s*\d+\s*)?(?:years?|yrs?)", jd_experience_required, re.IGNORECASE)
        if match:
            try:
                req_years = float(match.group(1))
            except ValueError:
                req_years = 0.0

    meets_requirement = total_years >= req_years if req_years > 0 else True

    return {
        "candidate_experience_years": total_years,
        "candidate_experience_months": total_months,
        "required_experience": jd_experience_required,
        "required_years_extracted": req_years,
        "meets_experience_requirement": meets_requirement,
    }


def analyze_education_match(
    resume_education: List[Dict[str, Any]],
    jd_education_required: str,
) -> Dict[str, Any]:
    """
    Evaluates candidate education degrees against JD requirements.
    """
    if not jd_education_required:
        return {"meets_education_requirement": True, "detected_degrees": [], "required_education": ""}

    DEGREE_HIERARCHY = {
        "phd": 4,
        "doctorate": 4,
        "master": 3,
        "m.s": 3,
        "m.tech": 3,
        "mba": 3,
        "bachelor": 2,
        "b.s": 2,
        "b.tech": 2,
        "b.e": 2,
        "associate": 1,
        "diploma": 1,
    }

    req_level = 0
    jd_lower = jd_education_required.lower()
    for deg, level in DEGREE_HIERARCHY.items():
        if deg in jd_lower:
            req_level = max(req_level, level)

    candidate_degrees = []
    max_candidate_level = 0
    for edu in resume_education:
        degree_str = str(edu.get("degree", "")).lower()
        candidate_degrees.append(edu.get("degree", ""))
        for deg, level in DEGREE_HIERARCHY.items():
            if deg in degree_str:
                max_candidate_level = max(max_candidate_level, level)

    meets_req = max_candidate_level >= req_level if req_level > 0 else True

    return {
        "meets_education_requirement": meets_req,
        "detected_degrees": candidate_degrees,
        "required_education": jd_education_required,
        "candidate_degree_level": max_candidate_level,
        "required_degree_level": req_level,
    }


# ---------------------------------------------------------------------------
# 5. Recommendation & Suggestion Generator
# ---------------------------------------------------------------------------

def generate_jd_suggestions(
    missing_keywords: List[str],
    skills_gap: List[str],
    experience_analysis: Dict[str, Any],
    semantic_similarity: float,
) -> List[str]:
    """
    Generates actionable ATS optimization recommendations based on JD matching results.
    """
    suggestions = []

    # High priority: Missing top skills
    if skills_gap:
        top_missing_skills = skills_gap[:5]
        suggestions.append(
            f"Add key required/preferred skills to your resume: {', '.join(top_missing_skills)}."
        )

    # Keywords integration
    remaining_kws = [kw for kw in missing_keywords if kw not in skills_gap]
    if remaining_kws:
        top_kws = remaining_kws[:5]
        suggestions.append(
            f"Incorporate relevant ATS keywords into your project and experience bullet points: {', '.join(top_kws)}."
        )

    # Semantic similarity
    if semantic_similarity < 60.0:
        suggestions.append(
            "Tailor your Professional Summary and project descriptions using terminology from the job description to improve semantic alignment."
        )

    # Experience alignment
    if not experience_analysis.get("meets_experience_requirement", True):
        req_yrs = experience_analysis.get("required_years_extracted", 0)
        cand_yrs = experience_analysis.get("candidate_experience_years", 0)
        suggestions.append(
            f"The job requires approx. {req_yrs}+ years of experience (detected {cand_yrs} years). Highlight freelance, internships, or relevant project leadership to strengthen seniority."
        )

    return suggestions


# ---------------------------------------------------------------------------
# 6. Main Job Description Matcher
# ---------------------------------------------------------------------------

def match_job_description(
    resume_data: Dict[str, Any],
    jd_data: Dict[str, Any],
    embedder: Optional[SentenceTransformer] = None,
    nlp: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Comprehensive job description matching orchestrator.
    Compares candidate resume against target job description using semantic embeddings,
    keyword matching, skills gap breakdown, experience check, and education alignment.
    
    Args:
        resume_data: Parsed resume data dictionary (including raw_text, skills, keywords, experience, education).
        jd_data: Parsed job description dictionary (including raw_text, required_skills, preferred_skills, keywords).
        embedder: Optional SentenceTransformer embedder instance.
        nlp: Optional spaCy NLP model instance.
        
    Returns:
        Dict conforming to JDComparison schema:
            - match_percentage: float (0.0 to 100.0)
            - semantic_similarity: float (0.0 to 100.0)
            - matched_keywords: List[str]
            - missing_keywords: List[str]
            - skills_gap: List[str]
            - keyword_match_percentage: float
            - experience_analysis: Dict
            - education_analysis: Dict
            - suggestions: List[str]
    """
    try:
        # 1. Extract texts
        resume_text = resume_data.get("raw_text") or resume_data.get("text") or ""
        jd_text = jd_data.get("raw_text") or jd_data.get("text") or ""

        # 2. Extract keywords and skills
        resume_skills = [str(s).strip() for s in resume_data.get("skills", []) if s and isinstance(s, str)]
        resume_keywords = [str(k).strip() for k in resume_data.get("keywords", []) if k and isinstance(k, str)]

        # Combine all resume textual keyword pool
        resume_pool: List[str] = list(dict.fromkeys(resume_skills + resume_keywords))

        jd_keywords = [str(k).strip() for k in jd_data.get("keywords", []) if k and isinstance(k, str)]
        jd_required = [str(k).strip() for k in jd_data.get("required_skills", []) if k and isinstance(k, str)]
        jd_preferred = [str(k).strip() for k in jd_data.get("preferred_skills", []) if k and isinstance(k, str)]

        # Combine all JD keywords to match
        all_jd_keywords = list(dict.fromkeys(jd_keywords + jd_required + jd_preferred))

        # 3. Calculate Semantic Similarity
        semantic_sim = calculate_semantic_similarity(
            resume_text=resume_text,
            jd_text=jd_text,
            embedder=embedder,
            nlp=nlp,
        )

        # 4. Identify Matched and Missing Keywords
        reference_pool: Union[List[str], str] = resume_pool if resume_pool else resume_text
        matched_keywords = identify_matched_keywords(
            resume_keywords_or_text=reference_pool,
            jd_keywords=all_jd_keywords,
        )
        missing_keywords = identify_missing_keywords(
            matched_keywords=matched_keywords,
            jd_keywords=all_jd_keywords,
        )

        # 5. Analyze Skills Gap
        skills_gap_analysis = analyze_skills_gap(
            resume_skills=resume_skills if resume_skills else resume_pool,
            jd_required_skills=jd_required,
            jd_preferred_skills=jd_preferred,
        )

        # 6. Analyze Experience & Education
        experience_analysis = analyze_experience_match(
            resume_experience=resume_data.get("experience", []),
            jd_experience_required=jd_data.get("experience_required", ""),
        )
        education_analysis = analyze_education_match(
            resume_education=resume_data.get("education", []),
            jd_education_required=jd_data.get("education_required", ""),
        )

        # 7. Compute Keyword Match Percentage
        total_target_kws = len(all_jd_keywords)
        if total_target_kws > 0:
            keyword_match_pct = (len(matched_keywords) / total_target_kws) * 100.0
        else:
            keyword_match_pct = 100.0 if not jd_text else 0.0

        # 8. Compute Combined Overall Match Percentage
        overall_match = (JD_KEYWORD_WEIGHT * keyword_match_pct) + (JD_SEMANTIC_WEIGHT * semantic_sim)
        overall_match = max(0.0, min(100.0, overall_match))

        # 9. Generate targeted suggestions
        suggestions = generate_jd_suggestions(
            missing_keywords=missing_keywords,
            skills_gap=skills_gap_analysis["skills_gap"],
            experience_analysis=experience_analysis,
            semantic_similarity=semantic_sim,
        )

        result = {
            "match_percentage": round(overall_match, 2),
            "semantic_similarity": round(semantic_sim, 2),
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "skills_gap": skills_gap_analysis["skills_gap"],
            "keyword_match_percentage": round(keyword_match_pct, 2),
            "skills_gap_details": skills_gap_analysis,
            "experience_analysis": experience_analysis,
            "education_analysis": education_analysis,
            "suggestions": suggestions,
            "_component_status": "success",
        }

        log_info(
            f"JD Match completed: Score={result['match_percentage']}%, Semantic={result['semantic_similarity']}%, "
            f"Matched={len(matched_keywords)}/{total_target_kws}",
            context="match_job_description",
        )
        return result

    except Exception as e:
        log_error(e, context="match_job_description")
        default_res = get_default_jd_comparison_results()
        default_res["_note"] = f"Error during JD comparison: {str(e)}"
        return default_res


# ---------------------------------------------------------------------------
# 7. Direct Text Comparison Helper (Optional Groq LLM integration)
# ---------------------------------------------------------------------------

def compare_resume_and_jd_text(
    resume_text: str,
    jd_text: str,
    embedder: Optional[SentenceTransformer] = None,
    nlp: Optional[Any] = None,
    use_groq: bool = False,
) -> Dict[str, Any]:
    """
    Helper function to compare raw resume text and job description text directly.
    Optionally leverages Groq LLM parser if structured fields need extraction on the fly.
    """
    if not resume_text.strip() or not jd_text.strip():
        return get_default_jd_comparison_results()

    resume_data = {"raw_text": resume_text}
    jd_data = {"raw_text": jd_text}

    if use_groq:
        try:
            from backend.services.groq_parser import parse_resume, parse_job_description
            parsed_resume = parse_resume(resume_text)
            parsed_jd = parse_job_description(jd_text)
            parsed_resume["raw_text"] = resume_text
            parsed_jd["raw_text"] = jd_text
            resume_data = parsed_resume
            jd_data = parsed_jd
        except Exception as e:
            log_warning(f"Groq parsing failed during JD match: {e}. Proceeding with text extraction.", context="compare_resume_and_jd_text")

    return match_job_description(
        resume_data=resume_data,
        jd_data=jd_data,
        embedder=embedder,
        nlp=nlp,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Testing JD Matcher Service...")
    print("=" * 60)

    sample_resume = (
        "Senior Software Engineer with 4 years of experience building scalable "
        "microservices with Python, FastAPI, Docker, and PostgreSQL. Experienced "
        "in designing RESTful APIs, Redis caching, CI/CD with GitHub Actions, "
        "and cloud deployment on AWS."
    )

    sample_jd = (
        "We are looking for a Senior Backend Developer. Requirements: 3+ years of "
        "experience in Python, FastAPI, Docker, and Kubernetes. Strong knowledge of "
        "PostgreSQL, Redis, and microservices architecture. Familiarity with AWS and CI/CD."
    )

    resume_skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "RESTful APIs", "Redis", "AWS", "Git"]
    jd_keywords = ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "Redis", "AWS", "CI/CD"]

    result = compare_resume_with_jd(
        resume_text=sample_resume,
        resume_keywords=resume_skills,
        resume_skills=resume_skills,
        jd_text=sample_jd,
        jd_keywords=jd_keywords,
    )

    print("\n--- Match Results ---")
    print(f"Match Percentage:    {result['match_percentage']}%")
    print(f"Semantic Similarity: {result['semantic_similarity']}")
    print(f"Matched Keywords:    {result['matched_keywords']}")
    print(f"Missing Keywords:    {result['missing_keywords']}")
    print(f"Skills Gap:          {result['skills_gap']}")
    print("\n[OK] jd_matcher ran successfully!")
