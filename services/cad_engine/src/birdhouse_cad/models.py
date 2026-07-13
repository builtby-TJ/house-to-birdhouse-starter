from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FeatureKind(str, Enum):
    WINDOW = "window"
    DOOR = "door"
    GARAGE_DOOR = "garage_door"
    SHUTTER = "shutter"
    TRIM = "trim"


class FacadeFeature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: FeatureKind
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)
    relief_mm: float = Field(default=1.2, ge=0, le=8)
    color_group: str = "trim"

    @model_validator(mode="after")
    def contained_in_facade(self) -> "FacadeFeature":
        if self.x + self.width > 1.0 + 1e-9:
            raise ValueError("feature extends beyond facade width")
        if self.y + self.height > 1.0 + 1e-9:
            raise ValueError("feature extends beyond facade height")
        return self


class Facade(BaseModel):
    model_config = ConfigDict(extra="forbid")
    features: List[FacadeFeature] = Field(default_factory=list, max_length=100)


class ModelDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width_mm: float = Field(gt=80, le=300)
    depth_mm: float = Field(gt=80, le=300)
    wall_height_mm: float = Field(gt=60, le=300)
    wall_thickness_mm: float = Field(ge=3.2, le=8)
    entrance_hole_diameter_mm: Optional[float] = Field(default=None, ge=20, le=60)


class RoofDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(pattern="^gable$")
    pitch_degrees: float = Field(ge=15, le=60)
    overhang_mm: float = Field(ge=3, le=30)
    thickness_mm: float = Field(default=4.5, ge=3.2, le=8)


class Facades(BaseModel):
    model_config = ConfigDict(extra="forbid")

    front: Facade
    back: Facade
    left: Facade
    right: Facade


class HouseProject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_name: str = Field(min_length=1)
    model: ModelDimensions
    roof: RoofDefinition
    facades: Facades
    colors: Dict[str, str] = Field(default_factory=dict)
