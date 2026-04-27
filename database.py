from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Dict, List

DB_PATH = "resume_screener.db"


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            job_title TEXT,
            jd_text TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            name TEXT,
            email TEXT,
            phone TEXT,
            location TEXT,
            skills_json TEXT,
            total_experience_years REAL,
            current_company TEXT,
            notice_period TEXT,
            current_ctc TEXT,
            expected_ctc TEXT,
            total_score REAL,
            recommendation TEXT,
            score_breakdown_json TEXT,
            explanation TEXT,
            resume_filename TEXT,
            is_duplicate INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()


def save_session(job_title: str, jd_text: str) -> int:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (created_at, job_title, jd_text) VALUES (?, ?, ?)",
        (datetime.utcnow().isoformat(), job_title, jd_text),
    )
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(session_id)


def save_candidate(session_id: int, candidate_dict: Dict) -> int:
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO candidates (
            session_id, name, email, phone, location, skills_json,
            total_experience_years, current_company, notice_period,
            current_ctc, expected_ctc, total_score, recommendation,
            score_breakdown_json, explanation, resume_filename, is_duplicate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            candidate_dict.get("name"),
            candidate_dict.get("email"),
            candidate_dict.get("phone"),
            candidate_dict.get("location"),
            json.dumps(candidate_dict.get("skills", [])),
            candidate_dict.get("total_experience_years"),
            candidate_dict.get("current_company"),
            candidate_dict.get("notice_period"),
            candidate_dict.get("current_ctc"),
            candidate_dict.get("expected_ctc"),
            candidate_dict.get("total_score"),
            candidate_dict.get("recommendation"),
            json.dumps(candidate_dict.get("score_breakdown", {})),
            candidate_dict.get("explanation"),
            candidate_dict.get("resume_filename"),
            1 if candidate_dict.get("is_duplicate") else 0,
        ),
    )

    candidate_id = cur.lastrowid
    conn.commit()
    conn.close()
    return int(candidate_id)


def get_session_candidates(session_id: int) -> List[Dict]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM candidates WHERE session_id = ? ORDER BY total_score DESC", (session_id,))
    rows = cur.fetchall()
    conn.close()

    candidates: List[Dict] = []
    for row in rows:
        item = dict(row)
        item["skills"] = json.loads(item.get("skills_json") or "[]")
        item["score_breakdown"] = json.loads(item.get("score_breakdown_json") or "{}")
        item["is_duplicate"] = bool(item.get("is_duplicate", 0))
        candidates.append(item)
    return candidates


def delete_session(session_id: int) -> None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM candidates WHERE session_id = ?", (session_id,))
    cur.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
