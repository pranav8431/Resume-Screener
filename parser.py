from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config import EDUCATION_KEYWORDS, INDIAN_CITIES
from skill_data import extract_skills_from_text

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _first_or_none(matches: List[str]) -> Optional[str]:
    return matches[0] if matches else None


def _normalize_phone(phone: str) -> Optional[str]:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) >= 12:
        digits = digits[-10:]
    elif len(digits) > 10:
        digits = digits[-10:]

    if re.fullmatch(r"[6-9]\d{9}", digits):
        return digits
    return None


def _extract_name(text: str) -> Optional[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blacklist_terms = {
        "technology",
        "solution",
        "software",
        "system",
        "pvt",
        "ltd",
        "private",
        "limited",
        "intern",
        "fresher",
        "graduate",
        "college",
        "university",
        "institute",
        "computer",
        "information",
        "engineering",
        "science",
        "bachelor",
        "master",
        "b.tech",
        "m.tech",
        "skills",
        "profile",
        "objective",
        "summary",
        "contact",
        "address",
        "phone",
        "email",
        "february",
        "january",
        "march",
        "april",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    }

    for line in lines[:12]:
        words = line.split()

        if any(word.isupper() and len(word) > 3 for word in words):
            continue

        lower = line.lower()
        if re.search(r"\d|@", lower):
            continue
        if any(term in lower for term in blacklist_terms):
            continue

        if not (2 <= len(words) <= 4):
            continue

        if all(re.fullmatch(r"[A-Za-z][A-Za-z\-\.']*", w) for w in words):
            return " ".join(w.capitalize() for w in words)

    return None


def _extract_location(text: str) -> Optional[str]:
    lower = text.lower()

    remote_patterns = [
        r"(?:location|work\s+location|job\s+location)\s*[:\-]\s*remote",
        r"(?:fully\s+)?remote\s+(?:work|job|position|role|opportunity)",
        r"work\s+from\s+home",
        r"wfh",
        r"100%\s+remote",
    ]
    for pattern in remote_patterns:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            return "Remote"

    label_patterns = [
        r"(?:location|work\s+location|job\s+location|office\s+location|place\s+of\s+work)\s*[:\-]\s*([a-zA-Z][a-zA-Z\s,/]{2,50}?)(?:\n|\.|$|\|)",
        r"(?:based\s+(?:in|out\s+of|at)|located\s+in|office\s+in|posted\s+(?:in|at))\s*[:\-]?\s*([a-zA-Z][a-zA-Z\s]{2,40}?)(?:\n|\.|,|$)",
        r"(?:city|place)\s*[:\-]\s*([a-zA-Z][a-zA-Z\s]{2,30}?)(?:\n|\.|,|$)",
    ]

    for pattern in label_patterns:
        match = re.search(pattern, lower, flags=re.IGNORECASE)
        if match:
            candidate_text = match.group(1).strip().lower()
            candidate_text = re.sub(
                r"\b(?:india|maharashtra|karnataka|gujarat|rajasthan|punjab|"
                r"haryana|telangana|tamil\s*nadu|kerala|west\s*bengal|odisha|"
                r"bihar|jharkhand|assam|goa)\b",
                "",
                candidate_text,
                flags=re.IGNORECASE,
            ).strip(" ,")

            if "remote" in candidate_text:
                return "Remote"
            if not candidate_text:
                continue

            for city in INDIAN_CITIES:
                if re.search(rf"\b{re.escape(city)}\b", candidate_text, flags=re.IGNORECASE):
                    return city.title()

    for city in INDIAN_CITIES:
        if city == "remote":
            continue
        if re.search(rf"\b{re.escape(city)}\b", lower, flags=re.IGNORECASE):
            return city.title()

    if re.search(r"\bremote\b", lower, flags=re.IGNORECASE):
        return "Remote"

    return None


def _parse_month(token: str) -> int:
    return MONTHS.get(token.strip().lower(), 1)


def _month_index(month: int, year: int) -> int:
    return year * 12 + month


def _calculate_experience_from_dates(text: str) -> Optional[float]:
    """
    Calculate total work experience from date ranges in text.
    CRITICAL: Must exclude date ranges that appear in education sections.
    """
    now = datetime.now()

    work_section_match = re.search(
        r"(?:^|\n)\s*(?:experience|work\s+experience|employment|career\s+history|work\s+history)"
        r"\s*\n(.*?)(?=\n\s*(?:education|projects?|skills?|achievements?|certifications?)|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if work_section_match:
        work_text = work_section_match.group(1)
    else:
        work_text = text

    total_months = 0

    month_pattern = (
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)"
        r"\s+(20\d{2}|19\d{2})"
        r"\s*[\-–—to]{1,4}\s*"
        r"(present|current|"
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)?"
        r"\s*(20\d{2}|19\d{2})?"
    )

    for m in re.finditer(month_pattern, work_text, re.IGNORECASE):
        start_month = _parse_month(m.group(1))
        start_year = int(m.group(2))
        end_token = (m.group(3) or "").strip().lower()
        end_year_token = m.group(4)

        if end_token in {"present", "current"}:
            end_month, end_year = now.month, now.year
        elif end_year_token:
            end_month = _parse_month(end_token) if end_token else 1
            end_year = int(end_year_token)
        else:
            continue

        duration_months = max(
            0,
            _month_index(end_month, end_year) - _month_index(start_month, start_year),
        )

        range_start_idx = m.start()
        preceding_text = work_text[max(0, range_start_idx - 200):range_start_idx].lower()

        edu_indicators = [
            "b.tech",
            "btech",
            "b tech",
            "m.tech",
            "mtech",
            "bachelor",
            "master",
            "degree",
            "university",
            "college",
            "institute",
            "school",
            "mba",
            "bsc",
            "msc",
            "bca",
            "mca",
            "diploma",
            "graduation",
        ]

        if any(ind in preceding_text for ind in edu_indicators):
            continue

        total_months += duration_months

    if total_months == 0:
        year_ranges = re.findall(
            r"(20\d{2}|19\d{2})\s*[\-–to]{1,3}\s*(present|current|20\d{2}|19\d{2})",
            work_text,
            re.IGNORECASE,
        )
        for start_yr_str, end_yr_str in year_ranges:
            start_yr = int(start_yr_str)
            end_yr = now.year if end_yr_str.lower() in {"present", "current"} else int(end_yr_str)
            total_months += max(0, (end_yr - start_yr) * 12)

    if total_months <= 0:
        return None

    return min(round(total_months / 12.0, 1), 40.0)


