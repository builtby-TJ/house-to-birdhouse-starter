from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq
import trimesh

from birdhouse_cad.models import HouseProject
from birdhouse_cad.production import (
    build_blank_shell,
    build_production_model,
    export_blank_shell,
    export_production_model,
)


ROOT = Path(__file__).resolve().parents[3]


def _sample_project() -> HouseProject:
    data = json.loads((ROOT / "sample_projects/basic_colonial.json").read_text())
    return HouseProject.model_validate(data)


def test_blank_shell_has_six_valid_solids_and_locked_hardware() -> None:
    parts = build_blank_shell(_sample_project())

    assert set(parts) == {"front_wall", "back_wall", "left_wall", "right_wall", "roof", "floor"}
    assert all(part.solid.val().isValid() for part in parts.values())
    assert all(part.solid.val().Volume() > 0 for part in parts.values())


def test_blank_shell_step_and_stl_exports_round_trip(tmp_path: Path) -> None:
    manifest = export_blank_shell(_sample_project(), tmp_path)

    assert manifest["part_count"] == 6
    assert manifest["modeled_screw_count"] == 24
    assert manifest["status"] == "production_cad_unvalidated_physically"
    for files in manifest["parts"].values():
        step = tmp_path / files["step"]
        stl = tmp_path / files["stl"]
        assert cq.importers.importStep(str(step)).val().Volume() > 0
        mesh = trimesh.load_mesh(stl)
        assert mesh.is_watertight
        assert mesh.volume > 0


def test_facade_model_adds_normalized_reliefs_and_entrance() -> None:
    project = _sample_project()
    blank = build_blank_shell(project)
    detailed = build_production_model(project)

    assert detailed["front_wall"].solid.val().Volume() != blank["front_wall"].solid.val().Volume()
    assert detailed["back_wall"].solid.val().Volume() > blank["back_wall"].solid.val().Volume()
    assert all(part.solid.val().isValid() for part in detailed.values())


def test_facade_model_exports_feature_and_color_manifest(tmp_path: Path) -> None:
    project = _sample_project()
    manifest = export_production_model(project, tmp_path)

    assert manifest["feature_count"] == 9
    assert manifest["color_groups"]["roof"] == "charcoal"
    assert manifest["entrance_hole_diameter_mm"] == 32
    assert manifest["part_count"] == 6
