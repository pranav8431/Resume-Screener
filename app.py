from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

from database import init_db, save_candidate, save_session
from explainer import generate_rule_based_explanation, generate_whatsapp_message
from exporter import export_to_excel
from extractor import extract_text
from parser import extract_jd_fields, extract_resume_fields
from utils import detect_duplicates, format_ctc

st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def load_matcher_module():
    with st.spinner("Loading NLP model..."):
        import matcher

    return matcher


MATCHER = load_matcher_module()


def initialize_state() -> None:
    defaults = {
        "jd_text": "",
        "jd_data": {},
        "raw_jd_extracted": None,
        "jd_confirmed": False,
        "candidates": [],
        "session_id": None,
        "processing_complete": False,
        "messages": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _render_tags(items: List[str], empty_text: str = "None") -> None:
    if not items:
        st.write(empty_text)
        return
    st.write(" | ".join(f"`{item}`" for item in items))


def _parse_notice_days(value: str) -> int:
    if not value:
        return 999
    lower = value.lower()
    if "immediate" in lower:
        return 0
    digits = "".join(ch for ch in lower if ch.isdigit())
    return int(digits) if digits else 999


def _build_table_dataframe(candidates: List[Dict]) -> pd.DataFrame:
    rows = []
    for c in candidates:
        matched_required = c.get("matched_required", [])
        missing_skills = c.get("missing_skills", [])
        exp_value = c.get("total_experience_years")
        exp_display = "-"
        if isinstance(exp_value, (int, float)):
            exp_display = f"{exp_value:.1f} yrs"
        rows.append(
            {
                "Rank": c.get("rank"),
                "Name": c.get("name") or "Unknown",
                "Score": c.get("total_score", 0),
                "Recommendation": c.get("recommendation", "🔴 Not Suitable"),
                "Matched Skills": ", ".join(matched_required) if matched_required else "-",
                "Missing Skills": ", ".join(missing_skills) if missing_skills else "-",
                "Experience": exp_display,
                "Notice Period": c.get("notice_period"),
                "Location": c.get("location"),
                "Duplicate": "🔁" if c.get("is_duplicate") else "",
            }
        )
    return pd.DataFrame(rows)


def _style_rows(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    def color_row(row):
        rec = row["Recommendation"]
        if "Call First" in rec:
            return ["background-color: #e2f0d9; color: #111111; font-weight: 600"] * len(row)
        if "Backup" in rec:
            return ["background-color: #fff2cc; color: #111111; font-weight: 600"] * len(row)
        return ["background-color: #f8d7da; color: #111111; font-weight: 600"] * len(row)

    return (
        df.style.apply(color_row, axis=1)
        .set_properties(**{"font-size": "14px", "white-space": "normal"})
    )


def _candidate_label(candidate: Dict) -> str:
    name = candidate.get("name") or "Unknown"
    score = candidate.get("total_score", 0)
    return f"{name} ({score}/100)"


def _conf_icon(level: str) -> str:
    return {"HIGH": "✅", "LOW": "⚠️", "NONE": "❌"}.get(level, "❓")


def _get_title_confidence(title: str) -> str:
    if not title or title == "Unknown Role":
        return "NONE"
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
        "intern",
        "trainee",
        "devops",
        "frontend",
        "backend",
        "qa",
        "tester",
        "sde",
        "associate",
        "executive",
        "officer",
    ]
    sentence_words = {
        "is",
        "are",
        "has",
        "have",
        "will",
        "was",
        "were",
        "building",
        "looking",
        "we",
        "our",
        "the",
    }
    words = title.lower().split()
    if len(words) > 6:
        return "LOW"
    if set(words) & sentence_words:
        return "LOW"
    if any(kw in title.lower() for kw in job_keywords):
        return "HIGH"
    return "LOW"


def render_jd_validation_panel(extracted_jd: dict) -> Optional[dict]:
    """
    Shows the validation panel and returns the CONFIRMED jd_data dict.
    The returned dict is what gets used for scoring — not the raw extraction.
    """
    st.markdown("### 📋 JD Review & Confirmation")
    st.info(
        "Review what was extracted from your JD. "
        "Fix any incorrect or missing fields — highlighted in red. "
        "All fields marked ❌ must be filled before you can analyze resumes."
    )

    left, right = st.columns([1, 1], gap="large")

    confirmed = {}
    has_errors = False

    with left:
        st.markdown("#### 📋 What We Extracted")

        title = extracted_jd.get("job_title", "")
        title_conf = _get_title_confidence(title)
        st.markdown(f"{_conf_icon(title_conf)} **Job Title**: `{title or 'Not found'}`")

        skills = extracted_jd.get("required_skills", [])
        skill_conf = "HIGH" if len(skills) >= 3 else ("LOW" if skills else "NONE")
        st.markdown(f"{_conf_icon(skill_conf)} **Required Skills** ({len(skills)} found):")
        if skills:
            st.markdown(" ".join([f"`{s}`" for s in skills]))
        else:
            st.markdown("_None extracted_")

        min_e = extracted_jd.get("required_experience_min")
        max_e = extracted_jd.get("required_experience_max")
        exp_conf = "HIGH" if (min_e is not None and max_e is not None) else ("LOW" if (min_e is not None or max_e is not None) else "NONE")
        exp_display = (
            f"{min_e}–{max_e} years"
            if (min_e is not None and max_e is not None)
            else ("Intern/Fresher" if min_e == 0.0 else "Not found")
        )
        st.markdown(f"{_conf_icon(exp_conf)} **Experience**: `{exp_display}`")

        location = extracted_jd.get("location")
        loc_conf = "HIGH" if location else "NONE"
        st.markdown(f"{_conf_icon(loc_conf)} **Location**: `{location or 'Not specified'}`")
        if not location:
            st.caption("ℹ️ No location in JD = candidates score 10/10 on location")

        pref = extracted_jd.get("preferred_skills", [])
        st.markdown(f"⚠️ **Preferred Skills** ({len(pref)} found):")
        if pref:
            st.markdown(" ".join([f"`{s}`" for s in pref]))
        else:
            st.markdown("_None extracted_")

    with right:
        st.markdown("#### ✏️ Confirm & Correct")

        title_conf = _get_title_confidence(extracted_jd.get("job_title", ""))
        title_label = "Job Title *" if title_conf == "NONE" else "Job Title"

        confirmed_title = st.text_input(
            title_label,
            value=extracted_jd.get("job_title", "") if title_conf != "NONE" else "",
            placeholder="e.g. Python Developer, ML Engineer Intern",
            key="conf_title",
            help="The exact job role you are hiring for",
        )
        if not confirmed_title.strip():
            st.error("⚠️ Job title is required")
            has_errors = True
        confirmed["job_title"] = confirmed_title.strip()

        skills_str = ", ".join(extracted_jd.get("required_skills", []))
        confirmed_skills_str = st.text_area(
            "Required Skills * (comma-separated)",
            value=skills_str,
            height=100,
            placeholder="e.g. Python, Django, PostgreSQL, AWS, Docker",
            key="conf_skills",
            help="Must-have skills for this role. Separate with commas.",
        )
        confirmed_skills = [s.strip().lower() for s in confirmed_skills_str.split(",") if s.strip()]
        if not confirmed_skills:
            st.error("⚠️ At least one required skill is needed")
            has_errors = True
        else:
            st.caption(f"✅ {len(confirmed_skills)} skills confirmed")
        confirmed["required_skills"] = confirmed_skills

        min_e = extracted_jd.get("required_experience_min")
        max_e = extracted_jd.get("required_experience_max")

        st.markdown("**Experience Required** *")
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            conf_min = st.number_input(
                "Min years",
                min_value=0.0,
                max_value=30.0,
                value=float(min_e) if min_e is not None else 0.0,
                step=0.5,
                key="conf_exp_min",
                help="0 for fresher/intern roles",
            )
        with exp_col2:
            conf_max = st.number_input(
                "Max years",
                min_value=0.0,
                max_value=30.0,
                value=float(max_e) if max_e is not None else 0.0,
                step=0.5,
                key="conf_exp_max",
            )

        if conf_min == 0.0 and conf_max == 0.0:
            st.caption("ℹ️ Both 0 = fresher/intern role. Correct if not.")
        elif conf_max < conf_min:
            st.error("⚠️ Max years must be ≥ min years")
            has_errors = True

        confirmed["required_experience_min"] = conf_min
        confirmed["required_experience_max"] = conf_max

        city_options = [
            "Not specified (Remote/Any)",
            "Remote",
            "Mumbai",
            "Delhi / NCR",
            "Bangalore",
            "Hyderabad",
            "Pune",
            "Chennai",
            "Kolkata",
            "Ahmedabad",
            "Jaipur",
            "Noida",
            "Gurgaon",
            "Chandigarh",
            "Nagpur",
            "Indore",
            "Bhopal",
            "Lucknow",
            "Kochi",
            "Coimbatore",
            "Vizag",
            "Surat",
            "Vadodara",
            "Patna",
            "Ranchi",
            "Mysore",
            "Other (type below)",
        ]

        extracted_loc = extracted_jd.get("location")
        default_idx = 0
        if extracted_loc:
            for i, opt in enumerate(city_options):
                if extracted_loc.lower() in opt.lower():
                    default_idx = i
                    break
            else:
                default_idx = len(city_options) - 1

        selected_loc = st.selectbox(
            "Job Location",
            options=city_options,
            index=default_idx,
            key="conf_location",
            help="Select 'Not specified' if location is irrelevant or fully remote",
        )

        if selected_loc == "Other (type below)":
            custom_loc = st.text_input("Enter city name", value=extracted_loc or "", key="conf_loc_custom")
            confirmed["location"] = custom_loc.strip() or None
        elif selected_loc == "Not specified (Remote/Any)":
            confirmed["location"] = None
        else:
            confirmed["location"] = selected_loc

        pref_str = ", ".join(extracted_jd.get("preferred_skills", []))
        confirmed_pref_str = st.text_area(
            "Preferred Skills (optional, comma-separated)",
            value=pref_str,
            height=80,
            placeholder="e.g. AWS, Kubernetes, GraphQL",
            key="conf_pref_skills",
            help="Good-to-have skills (not mandatory)",
        )
        confirmed["preferred_skills"] = [s.strip().lower() for s in confirmed_pref_str.split(",") if s.strip()]

        edu_req = extracted_jd.get("education_requirement")
        edu_options = ["Not specified", "btech", "mtech", "mba", "bsc", "msc", "bca", "mca", "phd", "diploma"]
        edu_default = edu_req if edu_req in edu_options else "Not specified"
        confirmed_edu = st.selectbox(
            "Education Requirement",
            options=edu_options,
            index=edu_options.index(edu_default),
            key="conf_edu",
            format_func=lambda x: {
                "Not specified": "Not specified",
                "btech": "B.Tech / B.E.",
                "mtech": "M.Tech / M.E.",
                "mba": "MBA / PGDM",
                "bsc": "B.Sc",
                "msc": "M.Sc",
                "bca": "BCA",
                "mca": "MCA",
                "phd": "PhD",
                "diploma": "Diploma",
            }.get(x, x),
        )
        confirmed["education_requirement"] = None if confirmed_edu == "Not specified" else confirmed_edu

        notice_options = ["No preference", "Immediate", "15 days", "30 days", "45 days", "60 days", "90 days"]
        extracted_notice = extracted_jd.get("notice_period_preference", "No preference")
        notice_default = extracted_notice if extracted_notice in notice_options else "No preference"
        confirmed["notice_period_preference"] = st.selectbox(
            "Notice Period Preference",
            options=notice_options,
            index=notice_options.index(notice_default),
            key="conf_notice",
        )

    st.divider()

    if has_errors:
        st.error("❌ Please fill all required fields marked with * before continuing.")
        st.button("✅ Confirm JD & Enable Resume Upload", disabled=True, use_container_width=True)
        return None

    with st.expander("📄 Preview — JD data that will be used for scoring", expanded=False):
        preview_col1, preview_col2 = st.columns(2)
        with preview_col1:
            st.markdown(f"**Role:** {confirmed.get('job_title')}")
            st.markdown(f"**Location:** {confirmed.get('location') or 'Any/Remote'}")
            st.markdown(
                f"**Experience:** {confirmed.get('required_experience_min')}–"
                f"{confirmed.get('required_experience_max')} years"
            )
            st.markdown(f"**Education:** {confirmed.get('education_requirement') or 'Any'}")
        with preview_col2:
            st.markdown(
                f"**Required Skills ({len(confirmed.get('required_skills', []))}):** "
                f"{', '.join(confirmed.get('required_skills', []) or ['None'])}"
            )
            st.markdown(
                f"**Preferred Skills ({len(confirmed.get('preferred_skills', []))}):** "
                f"{', '.join(confirmed.get('preferred_skills', []) or ['None'])}"
            )
            st.markdown(
                f"**Notice Preference:** {confirmed.get('notice_period_preference', 'No preference')}"
            )

    if st.button("✅ Confirm JD & Enable Resume Upload", type="primary", use_container_width=True):
        st.session_state["jd_data"] = confirmed
        st.session_state["jd_confirmed"] = True
        st.success("✅ JD confirmed! You can now upload and analyze resumes below.")
        return confirmed

    return None


def main() -> None:
    init_db()
    initialize_state()

    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload & Analyze",
        "📊 Rankings & Scores",
        "🔍 Candidate Details",
        "📥 Export",
    ])

    with tab1:
        st.subheader("Job Description")

        with st.expander("💡 Tips for best results — click to see", expanded=False):
            st.markdown(
                """
                **For most accurate extraction, your JD should clearly mention:**

                | Field | Good Example | Bad Example |
                |-------|-------------|-------------|
                | **Role** | `"We are hiring a Python Developer"` | `"Join our growing team"` |
                | **Skills** | `"Skills: Python, Django, AWS"` | Buried in paragraphs |
                | **Experience** | `"2-4 years experience"` | `"Senior professional"` |
                | **Location** | `"Location: Pune"` | Nothing mentioned |

                **Don't worry if your JD doesn't match this format exactly.**
                The app will extract what it can and you can manually correct
                any missing fields before analyzing resumes.

                **Common JD formats that work well:**
                - Naukri / LinkedIn job posts
                - WhatsApp recruiter messages
                - Internal HR documents
                - Any format — you can always fill in missing fields manually
                """
            )

        jd_text_input = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="e.g. We are hiring a Python Developer with 2-4 years...",
            value=st.session_state.get("jd_text_input", st.session_state.get("jd_text", "")),
            key="jd_text_input",
        )
        jd_file = st.file_uploader("Or upload JD file", type=["txt", "pdf"], key="jd_file_uploader")

        if jd_file is not None:
            jd_file_text = extract_text(jd_file.read(), jd_file.name)
            if jd_file_text:
                jd_text_input = jd_file_text
                st.session_state["jd_text_input"] = jd_file_text
                st.session_state["jd_text"] = jd_file_text

        if st.button("🔍 Extract JD Details"):
            jd_text = st.session_state.get("jd_text_input", "").strip()
            if not jd_text:
                st.warning("Please paste a job description first.")
            else:
                with st.spinner("Extracting JD details..."):
                    raw_extracted = extract_jd_fields(jd_text)
                    st.session_state["raw_jd_extracted"] = raw_extracted
                    st.session_state["jd_text"] = jd_text
                    st.session_state["jd_confirmed"] = False

        if st.session_state.get("raw_jd_extracted"):
            confirmed_jd = render_jd_validation_panel(st.session_state["raw_jd_extracted"])
            if confirmed_jd:
                st.session_state["jd_data"] = confirmed_jd
                st.session_state["jd_confirmed"] = True

        st.divider()
        st.markdown("### 📁 Resume Upload")

        if not st.session_state.get("jd_confirmed"):
            st.warning(
                "⬆️ Please extract and confirm the Job Description above before uploading resumes."
            )
            st.file_uploader(
                "Upload Resumes (confirm JD first)",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                disabled=True,
                key="resume_upload_disabled",
            )
            resume_files = []
            analyze_clicked = False
        else:
            jd_data = st.session_state["jd_data"]
            st.success(
                f"✅ JD confirmed for: **{jd_data.get('job_title')}** | "
                f"Skills: {len(jd_data.get('required_skills', []))} | "
                f"Exp: {jd_data.get('required_experience_min')}–"
                f"{jd_data.get('required_experience_max')} yrs"
            )

            resume_files = st.file_uploader(
                "Upload Resumes",
                type=["pdf", "docx", "txt"],
                accept_multiple_files=True,
                key="resume_upload_active",
            )

            if resume_files:
                st.info(f"📎 {len(resume_files)} resume(s) ready to analyze")

            analyze_clicked = st.button(
                "🚀 Analyze All Resumes",
                type="primary",
                use_container_width=True,
                disabled=not resume_files,
            )

        if analyze_clicked:
            jd_text = st.session_state.get("jd_text", "")
            jd_data = st.session_state.get("jd_data", {})
            session_id = st.session_state.get("session_id")
            if not session_id:
                session_id = save_session(jd_data.get("job_title", "Role"), jd_text)
                st.session_state["session_id"] = session_id

            progress = st.progress(0)
            status = st.empty()
            processed_candidates: List[Dict] = []
            uploaded_count = len(resume_files)

            for idx, uploaded_file in enumerate(resume_files, start=1):
                filename = uploaded_file.name
                resume_text = extract_text(uploaded_file.read(), filename)

                if not resume_text.strip():
                    st.warning(f"Could not read {filename}, skipping.")
                    progress.progress(int((idx / uploaded_count) * 100))
                    continue

                candidate = extract_resume_fields(resume_text)
                candidate["name"] = candidate.get("name") or filename.rsplit(".", 1)[0]

                scores = MATCHER.score_candidate(candidate, jd_data, resume_text, jd_text)
                candidate.update(scores)
                candidate["score_breakdown"] = {
                    "Skills": scores["skill_score"],
                    "Experience": scores["experience_score"],
                    "Semantic Match": scores["semantic_score"],
                    "Location": scores["location_score"],
                    "Education": scores["education_score"],
                }

                candidate["resume_text"] = resume_text
                candidate["resume_filename"] = filename
                candidate["explanation"] = generate_rule_based_explanation(candidate, jd_data, scores)
                candidate["is_duplicate"] = False

                processed_candidates.append(candidate)

                status.info(f"Processing {idx}/{uploaded_count}: {filename} ✅")
                progress.progress(int((idx / uploaded_count) * 100))

            processed_candidates = detect_duplicates(processed_candidates)
            processed_candidates = MATCHER.rank_candidates(processed_candidates)

            for c in processed_candidates:
                save_candidate(session_id, c)

            st.session_state["candidates"] = processed_candidates
            st.session_state["processing_complete"] = True

            dup_count = sum(1 for c in processed_candidates if c.get("is_duplicate"))
            st.success(
                f"✅ Analysis complete! {len(processed_candidates)} resumes processed, {dup_count} duplicates detected."
            )

    with tab2:
        candidates = st.session_state.get("candidates", [])

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("📋 Total Candidates", len(candidates))
        c2.metric("🟢 Call First", sum(1 for c in candidates if c.get("recommendation") == "🟢 Call First"))
        c3.metric("🟡 Backup", sum(1 for c in candidates if c.get("recommendation") == "🟡 Backup"))
        c4.metric("🔴 Not Suitable", sum(1 for c in candidates if c.get("recommendation") == "🔴 Not Suitable"))
        c5.metric("🔁 Duplicates", sum(1 for c in candidates if c.get("is_duplicate")))

        if not candidates:
            st.info("No candidates analyzed yet.")
        else:
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                rec_filter = st.multiselect(
                    "Recommendation",
                    ["🟢 Call First", "🟡 Backup", "🔴 Not Suitable"],
                    default=["🟢 Call First", "🟡 Backup", "🔴 Not Suitable"],
                )
            with f2:
                min_score = st.slider("Minimum Score", 0, 100, 0)
            with f3:
                hide_duplicates = st.checkbox("Hide duplicates", value=False)
            with f4:
                sort_by = st.selectbox("Sort by", ["Score", "Name", "Experience", "Notice Period"])

            filtered = [
                c
                for c in candidates
                if c.get("recommendation") in rec_filter and float(c.get("total_score", 0)) >= min_score
            ]
            if hide_duplicates:
                filtered = [c for c in filtered if not c.get("is_duplicate")]

            if sort_by == "Score":
                filtered.sort(key=lambda x: x.get("total_score", 0), reverse=True)
            elif sort_by == "Name":
                filtered.sort(key=lambda x: (x.get("name") or "").lower())
            elif sort_by == "Experience":
                filtered.sort(key=lambda x: x.get("total_experience_years") or 0, reverse=True)
            else:
                filtered.sort(key=lambda x: _parse_notice_days(x.get("notice_period")))

            for idx, candidate in enumerate(filtered, start=1):
                candidate["rank"] = idx

            table_df = _build_table_dataframe(filtered)

            st.dataframe(
                _style_rows(table_df),
                use_container_width=True,
                height=460,
                column_config={
                    "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100),
                    "Matched Skills": st.column_config.TextColumn("Matched Skills", width="large"),
                    "Missing Skills": st.column_config.TextColumn("Missing Skills", width="large"),
                },
                hide_index=True,
            )

    with tab3:
        candidates = st.session_state.get("candidates", [])
        if not candidates:
            st.info("No candidate data available yet.")
        else:
            labels = [_candidate_label(c) for c in candidates]
            selected_label = st.selectbox("Select Candidate", labels)
            selected_idx = labels.index(selected_label)
            selected = candidates[selected_idx]

            left, right = st.columns(2)

            with left:
                st.markdown(f"## {selected.get('name') or 'Unknown'}")
                st.write(f"**Email:** {selected.get('email') or 'N/A'}")
                st.write(f"**Phone:** {selected.get('phone') or 'N/A'}")
                st.write(f"**Location:** {selected.get('location') or 'N/A'}")
                st.write(f"**Current Company:** {selected.get('current_company') or 'N/A'}")
                st.write(f"**Notice Period:** {selected.get('notice_period') or 'N/A'}")
                st.write(f"**Current CTC:** {format_ctc(selected.get('current_ctc'))}")
                st.write(f"**Expected CTC:** {format_ctc(selected.get('expected_ctc'))}")

                education = selected.get("education") or []
                if education:
                    edu_lines = [
                        f"{e.get('degree', '')} | {e.get('institution', '')} | {e.get('year', '')}".strip(" |")
                        for e in education
                    ]
                    st.write("**Education:**")
                    for line in edu_lines:
                        st.write(f"- {line}")
                else:
                    st.write("**Education:** N/A")

            with right:
                score_df = pd.DataFrame(
                    {
                        "Category": ["Skills", "Experience", "Semantic Match", "Location", "Education"],
                        "Score": [
                            selected.get("skill_score", 0),
                            selected.get("experience_score", 0),
                            selected.get("semantic_score", 0),
                            selected.get("location_score", 0),
                            selected.get("education_score", 0),
                        ],
                    }
                )
                fig = px.bar(
                    score_df,
                    x="Score",
                    y="Category",
                    orientation="h",
                    text="Score",
                    title="Score Breakdown",
                    range_x=[0, 40],
                )
                fig.update_layout(height=320)
                st.plotly_chart(fig, use_container_width=True)

                st.write("**Matched Skills:**")
                _render_tags(selected.get("matched_required", []))
                st.write("**Missing Skills:**")
                _render_tags(selected.get("missing_skills", []), empty_text="None")

            with st.expander("📝 Candidate Explanation", expanded=True):
                st.write(selected.get("explanation") or "No explanation available.")

            st.subheader("WhatsApp Message")
            message_key = selected.get("resume_filename", selected.get("name", "candidate"))
            messages = st.session_state.setdefault("messages", {})
            if message_key not in messages:
                messages[message_key] = generate_whatsapp_message(
                    selected,
                    st.session_state.get("jd_data", {}),
                    api_key=None,
                )

            st.code(messages[message_key], language="text")
            st.caption("📋 Copy")
            if st.button("🔄 Regenerate"):
                messages[message_key] = generate_whatsapp_message(
                    selected,
                    st.session_state.get("jd_data", {}),
                    api_key=None,
                )
                st.rerun()

    with tab4:
        candidates = st.session_state.get("candidates", [])
        if not candidates:
            st.info("No data to export yet.")
        else:
            shortlist = [c for c in candidates if float(c.get("total_score", 0)) >= 60]
            st.write(f"{len(shortlist)} candidates shortlisted (score ≥ 60)")

            full_bytes = export_to_excel(candidates, st.session_state.get("jd_data", {}).get("job_title", "Report"))
            short_bytes = export_to_excel(
                shortlist,
                f"{st.session_state.get('jd_data', {}).get('job_title', 'Report')}_Shortlist",
            )

            b1, b2 = st.columns(2)
            with b1:
                st.download_button(
                    "📥 Download Full Report (Excel)",
                    data=full_bytes,
                    file_name="resume_screening_full.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            with b2:
                st.download_button(
                    "📥 Download Shortlist Only (Excel)",
                    data=short_bytes,
                    file_name="resume_screening_shortlist.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            st.subheader("WhatsApp Messages")
            call_first_candidates = [c for c in candidates if c.get("recommendation") == "🟢 Call First"]

            if not call_first_candidates:
                st.caption("No Call First candidates yet.")

            for candidate in call_first_candidates:
                title = f"{candidate.get('name', 'Candidate')} | Score: {candidate.get('total_score', 0)}"
                with st.expander(title, expanded=False):
                    message = generate_whatsapp_message(
                        candidate,
                        st.session_state.get("jd_data", {}),
                        api_key=None,
                    )
                    st.code(message, language="text")
                    st.divider()


if __name__ == "__main__":
    main()
