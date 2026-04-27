from __future__ import annotations

from typing import Dict, List

from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    EDUCATION_KEYWORDS,
    EMBEDDING_WEIGHT,
    RECOMMENDATION_THRESHOLDS,
    SENTENCE_EMBEDDING_MODEL,
    TFIDF_WEIGHT,
)

MODEL = SentenceTransformer(SENTENCE_EMBEDDING_MODEL)


def compute_skill_score(candidate_skills: List[str], jd_required: List[str], jd_preferred: List[str]) -> Dict:
    candidate_set = {skill.lower() for skill in (candidate_skills or [])}
    required_set = {skill.lower() for skill in (jd_required or [])}
    preferred_set = {skill.lower() for skill in (jd_preferred or [])}

    matched_required = sorted(candidate_set.intersection(required_set))
    matched_preferred = sorted(candidate_set.intersection(preferred_set))

    base_score = (len(matched_required) / max(len(required_set), 1)) * 40
    bonus = min(5, len(matched_preferred) * 1.5)
    final_skill_score = min(40, base_score + bonus)
    missing_skills = sorted(required_set - candidate_set)

    return {
        "score": round(final_skill_score, 2),
        "matched_required": matched_required,
        "matched_preferred": matched_preferred,
        "missing_skills": missing_skills,
    }


def compute_experience_score(candidate_exp: float, min_exp: float, max_exp: float) -> float:
    if candidate_exp is None:
        return 5.0

    min_exp = min_exp if min_exp is not None else 0.0
    max_exp = max_exp if max_exp is not None else (min_exp + 3.0)

    if min_exp <= candidate_exp <= max_exp:
        return 25.0

    if candidate_exp < min_exp:
        gap = min_exp - candidate_exp
        if gap <= 0.5:
            return 22.0
        if gap <= 1.0:
            return 18.0
        if gap <= 2.0:
            return 12.0
        return max(0.0, 25.0 - (gap * 5.0))

    excess = candidate_exp - max_exp
    if excess <= 1:
        return 22.0
    if excess <= 3:
        return 18.0
    return 15.0


def compute_semantic_score(resume_text: str, jd_text: str) -> float:
    safe_resume = (resume_text or "").strip()
    safe_jd = (jd_text or "").strip()

    if not safe_resume or not safe_jd:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        vectors = vectorizer.fit_transform([safe_resume, safe_jd])
        tfidf_sim = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
    except ValueError:
        tfidf_sim = 0.0

    try:
        resume_emb = MODEL.encode([safe_resume[:1000]], convert_to_numpy=True)
        jd_emb = MODEL.encode([safe_jd[:1000]], convert_to_numpy=True)
        emb_sim = float(cosine_similarity(resume_emb, jd_emb)[0][0])
    except Exception:
        emb_sim = 0.0

    baseline = 0.25
    calibrated_emb = max(0.0, (emb_sim - baseline) / (1.0 - baseline))
    calibrated_tfidf = tfidf_sim

    combined = (calibrated_tfidf * TFIDF_WEIGHT) + (calibrated_emb * EMBEDDING_WEIGHT)
    return round(min(combined, 1.0) * 20, 2)


def compute_location_score(candidate_loc: str, jd_loc: str) -> float:
    if not jd_loc:
        return 10.0
    if not candidate_loc:
        return 3.0

    candidate_loc = candidate_loc.strip().lower()
    jd_loc = jd_loc.strip().lower()

    if candidate_loc == jd_loc:
        return 10.0
    if "remote" in candidate_loc or "remote" in jd_loc:
        return 8.0

    metro_groups = {
        "delhi": ["delhi", "noida", "gurgaon", "gurugram", "faridabad", "ncr"],
        "mumbai": ["mumbai", "thane", "navi mumbai", "pune"],
        "bangalore": ["bangalore", "bengaluru"],
    }

    for group in metro_groups.values():
        if any(city in candidate_loc for city in group) and any(city in jd_loc for city in group):
            return 8.0

    return 0.0


def compute_education_score(candidate_education: List[Dict], jd_education_req: str) -> float:
    if jd_education_req is None:
        return 5.0

    candidate_degrees = {str(item.get("degree", "")).lower() for item in (candidate_education or [])}
    aliases = EDUCATION_KEYWORDS.get(jd_education_req.lower(), [])

    for alias in aliases + [jd_education_req]:
        if any(alias.lower() in degree for degree in candidate_degrees):
            return 5.0

    return 1.0


def score_candidate(candidate: Dict, jd: Dict, resume_text: str, jd_text: str) -> Dict:
    skill_result = compute_skill_score(
        candidate.get("skills", []),
        jd.get("required_skills", []),
        jd.get("preferred_skills", []),
    )
    exp_score = compute_experience_score(
        candidate.get("total_experience_years"),
        jd.get("required_experience_min"),
        jd.get("required_experience_max"),
    )
    semantic_score = compute_semantic_score(resume_text, jd_text)
    loc_score = compute_location_score(candidate.get("location"), jd.get("location"))
    edu_score = compute_education_score(candidate.get("education", []), jd.get("education_requirement"))

    total = skill_result["score"] + exp_score + semantic_score + loc_score + edu_score
    total = min(100.0, round(total, 1))

    if total >= RECOMMENDATION_THRESHOLDS["call_first"]:
        recommendation = "🟢 Call First"
    elif total >= RECOMMENDATION_THRESHOLDS["backup"]:
        recommendation = "🟡 Backup"
    else:
        recommendation = "🔴 Not Suitable"

    return {
        "skill_score": skill_result["score"],
        "experience_score": round(exp_score, 2),
        "semantic_score": round(semantic_score, 2),
        "location_score": round(loc_score, 2),
        "education_score": round(edu_score, 2),
        "matched_required": skill_result["matched_required"],
        "matched_preferred": skill_result["matched_preferred"],
        "missing_skills": skill_result["missing_skills"],
        "total_score": total,
        "recommendation": recommendation,
    }


def rank_candidates(candidates: List[Dict]) -> List[Dict]:
    sorted_candidates = sorted(candidates, key=lambda c: c.get("total_score", 0), reverse=True)
    for idx, candidate in enumerate(sorted_candidates, start=1):
        candidate["rank"] = idx
    return sorted_candidates