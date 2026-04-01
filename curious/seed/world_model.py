"""
World Model — Stores predictions about the observed system.

THIS FILE IS EVOLVED BY THE AI.
The AI reads this code, finds weaknesses, rewrites it, and tests improvements.
"""

import json
import time
import sqlite3
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Prediction:
    id: str
    statement: str          # "File X will change within 24h"
    confidence: float       # 0.0 to 1.0
    evidence: list[str]     # observations that led to this
    created_at: float       # timestamp
    deadline: float         # when to check if correct
    resolved: bool = False
    was_correct: bool | None = None
    resolved_at: float | None = None


class WorldModel:
    """Stores and manages predictions about the observed system."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                statement TEXT NOT NULL,
                confidence REAL NOT NULL,
                evidence TEXT NOT NULL,
                created_at REAL NOT NULL,
                deadline REAL NOT NULL,
                resolved INTEGER DEFAULT 0,
                was_correct INTEGER,
                resolved_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                source TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_prediction(self, prediction: Prediction):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO predictions VALUES (?,?,?,?,?,?,?,?,?)",
            (
                prediction.id,
                prediction.statement,
                prediction.confidence,
                json.dumps(prediction.evidence),
                prediction.created_at,
                prediction.deadline,
                int(prediction.resolved),
                prediction.was_correct if prediction.was_correct is not None else None,
                prediction.resolved_at,
            ),
        )
        conn.commit()
        conn.close()

    def add_observation(self, source: str, content: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO observations (timestamp, source, content) VALUES (?, ?, ?)",
            (time.time(), source, content),
        )
        conn.commit()
        conn.close()

    def get_pending_predictions(self) -> list[Prediction]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT * FROM predictions WHERE resolved = 0 ORDER BY deadline ASC"
        ).fetchall()
        conn.close()
        return [self._row_to_prediction(r) for r in rows]

    def get_expired_predictions(self) -> list[Prediction]:
        now = time.time()
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT * FROM predictions WHERE resolved = 0 AND deadline < ?",
            (now,),
        ).fetchall()
        conn.close()
        return [self._row_to_prediction(r) for r in rows]

    def get_recent_observations(self, limit: int = 50) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            "SELECT timestamp, source, content FROM observations ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [{"timestamp": r[0], "source": r[1], "content": r[2]} for r in rows]

    def resolve_prediction(self, prediction_id: str, was_correct: bool):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE predictions SET resolved = 1, was_correct = ?, resolved_at = ? WHERE id = ?",
            (int(was_correct), time.time(), prediction_id),
        )
        conn.commit()
        conn.close()

    def get_accuracy(self, window_days: int | None = None) -> dict:
        conn = sqlite3.connect(self.db_path)
        query = "SELECT was_correct FROM predictions WHERE resolved = 1"
        params = ()
        if window_days:
            cutoff = time.time() - (window_days * 86400)
            query += " AND resolved_at > ?"
            params = (cutoff,)

        rows = conn.execute(query, params).fetchall()
        conn.close()

        if not rows:
            return {"total": 0, "correct": 0, "accuracy": 0.0}

        total = len(rows)
        correct = sum(1 for r in rows if r[0] == 1)
        return {"total": total, "correct": correct, "accuracy": correct / total}

    def get_stats(self) -> dict:
        conn = sqlite3.connect(self.db_path)
        total_predictions = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        pending = conn.execute("SELECT COUNT(*) FROM predictions WHERE resolved = 0").fetchone()[0]
        total_observations = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        conn.close()

        accuracy = self.get_accuracy()
        return {
            "total_predictions": total_predictions,
            "pending_predictions": pending,
            "resolved_predictions": accuracy["total"],
            "correct_predictions": accuracy["correct"],
            "accuracy": accuracy["accuracy"],
            "total_observations": total_observations,
        }

    def _row_to_prediction(self, row) -> Prediction:
        return Prediction(
            id=row[0],
            statement=row[1],
            confidence=row[2],
            evidence=json.loads(row[3]),
            created_at=row[4],
            deadline=row[5],
            resolved=bool(row[6]),
            was_correct=bool(row[7]) if row[7] is not None else None,
            resolved_at=row[8],
        )
