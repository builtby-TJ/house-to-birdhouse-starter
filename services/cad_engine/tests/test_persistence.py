from __future__ import annotations

import json
from pathlib import Path

from birdhouse_cad.models import HouseProject
from birdhouse_cad.persistence import PersistentProjectStore


ROOT = Path(__file__).resolve().parents[3]


def _project() -> HouseProject:
    return HouseProject.model_validate_json(
        (ROOT / "sample_projects/basic_colonial.json").read_text()
    )


def test_project_revisions_survive_store_reopen(tmp_path: Path) -> None:
    database = tmp_path / "birdhouse.sqlite3"
    store = PersistentProjectStore(database, tmp_path / "jobs")
    created = store.create_project(_project())

    revised_data = json.loads(_project().model_dump_json())
    revised_data["project_name"] = "Revised Colonial"
    revised = store.revise_project(created["project_id"], HouseProject.model_validate(revised_data))

    reopened = PersistentProjectStore(database, tmp_path / "jobs")
    persisted = reopened.get_project(created["project_id"])
    assert revised is not None
    assert persisted is not None
    assert persisted["revision"] == 2
    assert persisted["project_name"] == "Revised Colonial"


def test_persistent_generation_records_ready_job_and_manifest(tmp_path: Path) -> None:
    store = PersistentProjectStore(tmp_path / "birdhouse.sqlite3", tmp_path / "jobs")
    created = store.create_project(_project())
    job = store.generate(created["project_id"])

    assert job is not None
    assert job["status"] == "READY"
    assert job["revision"] == 1
    assert job["manifest"]["part_count"] == 6
    assert store.get_job(job["job_id"])["status"] == "READY"
