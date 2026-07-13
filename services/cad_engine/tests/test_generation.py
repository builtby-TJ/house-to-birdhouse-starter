import json
from pathlib import Path

from birdhouse_cad.geometry import export_parts
from birdhouse_cad.models import HouseProject


ROOT = Path(__file__).resolve().parents[3]


def test_generates_six_parts_and_preview(tmp_path: Path) -> None:
    data = json.loads((ROOT / "sample_projects/basic_colonial.json").read_text())
    project = HouseProject.model_validate(data)
    manifest = export_parts(project, tmp_path)

    assert manifest["part_count"] == 6
    assert (tmp_path / "exploded_preview.glb").exists()
    expected = {
        "front_wall.stl",
        "back_wall.stl",
        "left_wall.stl",
        "right_wall.stl",
        "roof.stl",
        "floor.stl",
    }
    assert expected.issubset({path.name for path in tmp_path.iterdir()})
