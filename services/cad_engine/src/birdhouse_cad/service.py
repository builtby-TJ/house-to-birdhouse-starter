from __future__ import annotations

import json
import uuid
from pathlib import Path
from threading import Lock
from typing import Any

from .geometry import export_parts
from .models import HouseProject


class LocalJobRegistry:
    """Development-only job store. Replace with PostgreSQL and a durable queue."""

    def __init__(self, output_root: Path) -> None:
        self.output_root = output_root
        self.output_root.mkdir(parents=True, exist_ok=True)
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def generate(self, project: HouseProject) -> dict[str, Any]:
        job_id = uuid.uuid4().hex
        with self._lock:
            self._jobs[job_id] = {"job_id": job_id, "status": "RUNNING"}

        try:
            output_dir = self.output_root / job_id
            manifest = export_parts(project, output_dir)
            manifest_path = output_dir / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            result = {
                "job_id": job_id,
                "status": "READY",
                "output_dir": str(output_dir),
                "manifest": manifest,
            }
        except Exception as exc:  # pragma: no cover - defensive API boundary
            result = {"job_id": job_id, "status": "FAILED", "error": str(exc)}

        with self._lock:
            self._jobs[job_id] = result
        return result

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            return self._jobs.get(job_id)
