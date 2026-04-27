# AI Resume Screener

Rule-based resume screening app for Indian hiring workflows, built with Python and Streamlit.

## Overview
This project screens resumes against a job description using deterministic extraction and scoring logic.

Core principles:
- No external LLM APIs required for extraction or scoring.
- Rule-based parsing for JD and resume fields.
- Repeatable scoring with transparent components.
- Recruiter override support before analysis.

## Key Features
- Multi-format input support: PDF, DOCX, TXT.
- JD extraction with validation and manual correction before analysis.
- Resume parsing for name, contact, location, experience, education, and skills.
- Skill normalization via alias dictionary.
- Weighted scoring and ranking.
- Duplicate detection.
- Candidate detail view with score breakdown and explanation.
- Excel export for full report and shortlist.

## JD Validation Flow (Tab 1)
The app now uses a strict 3-step JD flow:

1. Add JD
- Paste JD text or upload a JD file.

2. Validate extraction
- Click Extract JD Details.
- Review the validation panel with confidence markers:
  - High confidence: extracted and likely correct.
  - Low confidence: extracted but uncertain.
  - Missing: could not extract.

3. Confirm or override
- Edit all fields on the right panel as needed.
- Confirm JD.
- Resume upload and analysis are unlocked only after confirmation.

This ensures scoring always uses recruiter-confirmed JD data instead of raw extraction output.

## Scoring Model
| Component | Max Score | Method |
|---|---:|---|
| Skill Match | 40 | Required skill coverage with preferred-skill bonus |
| Experience Match | 25 | Candidate vs JD min-max experience fit |
| Semantic Similarity | 20 | TF-IDF plus sentence embedding similarity |
| Location Match | 10 | Exact, metro, remote, or not-specified logic |
| Education Match | 5 | JD education requirement vs candidate education |
| Total | 100 | Sum capped at 100 |

Recommendation bands:
- 80 and above: Call First
- 60 to 79.9: Backup
- Below 60: Not Suitable

## Tech Stack
- Python
- Streamlit
- Pandas
- Plotly
- scikit-learn
- sentence-transformers
- SQLite

## Project Structure
- app.py: Streamlit interface and orchestration
- extractor.py: Raw text extraction from uploaded files
- parser.py: Rule-based parsing for JD and resume fields
- skill_data.py: Skill dictionary and alias pattern matching
- matcher.py: Scoring and ranking logic
- utils.py: Helper utilities and duplicate detection
- database.py: Persistence helpers
- exporter.py: Excel export
- explainer.py: Rule-based explanations and message text
- config.py: Constants, thresholds, and weights

## Setup
Recommended: use a local virtual environment.

1. Create and activate environment

Linux or macOS:

	python -m venv .venv
	source .venv/bin/activate

Windows (PowerShell):

	python -m venv .venv
	.venv\Scripts\Activate.ps1

2. Install dependencies

	pip install -r requirements.txt

3. Run app

	streamlit run app.py

## Usage
1. Open Upload and Analyze tab.
2. Paste or upload JD.
3. Click Extract JD Details.
4. Validate and confirm JD fields.
5. Upload resumes.
6. Click Analyze All Resumes.
7. Review rankings, details, and exports in remaining tabs.

## Current Limitations
- Regex parsing quality depends on document text quality.
- Experience estimation from date ranges is heuristic.
- Dictionary-based skill matching may miss very niche terms.
- Semantic score can vary with heavily noisy or OCR-corrupted input.

## Notes
- If JD location is not specified, location score is treated as fully satisfied.
- Preferred skills are optional and affect bonus scoring, not mandatory fit.
- JD confirmation is required before resume analysis by design.
