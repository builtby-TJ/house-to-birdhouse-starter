import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from birdhouse_cad.models import HouseProject


ROOT = Path(__file__).resolve().parents[3]


def test_sample_project_validates() -> None:
    data = json.loads((ROOT / "sample_projects/basic_colonial.json").read_text())
    project = HouseProject.model_validate(data)
    assert project.project_name == "Basic Colonial Prototype"
    assert len(project.facades.front.features) == 3


def test_feature_cannot_extend_past_wall() -> None:
    data = json.loads((ROOT / "sample_projects/basic_colonial.json").read_text())
    data["facades"]["front"]["features"][0]["x"] = 0.95
    with pytest.raises(ValidationError):
        HouseProject.model_validate(data)
