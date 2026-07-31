from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional

from extractor import extract_skills

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_SEMANTIC_WEIGHT = 0.6
DEFAULT_SKILL_WEIGHT = 0.4

class MatcherError(Exception):
    """Base exception for matcher-related failures."""

class InvalidInputError(MatcherError):
    """Raised when resume text or job description is missing/invalid."""

class ModelLoadError(MatcherError):
    """Raised when the sentence-transformer model fails to load."""

@dataclass
class MatchResult:
    match_score: float                 
    semantic_score: float               
    skill_overlap_score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict:
        return {
            "match_score": self.match_score,
            "semantic_score": self.semantic_score,
            "skill_overlap_score": self.skill_overlap_score,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
        }

@lru_cache(maxsize = None)
def load_model(model_name: str = DEFAULT_MODEL_NAME):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ModelLoadError(
            "sentence-transformers is not installed. "
            "Run `pip install sentence-transformers`."
        ) from exc

    try:
        logger.info("Loading sentence-transformer model '%s'...", model_name)
        return SentenceTransformer(model_name)
    except Exception as exc:
        raise ModelLoadError(
            f"Failed to load sentence-transformer model '{model_name}': {exc}"
        ) from exc

@lru_cache(maxsize = 32)
def embed_text_cached(model_name: str, text: str):
    model = load_model(model_name)
    return model.encode(text, convert_to_numpy=True)


def embed_texts(model_name: str, jd_text: str, resume_text: str):
    model = load_model(model_name)
    jd_embedding = embed_text_cached(model_name, jd_text)
    resume_embedding = model.encode(resume_text, convert_to_numpy=True)
    return jd_embedding, resume_embedding

def validate_text(value: Optional[str], field_name: str) -> str:
    if value is None or not isinstance(value, str) or not value.strip():
        raise InvalidInputError(f"{field_name} must be a non-empty string.")
    return value.strip()

def clamp_percentage(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)

def compute_semantic_score(resume_text: str, job_description: str, model_name: str = DEFAULT_MODEL_NAME) -> float:
    resume_text = validate_text(resume_text, "resume_text")
    job_description = validate_text(job_description, "job_description")
    try:
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError as exc:
        raise ModelLoadError(
            "scikit-learn is not installed. Run `pip install scikit-learn`."
        ) from exc

    jd_embedding, resume_embedding = embed_texts(
        model_name, job_description, resume_text
    )

    similarity = cosine_similarity([jd_embedding], [resume_embedding])[0][0]
    return clamp_percentage(float(similarity) * 100)

def compute_skill_overlap(resume_text: str, job_description: str) -> Dict[str, object]:
    resume_text = validate_text(resume_text, "resume_text")
    job_description = validate_text(job_description, "job_description")

    jd_skills = set(extract_skills(job_description))
    resume_skills = set(extract_skills(resume_text))

    if not jd_skills:
        return {
            "score": 0.0,
            "matched": [],
            "missing": [],
            "undefined": True,
        }

    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)
    overlap_score = clamp_percentage(100 * len(matched) / len(jd_skills))
    return {
        "score": overlap_score,
        "matched": matched,
        "missing": missing,
        "undefined": False,
    }


def compute_match_score(resume_text: str, job_description: str, *, model_name: str = DEFAULT_MODEL_NAME, semantic_weight: float = DEFAULT_SEMANTIC_WEIGHT, skill_weight: float = DEFAULT_SKILL_WEIGHT) -> MatchResult:
    if abs((semantic_weight + skill_weight) - 1.0) > 1e-6:
        raise InvalidInputError("semantic_weight + skill_weight must equal 1.0")

    resume_text = validate_text(resume_text, "resume_text")
    job_description = validate_text(job_description, "job_description")

    semantic_score = compute_semantic_score(resume_text, job_description, model_name)
    overlap = compute_skill_overlap(resume_text, job_description)

    if overlap["undefined"]:
        blended = semantic_score
    else:
        blended = (semantic_weight * semantic_score) + (skill_weight * overlap["score"])

    return MatchResult(
        match_score=clamp_percentage(blended),
        semantic_score=semantic_score,
        skill_overlap_score=overlap["score"],
        matched_skills=overlap["matched"],
        missing_skills=overlap["missing"],
    )


def rank_candidates(candidates: List[Dict], *, score_key: str = "match_score") -> List[Dict]:
    def _safe_score(candidate: Dict) -> float:
        value = candidate.get(score_key)
        if isinstance(value, (int, float)):
            return float(value)
        logger.warning(
            "Candidate missing/invalid '%s' (%r); treating as 0.",
            score_key, candidate.get("name", candidate),
        )
        return 0.0
    return sorted(candidates, key=_safe_score, reverse=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    from parser import extract_text_from_pdf

    SAMPLE_JOB_DESCRIPTION = """
    We are looking for a Software Engineer with experience in Python,
    Java, SQL, REST APIs, Git, Linux, Docker, AWS and problem solving.
    Experience with Machine Learning is a plus.
    """

    try:
        resume = extract_text_from_pdf("resumes/sample1.pdf")
        result = compute_match_score(resume, SAMPLE_JOB_DESCRIPTION)

        print(f"Blended Match Score : {result.match_score}%")
        print(f"Semantic Score    : {result.semantic_score}%")
        print(f"Skill Overlap     : {result.skill_overlap_score}%")
        print(f"Matched Skills    : {', '.join(result.matched_skills) or 'none'}")
        print(f"Missing Skills    : {', '.join(result.missing_skills) or 'none'}")
    except MatcherError as exc:
        print(f"Matcher error: {exc}")
    except FileNotFoundError:
        print("Sample resume not found — place a PDF at resumes/sample1.pdf to test.")