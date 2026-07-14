from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

import birdhouse_cad.api as api_module
from birdhouse_cad.persistence import PersistentProjectStore


ROOT = Path(__file__).resolve().parents[3]


def test_revisioned_api_generation_workflow(tmp_path: Path) -> None:
    api_module.store = PersistentProjectStore(tmp_path / "api.sqlite3", tmp_path / "jobs")
    client = TestClient(api_module.app)
    payload = json.loads((ROOT / "sample_projects/basic_colonial.json").read_text())

    created = client.post("/v1/projects", json=payload)
    assert created.status_code == 200
    project_id = created.json()["project_id"]

    payload["project_name"] = "API Revised Colonial"
    revised = client.put(f"/v1/projects/{project_id}", json=payload)
    assert revised.json()["revision"] == 2

    generated = client.post(f"/v1/projects/{project_id}/generate")
    assert generated.status_code == 200
    assert generated.json()["status"] == "READY"
    job_id = generated.json()["job_id"]

    manifest = client.get(f"/v1/models/{job_id}/manifest")
    assert manifest.status_code == 200
    assert manifest.json()["part_count"] == 6
