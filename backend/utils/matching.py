import re
import logging
from typing import List, Set, Union, Optional, Dict, Any
from rapidfuzz import fuzz

logger = logging.getLogger('ats_resume_scorer')

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "react.js": "react",
    "reactjs": "react",
    "node.js": "node",
    "nodejs": "node",
    "vue.js": "vue",
    "vuejs": "vue",
    "angular.js": "angular",
    "angularjs": "angular",
    "next.js": "nextjs",
    "express.js": "express",
    "c++": "cpp",
    "c#": "csharp",
    ".net": "dotnet",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "k8s": "kubernetes",
    "gcp": "google cloud platform",
    "aws": "amazon web services",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "ai": "artificial intelligence",
    "ci/cd": "cicd",
    "git / github": "git",
    "restful api": "rest api",
    "rest apis": "rest api",
    "restful apis": "rest api",
}


def normalize_skill(skill: str) -> str:
    """
    Normalizes a skill string for accurate comparison.
    - Converts to lowercase
    - Strips leading/trailing whitespace
    - Removes parenthetical additions like 'Python (intermediate)' -> 'python'
    - Maps known aliases/synonyms
    """
    if not skill or not isinstance(skill, str):
        return ""

    cleaned = skill.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Check direct aliases before cleaning parens
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]

    # Remove trailing parentheticals
    cleaned = re.sub(r"\s*\(.*?\)", "", cleaned).strip()

    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]

    return cleaned


def is_fuzzy_match(
    term1: str,
    term2: str,
    threshold: float = 85.0
) -> bool:
    """
    Checks if two terms match either exactly or fuzzily.
    """
    norm1 = normalize_skill(term1)
    norm2 = normalize_skill(term2)

    if not norm1 or not norm2:
        return False

    if norm1 == norm2:
        return True

    # Exact word boundaries match
    if len(norm1) >= 3 and len(norm2) >= 3:
        if re.search(r'\b' + re.escape(norm1) + r'\b', norm2) or re.search(r'\b' + re.escape(norm2) + r'\b', norm1):
            return True

    # Token sort and set ratio
    token_sort = fuzz.token_sort_ratio(norm1, norm2)
    if token_sort >= threshold:
        return True

    token_set = fuzz.token_set_ratio(norm1, norm2)
    if token_set >= threshold:
        return True

    return False


def is_keyword_in_text(
    keyword: str,
    text: str,
    threshold: float = 85.0
) -> bool:
    """
    Checks whether a keyword exists in a body of text (exact match, normalized match, or fuzzy partial match).
    """
    if not keyword or not text:
        return False

    norm_keyword = normalize_skill(keyword)
    norm_text = text.lower()

    if not norm_keyword:
        return False

    # Regex word boundary match
    pattern = r'\b' + re.escape(norm_keyword) + r'\b'
    if re.search(pattern, norm_text):
        return True

    # Check aliases in text
    for alias, canonical in SKILL_ALIASES.items():
        if canonical == norm_keyword:
            alias_pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(alias_pattern, norm_text):
                return True

    # Partial ratio check for multi-word keywords
    if " " in norm_keyword:
        ratio = fuzz.partial_ratio(norm_keyword, norm_text)
        if ratio >= threshold:
            return True

    return False


class FuzzyMatchResult(dict):
    """
    Result container that behaves like a dictionary with 'matched' and 'missing' keys,
    while also supporting direct list-like iteration and len() over 'matched'.
    """
    def __init__(self, matched: List[str], missing: List[str]):
        super().__init__(matched=matched, missing=missing)
        self.matched = matched
        self.missing = missing

    def __iter__(self):
        return iter(self['matched'])

    def __len__(self):
        return len(self['matched'])

    def __getitem__(self, item):
        if isinstance(item, int):
            return self['matched'][item]
        return super().__getitem__(item)


def fuzzy_match_keywords(
    pool_a: Union[List[str], Set[str], str],
    pool_b: Union[List[str], Set[str], str],
    threshold: float = 80.0
) -> FuzzyMatchResult:
    """
    Compares keywords between candidate resume terms and target job description keywords.
    Returns FuzzyMatchResult with 'matched' and 'missing' keyword lists.
    """
    if not pool_a and not pool_b:
        return FuzzyMatchResult(matched=[], missing=[])

    # Determine which pool represents target keywords to check vs reference pool
    if isinstance(pool_b, str):
        target_keywords = list(pool_a) if isinstance(pool_a, (list, set, tuple)) else [pool_a]
        reference_pool = pool_b
    else:
        # Default: pool_b is target JD keywords, pool_a is candidate resume terms/text
        target_keywords = list(pool_b) if isinstance(pool_b, (list, set, tuple)) else [pool_b]
        reference_pool = pool_a

    matched: List[str] = []
    missing: List[str] = []
    seen: Set[str] = set()

    is_text_pool = isinstance(reference_pool, str)
    normalized_ref_list = []
    if not is_text_pool:
        normalized_ref_list = [normalize_skill(k) for k in reference_pool if k]

    for kw in target_keywords:
        if not kw or not isinstance(kw, str):
            continue

        raw_kw = kw.strip()
        norm_kw = normalize_skill(raw_kw)
        if not norm_kw or norm_kw in seen:
            continue
        seen.add(norm_kw)

        is_match = False
        if is_text_pool:
            if is_keyword_in_text(raw_kw, reference_pool, threshold=threshold):
                is_match = True
        else:
            for ref_raw, ref_norm in zip(reference_pool, normalized_ref_list):
                if norm_kw == ref_norm or is_fuzzy_match(raw_kw, ref_raw, threshold=threshold):
                    is_match = True
                    break

        if is_match:
            matched.append(raw_kw)
        else:
            missing.append(raw_kw)

    return FuzzyMatchResult(matched=matched, missing=missing)