def _extract_total_experience(text: str) -> Optional[float]:
    """Extract total work experience in years."""

    explicit_patterns = [
        r"(\d+\.?\d*)\s*\+?\s*years?\s+of\s+(?:total\s+)?(?:work\s+|professional\s+)?experience",
        r"(?:total\s+)?experience\s*[:\-]?\s*(\d+\.?\d*)\s*\+?\s*years?",
        r"(\d+\.?\d*)\s*years?\s+(?:of\s+)?(?:work|industry|total|professional)\s+experience",
        r"(\d+\.?\d*)\s*\+?\s*years?\s+experience\s+in",
    ]
    for pattern in explicit_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return float(m.group(1))

    return _calculate_experience_from_dates(text)


def _extract_current_company(text: str) -> Optional[str]:
    patterns = [
        r"(?:currently\s+working|present|current)\s+(?:at|in|with)?\s+([A-Z][^\n,]{2,40})",
        r"([A-Z][A-Za-z0-9&\-. ]{2,50})\s*\|\s*(?:present|current)",
        r"([A-Z][A-Za-z0-9&\-. ]{2,50})\s*[\-–]\s*(?:present|current)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            company = match.group(1).strip(" -|,")
            if 2 <= len(company) <= 50:
                return company

    current_year = datetime.now().year
    near_present = re.search(
        rf"([A-Z][A-Za-z0-9&\-. ]{{2,50}}).*?(?:present|current|{current_year})",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if near_present:
        return near_present.group(1).strip(" -|,")

    return None


def _normalize_notice_period(text: str) -> Optional[str]:
    lower = text.lower()

    immediate_patterns = [
        r"immediate\s+(?:joiner|joining|availability|join)",
        r"can\s+join\s+immediately",
        r"available\s+immediately",
        r"notice\s+period\s*[:\s]*nil",
        r"notice\s+period\s*[:\s]*none",
        r"no\s+notice\s+period",
        r"ready\s+to\s+join\s+immediately",
        r"join\s+within\s+(?:a\s+)?(?:week|few\s+days)",
    ]
    for pattern in immediate_patterns:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            return "Immediate"

    if re.search(r"(?:serving|currently\s+serving)\s+notice", lower, flags=re.IGNORECASE):
        days_match = re.search(r"(\d+)\s*days?\s+(?:left|remaining|more)", lower, flags=re.IGNORECASE)
        if days_match:
            days = int(days_match.group(1))
            if days <= 15:
                return "15 days"
            return "30 days"
        return "30 days"

    patterns = [
        r"notice\s+period\s*[:\-]?\s*(\d+)\s*(days?|months?|weeks?)",
        r"(\d+)\s*(days?|months?|weeks?)\s+notice(?:\s+period)?",
        r"notice\s*[:\-]\s*(\d+)\s*(days?|months?|weeks?)",
        r"np\s*[:\-]\s*(\d+)\s*(days?|months?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lower, flags=re.IGNORECASE)
        if match:
            value = int(match.group(1))
            unit = match.group(2).lower() if match.group(2) else "days"

            if "month" in unit:
                value = value * 30
            elif "week" in unit:
                value = value * 7

            if value <= 7:
                return "Immediate"
            if value <= 15:
                return "15 days"
            if value <= 30:
                return "30 days"
            if value <= 45:
                return "45 days"
            if value <= 60:
                return "60 days"
            return "90 days"

    return None


def _extract_ctc(text: str, expected: bool = False) -> Optional[str]:
    if expected:
        patterns = [
            r"(?:expected\s+ctc|ectc|expected\s+salary|salary\s+expectation)[:\s]+(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)\s*(?:lpa|l|lac|lakh)?",
        ]
    else:
        patterns = [
            r"(?:current\s+ctc|cctc|current\s+salary)[:\s]+(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)\s*(?:lpa|l|lac|lakh|lakhs)?",
            r"(?:ctc|salary|package)[:\s]+(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)\s*(?:lpa|l)",
            r"(?:current\s+ctc|ctc|salary|package)[:\s]+(?:rs\.?|inr|₹)?\s*([\d,]+)",
        ]

    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered, flags=re.IGNORECASE)
        if not match:
            continue

        raw = match.group(1).replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            continue

        snippet = lowered[max(0, match.start() - 20): match.end() + 20]
        if "lpa" in snippet or "lakh" in snippet or re.search(r"\d\s*l\b", snippet, flags=re.IGNORECASE):
            return f"{value:g} LPA"
        if value > 10000:
            return f"{round(value / 100000, 2):g} LPA"
        return f"{value:g} LPA"

    return None


def _extract_education(text: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for idx, line in enumerate(lines):
        lower = line.lower()
        for degree_key, aliases in EDUCATION_KEYWORDS.items():
            filtered_aliases = [alias for alias in aliases if len(alias.replace(".", "").strip()) >= 3]
            if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", lower, flags=re.IGNORECASE) for alias in filtered_aliases):
                institution = ""
                year = ""
                block = " ".join(lines[idx: idx + 3])

                inst_match = re.search(
                    r"(?:from|at|institute|university|college)\s*[:\-]?\s*([A-Za-z0-9&,.\- ]{3,80})",
                    block,
                    flags=re.IGNORECASE,
                )
                if inst_match:
                    institution = inst_match.group(1).strip(" ,.-")

                year_match = re.search(r"(19\d{2}|20\d{2})", block, flags=re.IGNORECASE)
                if year_match:
                    year = year_match.group(1)

                degree_display = degree_key.upper() if degree_key != "btech" else "B.Tech"
                if degree_key == "mtech":
                    degree_display = "M.Tech"

                entry = {
                    "degree": degree_display,
                    "institution": institution,
                    "year": year,
                }
                if entry not in results:
                    results.append(entry)

    return results


def _extract_previous_companies(text: str, current_company: Optional[str]) -> List[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    companies: List[str] = []

    patterns = [
        r"(?:at|with|in)\s+([A-Z][A-Za-z0-9&\-. ]{2,50})",
        r"([A-Z][A-Za-z0-9&\-. ]{2,50})\s*[\-–]\s*(?:20\d{2}|19\d{2})",
    ]

    for line in lines:
        if not re.search(r"(20\d{2}|19\d{2}|present|current)", line, flags=re.IGNORECASE):
            continue
        for pattern in patterns:
            for match in re.finditer(pattern, line):
                company = match.group(1).strip(" ,|-.")
                if len(company) < 2:
                    continue
                if current_company and company.lower() == current_company.lower():
                    continue
                if company not in companies:
                    companies.append(company)

    return companies


def _clean_title(title: str) -> str:
    """Fix casing for acronyms in job titles."""
    acronyms = {
        "ml",
        "ai",
        "nlp",
        "api",
        "sql",
        "aws",
        "gcp",
        "ui",
        "ux",
        "hr",
        "qa",
        "ios",
        "sde",
        "swe",
        "mle",
        "erp",
        "crm",
        "bi",
        "rag",
        "llm",
        "rpa",
        "etl",
        "iot",
        "ar",
        "vr",
        "cv",
    }
    words = title.strip().split()
    result = []
    for word in words:
        clean = word.strip(".,;:()'\"")
        if clean.lower() in acronyms:
            result.append(clean.upper())
        elif "/" in clean:
            parts = clean.split("/")
            result.append("/".join(p.upper() if p.lower() in acronyms else p.capitalize() for p in parts))
        else:
            result.append(clean.capitalize())
    return " ".join(result)


def _extract_job_title(jd_text: str) -> str:
    job_keywords = [
        "developer",
        "engineer",
        "analyst",
        "designer",
        "manager",
        "lead",
        "architect",
        "scientist",
        "consultant",
        "specialist",
        "executive",
        "officer",
        "intern",
        "trainee",
        "devops",
        "fullstack",
        "frontend",
        "backend",
        "qa",
        "tester",
        "sde",
        "swe",
        "mle",
        "mlops",
        "data",
        "research",
        "product",
        "project",
        "technical",
        "software",
        "associate",
        "generalist",
        "strategist",
    ]

    label_patterns = [
        r"(?:position|role|job\s+title|opening|vacancy|designation)\s*[:\-]\s*([^\n\.]{3,80})",
        r"(?:we\s+are\s+)?(?:hiring|recruiting)\s+for\s+(?:the\s+role\s+of\s+)?([^\n\.]{3,80})",
    ]
    for pattern in label_patterns:
        m = re.search(pattern, jd_text, re.IGNORECASE)
        if m:
            t = m.group(1).strip().rstrip(".,;:")
            if any(kw in t.lower() for kw in job_keywords) and len(t.split()) <= 8:
                return _clean_title(t)

    role_extract = [
        r"(?:we\s+are\s+)?(?:hiring|looking\s+for|seeking|recruiting)\s+"
        r"(?:an?\s+|experienced\s+|talented\s+|skilled\s+)?"
        r"([A-Za-z][A-Za-z0-9/\-\s]{2,60}?)"
        r"(?=\s+(?:to\s+join|who|with|having|for\s+our|\.|,|\n|$))",
        r"invite\s+applications?\s+for\s+(?:the\s+)?(?:role|position)?\s*(?:of\s+)?"
        r"([A-Za-z][A-Za-z0-9/\-\s]{2,60}?)(?=\.|,|\n|$)",
    ]
    for pattern in role_extract:
        m = re.search(pattern, jd_text, re.IGNORECASE)
        if m:
            t = m.group(1).strip().rstrip(".,;:")
            if any(kw in t.lower() for kw in job_keywords):
                return _clean_title(" ".join(t.split()[:6]))

    as_role = re.search(
        r"(?:^|\.\s+|\n)As\s+(?:an?\s+)?"
        r"([A-Za-z][A-Za-z0-9/\-\s]{2,50}?)"
        r"(?=\s*,|\s+you|\s+the\s+candidate|\s+at|\.|$)",
        jd_text,
        re.IGNORECASE | re.MULTILINE,
    )
    if as_role:
        t = as_role.group(1).strip()
        if any(kw in t.lower() for kw in job_keywords) and len(t.split()) <= 5:
            return _clean_title(t)

    lines = [l.strip() for l in jd_text.splitlines() if l.strip()]
    sentence_words = {
        "is",
        "are",
        "has",
        "have",
        "will",
        "was",
        "were",
        "our",
        "we",
        "the",
        "this",
        "that",
        "building",
        "looking",
        "seeking",
        "dedicated",
    }

    for line in lines[:20]:
        words = line.split()
        if 2 <= len(words) <= 7:
            if any(kw in line.lower() for kw in job_keywords):
                word_set = {w.lower().strip("•-:") for w in words}
                if not (word_set & sentence_words):
                    return _clean_title(line)

    role_desc = re.search(
        r"(?:you(?:'ll|\s+will)\s+work\s+as\s+(?:an?\s+)?)([A-Za-z][A-Za-z0-9/\-\s]{2,50}?)(?=\s*[,.])",
        jd_text,
        re.IGNORECASE,
    )
    if role_desc:
        t = role_desc.group(1).strip()
        if any(kw in t.lower() for kw in job_keywords):
            return _clean_title(t)

    intern_match = re.search(
        r"([A-Za-z/\-]{2,30})\s+(?:engineer|developer|scientist|analyst)?\s*intern(?:ship)?",
        jd_text,
        re.IGNORECASE,
    )
    if intern_match:
        matched = intern_match.group(0).strip()
        return _clean_title(matched)

    return "Unknown Role"


def _extract_required_experience(jd_text: str) -> Tuple[Optional[float], Optional[float]]:
    lower = jd_text.lower()

    zero_exp_signals = [
        r"\b(?:intern|internship|interns)\b",
        r"\b(?:fresher|freshers|fresh\s+graduate[s]?)\b",
        r"\bentry[\s\-]?level\b",
        r"\b0\s*[\-–]\s*1\s*years?\b",
        r"\bno\s+(?:prior\s+)?experience\s+(?:required|needed)\b",
        r"\bopen\s+to\s+freshers\b",
        r"\b(?:trainee|apprentice)\b",
    ]
    for pattern in zero_exp_signals:
        if re.search(pattern, lower):
            return 0.0, 1.0

    fresher_range = re.search(r"\b0\s*[-–]\s*(\d)\s*years?\b", lower)
    if fresher_range:
        return 0.0, float(fresher_range.group(1))

    range_patterns = [
        r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
        r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s+(?:of\s+)?exp",
        r"between\s+(\d+)\s+and\s+(\d+)\s+years?",
        r"exp(?:erience)?\s*[:\-]?\s*(\d+)\s*[-–]\s*(\d+)\s*(?:years?|yrs?)",
    ]
    for pattern in range_patterns:
        m = re.search(pattern, lower)
        if m:
            return float(m.group(1)), float(m.group(2))

    min_patterns = [
        r"(?:minimum|min|at\s+least|atleast)\s+(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)",
        r"(?:experience|exp)\s*[:\-]?\s*(\d+)\s*\+\s*(?:years?|yrs?)",
        r"(\d+)\s*\+\s*(?:years?|yrs?)",
    ]
    for pattern in min_patterns:
        m = re.search(pattern, lower)
        if m:
            val = float(m.group(1))
            return val, val + 3.0

    general_patterns = [
        r"(\d+(?:\.\d+)?)\s+(?:years?|yrs?)\s+of\s+(?:relevant\s+)?(?:work\s+)?experience",
        r"experience\s+of\s+(?:at\s+least\s+)?(\d+(?:\.\d+)?)\s+(?:years?|yrs?)",
        r"(\d+(?:\.\d+)?)\s+(?:years?|yrs?)\s+(?:work\s+)?experience",
        r"(?:experience|exp)\s*[:\-]\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
    ]
    for pattern in general_patterns:
        m = re.search(pattern, lower)
        if m:
            val = float(m.group(1))
            return val, val + 2.0

    return None, None


def _extract_jd_location(jd_text: str) -> Optional[str]:
    return _extract_location(jd_text)


def _extract_jd_education_requirement(jd_text: str) -> Optional[str]:
    lower = jd_text.lower()
    for degree, aliases in EDUCATION_KEYWORDS.items():
        filtered_aliases = [alias for alias in aliases if len(alias.replace(".", "").strip()) >= 3]
        if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", lower, flags=re.IGNORECASE) for alias in filtered_aliases):
            return degree
    return None


def _extract_notice_preference(jd_text: str) -> Optional[str]:
    lower = jd_text.lower()
    if "immediate joiner" in lower or "immediate" in lower:
        return "Immediate"
    match = re.search(r"notice\s+period\s*[:\-]?\s*(\d+)\s*days?", lower, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1)} days"
    return None


def _extract_preferred_skills(jd_text: str) -> List[str]:
    sections = []
    patterns = [
        r"preferred\s*:\s*(.*)",
        r"good\s+to\s+have\s*:\s*(.*)",
        r"plus\s*:\s*(.*)",
        r"nice\s+to\s+have\s*:\s*(.*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, jd_text, flags=re.IGNORECASE)
        if match:
            sections.append(match.group(1))

    section_text = "\n".join(sections)
    return extract_skills_from_text(section_text)


def extract_resume_fields(text: str) -> Dict:
    email_matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    phone_matches = re.findall(r"(?:\+91[\-\s]?)?[6-9]\d{9}", text)

    phone = None
    for match in phone_matches:
        normalized = _normalize_phone(match)
        if normalized:
            phone = normalized
            break

    current_company = _extract_current_company(text)

    return {
        "name": _extract_name(text),
        "email": _first_or_none(email_matches),
        "phone": phone,
        "location": _extract_location(text),
        "total_experience_years": _extract_total_experience(text),
        "skills": extract_skills_from_text(text),
        "current_company": current_company,
        "notice_period": _normalize_notice_period(text),
        "current_ctc": _extract_ctc(text, expected=False),
        "expected_ctc": _extract_ctc(text, expected=True),
        "education": _extract_education(text),
        "previous_companies": _extract_previous_companies(text, current_company),
    }


def extract_jd_fields(jd_text: str) -> Dict:
    min_exp, max_exp = _extract_required_experience(jd_text)

    preferred_section = ""
    preferred_start = -1
    split_patterns = [
        r"(?:preferred|good\s+to\s+have|nice\s+to\s+have|plus\s*:|bonus)",
    ]

    for pattern in split_patterns:
        match = re.search(pattern, jd_text, flags=re.IGNORECASE)
        if match:
            preferred_start = match.start()
            preferred_section = jd_text[preferred_start:]
            break

    if preferred_start > 0:
        required_text = jd_text[:preferred_start]
    else:
        required_text = jd_text

    required_skills = extract_skills_from_text(required_text)
    preferred_skills = extract_skills_from_text(preferred_section)

    preferred_set = set(preferred_skills)
    required_skills = [skill for skill in required_skills if skill not in preferred_set]

    return {
        "job_title": _extract_job_title(jd_text),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "required_experience_min": min_exp,
        "required_experience_max": max_exp,
        "location": _extract_jd_location(jd_text),
        "education_requirement": _extract_jd_education_requirement(jd_text),
        "notice_period_preference": _extract_notice_preference(jd_text),
    }