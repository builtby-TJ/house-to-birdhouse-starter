from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

from .models import HouseProject
from .production import export_production_model


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class PersistentProjectStore:
    """Revisioned local store with the same boundary intended for PostgreSQL deployment."""

    def __init__(self, database_path: Path, output_root: Path) -> None:
        self.database_path = database_path
        self.output_root = output_root
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_root.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize()

    @classmethod
    def from_environment(cls) -> "PersistentProjectStore":
        return cls(
            Path(os.environ.get("BIRDHOUSE_DATABASE_PATH", "generated_jobs/birdhouse.sqlite3")),
            Path(os.environ.get("BIRDHOUSE_OUTPUT_ROOT", "generated_jobs")),
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    current_revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS revisions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    revision_number INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(project_id, revision_number)
                );
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    revision_number INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    output_dir TEXT,
                    manifest_json TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def create_project(self, project: HouseProject) -> dict[str, Any]:
        project_id = uuid.uuid4().hex
        now = _utc_now()
        with self._lock, self._connect() as connection:
            connection.execute(
                "INSERT INTO projects VALUES (?, ?, 1, ?, ?)",
                (project_id, project.project_name, now, now),
            )
            connection.execute(
                "INSERT INTO revisions VALUES (?, ?, 1, ?, ?)",
                (uuid.uuid4().hex, project_id, project.model_dump_json(), now),
            )
        return self.get_project(project_id)

    def revise_project(self, project_id: str, project: HouseProject) -> dict[str, Any] | None:
        now = _utc_now()
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT current_revision FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if row is None:
                return None
            revision = int(row["current_revision"]) + 1
            connection.execute(
                "INSERT INTO revisions VALUES (?, ?, ?, ?, ?)",
                (uuid.uuid4().hex, project_id, revision, project.model_dump_json(), now),
            )
            connection.execute(
                "UPDATE projects SET name = ?, current_revision = ?, updated_at = ? WHERE id = ?",
                (project.project_name, revision, now, project_id),
            )
        return self.get_project(project_id)

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT p.*, r.payload_json
                FROM projects p JOIN revisions r
                  ON r.project_id = p.id AND r.revision_number = p.current_revision
                WHERE p.id = ?
                """,
                (project_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "project_id": row["id"],
            "project_name": row["name"],
            "revision": row["current_revision"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "project": json.loads(row["payload_json"]),
        }

    def list_projects(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, name, current_revision, updated_at FROM projects ORDER BY updated_at DESC"
            ).fetchall()
        return [
            {
                "project_id": row["id"],
                "project_name": row["name"],
                "revision": row["current_revision"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def generate(self, project_id: str) -> dict[str, Any] | None:
        stored = self.get_project(project_id)
        if stored is None:
            return None
        job_id = uuid.uuid4().hex
        now = _utc_now()
        revision = int(stored["revision"])
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO jobs VALUES (?, ?, ?, 'RUNNING', NULL, NULL, NULL, ?, ?)",
                (job_id, project_id, revision, now, now),
            )
        try:
            project = HouseProject.model_validate(stored["project"])
            output_dir = self.output_root / job_id
            manifest = export_production_model(project, output_dir)
            status = "READY"
            error = None
        except Exception as exc:  # pragma: no cover - defensive job boundary
            output_dir = None
            manifest = None
            status = "FAILED"
            error = str(exc)
        updated = _utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE jobs SET status = ?, output_dir = ?, manifest_json = ?, error = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    str(output_dir) if output_dir else None,
                    json.dumps(manifest) if manifest else None,
                    error,
                    updated,
                    job_id,
                ),
            )
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        return {
            "job_id": row["id"],
            "project_id": row["project_id"],
            "revision": row["revision_number"],
            "status": row["status"],
            "output_dir": row["output_dir"],
            "manifest": json.loads(row["manifest_json"]) if row["manifest_json"] else None,
            "error": row["error"],
        }
