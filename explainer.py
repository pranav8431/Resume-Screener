from __future__ import annotations
from typing import Dict, Optional


def generate_rule_based_explanation(candidate: dict, jd: dict, scores: dict) -> str:
    parts = []
    name = candidate.get("name") or "This candidate"
    matched = scores.get("matched_required") or []
    missing = scores.get("missing_skills") or []
    total_required = len(jd.get("required_skills") or [])
    total_score = scores.get("total_score", 0)
    job_title = jd.get("job_title", "this role")

    # Skills sentence
    if total_required > 0:
        parts.append(
            f"{name} matched {len(matched)} of {total_required} required skills"
            f"{' (' + ', '.join(matched[:4]) + ')' if matched else ''}."
        )
    else:
        parts.append(f"{name} has skills in: {', '.join(matched[:4]) if matched else 'none detected'}.")

    # Experience sentence
    exp = candidate.get("total_experience_years")
    min_exp = jd.get("required_experience_min")
    max_exp = jd.get("required_experience_max")
    exp_score = scores.get("experience_score", 0)

    if exp is not None and min_exp is not None:
        if exp_score >= 23:
            parts.append(
                f"Their {exp} years of experience fits the "
                f"{min_exp}-{max_exp} year requirement well."
            )
        elif exp_score >= 15:
            parts.append(
                f"Their {exp} years of experience is close to the "
                f"{min_exp}-{max_exp} year requirement."
            )
        else:
            parts.append(
                f"Their {exp} years of experience does not fully meet "
                f"the {min_exp}+ year requirement."
            )
    elif exp is None:
        parts.append("Experience details could not be extracted from the resume.")

    # Location sentence
    loc_score = scores.get("location_score", 0)
    candidate_loc = candidate.get("location")
    jd_loc = jd.get("location")
    if loc_score >= 8:
        parts.append(f"Location ({candidate_loc or 'N/A'}) matches the job location ({jd_loc or 'N/A'}).")
    elif jd_loc:
        parts.append(f"Location may not match - the job is in {jd_loc}.")

    # Missing skills sentence
    if missing:
        parts.append(f"Key missing skills: {', '.join(list(missing)[:3])}.")
    else:
        parts.append("No critical skill gaps detected.")

    return " ".join(parts)


def generate_openai_explanation(
    candidate: dict, jd: dict, scores: dict, api_key: str
) -> str:
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)

        prompt = (
            f"Candidate: {candidate.get('name')}\n"
            f"Role: {jd.get('job_title')}\n"
            f"Score: {scores.get('total_score')}/100\n"
            f"Matched skills: {', '.join(scores.get('matched_required', []))}\n"
            f"Missing skills: {', '.join(scores.get('missing_skills', []))}\n"
            f"Experience: {candidate.get('total_experience_years')} years "
            f"(required: {jd.get('required_experience_min')}-{jd.get('required_experience_max')})\n"
            f"Location: {candidate.get('location')} (job: {jd.get('location')})\n\n"
            "Write a 3-sentence recruiter explanation. Be factual and direct."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional recruitment assistant for Indian hiring teams."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return generate_rule_based_explanation(candidate, jd, scores)


def generate_whatsapp_message(
    candidate: dict, jd: dict, api_key: Optional[str] = None
) -> str:
    name = candidate.get("name") or "there"
    job_title = jd.get("job_title") or "this role"
    location = jd.get("location") or "our office"

    # Get top 3 matched skills for personalization
    matched = candidate.get("matched_required") or []
    if not matched:
        matched = candidate.get("skills", [])
    skills_str = ", ".join(matched[:3]) if matched else "your technical skills"

    if api_key:
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            prompt = (
                f"Write a WhatsApp message from a recruiter to {name} for the {job_title} "
                f"role in {location}. Mention their skills: {skills_str}. "
                f"Keep it under 80 words, warm, professional, end with asking for availability."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    # Rule-based template fallback
    return (
        f"Hi {name}, I came across your profile and feel you'd be a great fit "
        f"for the *{job_title}* role in {location}. Your experience with "
        f"{skills_str} matches what we're looking for. "
        f"Would you be available for a quick call this week? 😊"
    )
