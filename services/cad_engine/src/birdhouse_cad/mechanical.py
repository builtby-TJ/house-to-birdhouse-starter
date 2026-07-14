from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

import yaml


def default_standard_path() -> Path:
    configured = os.environ.get("BIRDHOUSE_MECHANICAL_STANDARD")
    if configured:
        return Path(configured)
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / "mechanical_standard.yaml"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "config/mechanical_standard.yaml was not found; set BIRDHOUSE_MECHANICAL_STANDARD"
    )


@dataclass(frozen=True)
class ScrewStandard:
    designation: str
    length_mm: float
    screw_type: str
    material: str
    head: str
    pilot_hole_diameter: float
    pilot_hole_range: tuple[float, float]
    clearance_hole_diameter: float
    counterbore_diameter: float
    counterbore_depth: float
    boss_outside_diameter: float
    target_engagement: float
    minimum_edge_distance: float
    supplier_measurements_confirmed: bool


@dataclass(frozen=True)
class ScrewCouponStandard:
    body_depth: float
    station_spacing: float
    bottom_safety_thickness: float
    label_engraving_depth: float


@dataclass(frozen=True)
class CornerCouponStandard:
    segment_length: float
    segment_height: float
    rabbet_depth: float
    rabbet_width: float
    fit_clearance: float
    screw_heights: tuple[float, float]


@dataclass(frozen=True)
class BaseCouponStandard:
    segment_length: float
    floor_depth: float
    wall_height: float
    lip_width: float
    lip_height: float
    fit_clearance: float
    screw_positions: tuple[float, float]


@dataclass(frozen=True)
class MechanicalStandard:
    units: str
    nominal_wall_thickness: float
    nominal_floor_thickness: float
    corner_receiving_zone: float
    screw: ScrewStandard
    screw_coupon: ScrewCouponStandard
    corner_coupon: CornerCouponStandard
    base_coupon: BaseCouponStandard


def _positive(name: str, value: Any) -> float:
    number = float(value)
    if number <= 0:
        raise ValueError(f"{name} must be positive")
    return number


def load_mechanical_standard(path: Path | None = None) -> MechanicalStandard:
    standard_path = path or default_standard_path()
    data = yaml.safe_load(standard_path.read_text(encoding="utf-8"))
    screws = data["screws"]
    panels = data["panels"]
    coupons = data["test_coupons"]

    locked_values = {
        "designation": "#4 x 1/2 in",
        "type": "self_tapping",
        "material": "stainless_steel",
        "head": "pan",
    }
    for key, expected in locked_values.items():
        if screws.get(key) != expected:
            raise ValueError(f"locked screw {key} must remain {expected!r}")

    pilot_range = tuple(float(value) for value in screws["pilot_hole_range"])
    if len(pilot_range) != 2 or pilot_range[0] > pilot_range[1]:
        raise ValueError("pilot_hole_range must contain an ascending minimum and maximum")
    pilot = _positive("pilot_hole_diameter", screws["pilot_hole_diameter"])
    if not pilot_range[0] <= pilot <= pilot_range[1]:
        raise ValueError("pilot_hole_diameter must be inside pilot_hole_range")

    corner = coupons["corner_coupon"]
    heights = tuple(float(value) for value in corner["screw_heights"])
    if len(heights) != 2:
        raise ValueError("corner coupon requires exactly two screw heights")

    base = coupons["base_coupon"]
    screw_positions = tuple(float(value) for value in base["screw_positions"])
    if len(screw_positions) != 2:
        raise ValueError("base coupon requires exactly two screw positions")

    return MechanicalStandard(
        units=data["product"]["units"],
        nominal_wall_thickness=_positive("nominal_wall_thickness", panels["nominal_wall_thickness"]),
        nominal_floor_thickness=_positive("floor_thickness", panels["floor_thickness"]),
        corner_receiving_zone=_positive("corner_receiving_zone", panels["corner_receiving_zone"]),
        screw=ScrewStandard(
            designation=screws["designation"],
            length_mm=_positive("length_mm", screws["length_mm"]),
            screw_type=screws["type"],
            material=screws["material"],
            head=screws["head"],
            pilot_hole_diameter=pilot,
            pilot_hole_range=(pilot_range[0], pilot_range[1]),
            clearance_hole_diameter=_positive("clearance_hole_diameter", screws["clearance_hole_diameter"]),
            counterbore_diameter=_positive("counterbore_diameter", screws["counterbore_diameter"]),
            counterbore_depth=_positive("counterbore_depth", screws["counterbore_depth"]),
            boss_outside_diameter=_positive("boss_outside_diameter", screws["boss_outside_diameter"]),
            target_engagement=_positive("target_engagement", screws["target_engagement"]),
            minimum_edge_distance=_positive("minimum_edge_distance", screws["minimum_edge_distance"]),
            supplier_measurements_confirmed=bool(screws["supplier_measurements_confirmed"]),
        ),
        screw_coupon=ScrewCouponStandard(
            body_depth=_positive("body_depth", coupons["screw_coupon"]["body_depth"]),
            station_spacing=_positive("station_spacing", coupons["screw_coupon"]["station_spacing"]),
            bottom_safety_thickness=_positive(
                "bottom_safety_thickness", coupons["screw_coupon"]["bottom_safety_thickness"]
            ),
            label_engraving_depth=_positive(
                "label_engraving_depth", coupons["screw_coupon"]["label_engraving_depth"]
            ),
        ),
        corner_coupon=CornerCouponStandard(
            segment_length=_positive("segment_length", corner["segment_length"]),
            segment_height=_positive("segment_height", corner["segment_height"]),
            rabbet_depth=_positive("rabbet_depth", corner["rabbet_depth"]),
            rabbet_width=_positive("rabbet_width", corner["rabbet_width"]),
            fit_clearance=_positive("fit_clearance", corner["fit_clearance"]),
            screw_heights=(heights[0], heights[1]),
        ),
        base_coupon=BaseCouponStandard(
            segment_length=_positive("segment_length", base["segment_length"]),
            floor_depth=_positive("floor_depth", base["floor_depth"]),
            wall_height=_positive("wall_height", base["wall_height"]),
            lip_width=_positive("lip_width", base["lip_width"]),
            lip_height=_positive("lip_height", base["lip_height"]),
            fit_clearance=_positive("fit_clearance", base["fit_clearance"]),
            screw_positions=(screw_positions[0], screw_positions[1]),
        ),
    )
