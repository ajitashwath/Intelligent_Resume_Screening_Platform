# extractor.py
"""
Skill extraction module for the Intelligent Resume Screening Platform.

Extracts skills from resume text by matching against the curated keyword
dictionary in shared_data.py.  Uses word-boundary regex to reduce false
positives and returns properly-cased display names.
"""

import re
from typing import Dict, List, Set

from shared_data import SKILL_KEYWORDS


# ---------------------------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Lowercase and collapse all whitespace into single spaces."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Skill extraction
# ---------------------------------------------------------------------------

def extract_skills(text: str) -> List[str]:
    """Return a sorted list of **display-name** skills found in *text*.

    Uses word-boundary matching (`\\b`) so partial matches inside longer
    words are ignored (e.g. "express" won't match "expression").

    Returns
    -------
    list[str]
        Sorted list of properly-cased skill names (e.g. "AWS", "Node.js").
    """
    if not text:
        return []

    cleaned = clean_text(text)
    detected_skills: Set[str] = set()

    for category_skills in SKILL_KEYWORDS.values():
        for match_key, display_name in category_skills.items():
            # match_key is already lowercase (enforced by shared_data.py)
            pattern = r"\b" + re.escape(match_key) + r"\b"
            if re.search(pattern, cleaned):
                detected_skills.add(display_name)

    return sorted(detected_skills)


def extract_skills_by_category(text: str) -> Dict[str, List[str]]:
    """Return detected skills grouped by their category.

    Useful for rendering categorised skill sections in the UI.

    Returns
    -------
    dict[str, list[str]]
        Mapping of category name → sorted list of display-name skills.
        Categories with zero matches are omitted.
    """
    if not text:
        return {}

    cleaned = clean_text(text)
    result: Dict[str, List[str]] = {}

    for category, category_skills in SKILL_KEYWORDS.items():
        matched: List[str] = []
        for match_key, display_name in category_skills.items():
            pattern = r"\b" + re.escape(match_key) + r"\b"
            if re.search(pattern, cleaned):
                matched.append(display_name)
        if matched:
            result[category] = sorted(matched)

    return result


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from parser import extract_text_from_pdf

    sample_text = extract_text_from_pdf("resumes/sample1.pdf")
    print("=== Flat skill list ===")
    skills = extract_skills(sample_text)
    for skill in skills:
        print(f"  • {skill}")

    print("\n=== Skills by category ===")
    by_cat = extract_skills_by_category(sample_text)
    for cat, cat_skills in by_cat.items():
        print(f"\n  [{cat}]")
        for s in cat_skills:
            print(f"    • {s}")