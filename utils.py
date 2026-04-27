from __future__ import annotations

import re
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def clean_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_location(loc: str) -> str:
    if not loc:
        return ""
    normalized = loc.strip().lower()
    normalized = normalized.replace("bengaluru", "bangalore")
    normalized = normalized.replace("gurugram", "gurgaon")
    return normalized


def _normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("91") and len(digits) >= 12:
        digits = digits[-10:]
    elif len(digits) > 10:
        digits = digits[-10:]
    return digits


def format_ctc(ctc_str) -> str:
    if ctc_str is None or str(ctc_str).strip() == "":
        return "Not mentioned"

    value = str(ctc_str).strip().lower().replace(",", "")

    num_match = re.search(r"(\d+(?:\.\d+)?)", value)
    if not num_match:
        return "Not mentioned"

    num = float(num_match.group(1))

    if "lpa" in value or "lakh" in value or re.search(r"\bl\b", value):
        return f"{num:g} LPA"
    if num > 10000:
        return f"{round(num / 100000, 2):g} LPA"
    if 1 <= num <= 50:
        return f"{num:g} LPA"
    return f"{num:g} LPA"


def detect_duplicates(candidates: List[Dict]) -> List[Dict]:
    seen_emails = set()
    seen_phones = set()

    for candidate in candidates:
        candidate["is_duplicate"] = False

    for idx, candidate in enumerate(candidates):
        email = (candidate.get("email") or "").strip().lower()
        phone = _normalize_phone(candidate.get("phone") or "")

        if email and email in seen_emails:
            candidate["is_duplicate"] = True
            continue
        if phone and phone in seen_phones:
            candidate["is_duplicate"] = True
            continue

        if email:
            seen_emails.add(email)
        if phone:
            seen_phones.add(phone)

        current_text = clean_text(candidate.get("resume_text") or "")
        if not current_text:
            continue

        previous_texts = [clean_text(candidates[j].get("resume_text") or "") for j in range(idx) if not candidates[j].get("is_duplicate")]
        if not previous_texts:
            continue

        corpus = previous_texts + [current_text]
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(matrix[-1], matrix[:-1])[0]
            if sims.size and float(max(sims)) > 0.85:
                candidate["is_duplicate"] = True
        except ValueError:
            pass

    return candidates
