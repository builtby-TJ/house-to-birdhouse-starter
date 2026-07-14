from __future__ import annotations

import math
from pathlib import Path

import cadquery as cq
import trimesh

from birdhouse_cad.coupons import (
    build_base_coupon,
    build_corner_coupon,
    build_screw_coupon,
    export_test_coupons,
)
from birdhouse_cad.mechanical import load_mechanical_standard


def _circle_radii(solid: cq.Workplane) -> list[float]:
    return [edge.radius() for edge in solid.val().Edges() if edge.geomType() == "CIRCLE"]


def test_locked_screw_standard_and_screw_coupon_dimensions() -> None:
    standard = load_mechanical_standard()
    coupon = build_screw_coupon(standard)

    assert standard.screw.designation == "#4 x 1/2 in"
    assert standard.screw.screw_type == "self_tapping"
    assert standard.screw.material == "stainless_steel"
    assert standard.screw.head == "pan"
    assert coupon.pilot_diameters == (2.1, 2.2, 2.3)
    bounds = coupon.solid.val().BoundingBox()
    assert math.isclose(bounds.xlen, coupon.width, abs_tol=0.01)
    assert math.isclose(bounds.ylen, coupon.depth, abs_tol=0.01)
    assert math.isclose(bounds.zlen, coupon.height, abs_tol=0.01)
    assert coupon.solid.val().isValid()

    radii = _circle_radii(coupon.solid)
    for diameter in (*coupon.pilot_diameters, standard.screw.counterbore_diameter):
        assert any(math.isclose(radius, diameter / 2, abs_tol=1e-6) for radius in radii)


def test_corner_coupon_alignment_holes_and_tip_safety() -> None:
    standard = load_mechanical_standard()
    coupon = build_corner_coupon(standard)

    assert len(coupon.screw_centers) == 2
    assert coupon.clearance_part.val().isValid()
    assert coupon.receiving_part.val().isValid()
    assert coupon.receiving_zone_end_y - coupon.screw_tip_y >= 2.0 - 1e-9
    assert math.isclose(
        coupon.clearance_part.intersect(coupon.receiving_part).val().Volume(),
        0.0,
        abs_tol=1e-6,
    )
    clearance_bounds = coupon.clearance_part.val().BoundingBox()
    receiving_bounds = coupon.receiving_part.val().BoundingBox()
    assert clearance_bounds.xlen > clearance_bounds.ylen
    assert receiving_bounds.ylen > receiving_bounds.xlen
    assert math.isclose(clearance_bounds.zlen, receiving_bounds.zlen, abs_tol=1e-6)

    clearance_radii = _circle_radii(coupon.clearance_part)
    receiving_radii = _circle_radii(coupon.receiving_part)
    assert any(
        math.isclose(radius, standard.screw.clearance_hole_diameter / 2, abs_tol=1e-6)
        for radius in clearance_radii
    )
    assert any(
        math.isclose(radius, standard.screw.counterbore_diameter / 2, abs_tol=1e-6)
        for radius in clearance_radii
    )
    assert any(
        math.isclose(radius, standard.screw.pilot_hole_diameter / 2, abs_tol=1e-6)
        for radius in receiving_radii
    )


def test_base_coupon_alignment_holes_and_tip_safety() -> None:
    standard = load_mechanical_standard()
    coupon = build_base_coupon(standard)

    assert len(coupon.screw_centers) == 2
    assert coupon.floor_part.val().isValid()
    assert coupon.wall_part.val().isValid()
    assert coupon.receiving_zone_end_z - coupon.screw_tip_z >= 2.0 - 1e-9
    assert math.isclose(
        coupon.floor_part.intersect(coupon.wall_part).val().Volume(),
        0.0,
        abs_tol=1e-6,
    )
    assert math.isclose(
        coupon.interface_z,
        standard.nominal_floor_thickness + standard.base_coupon.lip_height,
        abs_tol=1e-6,
    )

    floor_radii = _circle_radii(coupon.floor_part)
    wall_radii = _circle_radii(coupon.wall_part)
    assert any(
        math.isclose(radius, standard.screw.clearance_hole_diameter / 2, abs_tol=1e-6)
        for radius in floor_radii
    )
    assert any(
        math.isclose(radius, standard.screw.counterbore_diameter / 2, abs_tol=1e-6)
        for radius in floor_radii
    )
    assert any(
        math.isclose(radius, standard.screw.pilot_hole_diameter / 2, abs_tol=1e-6)
        for radius in wall_radii
    )


def test_coupon_step_and_stl_exports_round_trip(tmp_path: Path) -> None:
    manifest = export_test_coupons(tmp_path)

    assert manifest["locked_screw"]["designation"] == "#4 x 1/2 in"
    assert manifest["corner_coupon"]["part_count"] == 2
    assert manifest["base_coupon"]["part_count"] == 2
    for files in manifest["exports"].values():
        step = tmp_path / files["step"]
        stl = tmp_path / files["stl"]
        assert step.stat().st_size > 0
        assert stl.stat().st_size > 0
        assert cq.importers.importStep(str(step)).val().Volume() > 0
        mesh = trimesh.load_mesh(stl)
        assert mesh.is_watertight
        assert mesh.volume > 0
