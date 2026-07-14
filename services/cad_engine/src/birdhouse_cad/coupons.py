from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

from .mechanical import MechanicalStandard, load_mechanical_standard


@dataclass(frozen=True)
class ScrewCoupon:
    solid: cq.Workplane
    pilot_diameters: tuple[float, ...]
    width: float
    depth: float
    height: float


@dataclass(frozen=True)
class CornerCoupon:
    clearance_part: cq.Workplane
    receiving_part: cq.Workplane
    screw_centers: tuple[tuple[float, float, float], ...]
    interface_y: float
    screw_tip_y: float
    receiving_zone_end_y: float
    fit_clearance: float


@dataclass(frozen=True)
class BaseCoupon:
    floor_part: cq.Workplane
    wall_part: cq.Workplane
    screw_centers: tuple[tuple[float, float, float], ...]
    interface_z: float
    screw_tip_z: float
    receiving_zone_end_z: float
    fit_clearance: float


@dataclass(frozen=True)
class RoofCoupon:
    header_part: cq.Workplane
    roof_part: cq.Workplane
    screw_centers: tuple[tuple[float, float, float], ...]
    interface_z: float
    screw_tip_z: float
    receiving_zone_end_z: float
    fit_clearance: float


def _box(x: float, y: float, z: float, dx: float, dy: float, dz: float) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz, centered=(False, False, False)).translate((x, y, z))


def _cylinder_y(radius: float, length: float, x: float, y: float, z: float) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(0, 1, 0))
    return cq.Workplane(obj=solid)


def _cylinder_z(radius: float, length: float, x: float, y: float, z: float) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(0, 0, 1))
    return cq.Workplane(obj=solid)


def _cylinder_negative_z(
    radius: float, length: float, x: float, y: float, z: float
) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(0, 0, -1))
    return cq.Workplane(obj=solid)


def build_screw_coupon(standard: MechanicalStandard | None = None) -> ScrewCoupon:
    standard = standard or load_mechanical_standard()
    screw = standard.screw
    coupon = standard.screw_coupon
    pilots = (screw.pilot_hole_range[0], screw.pilot_hole_diameter, screw.pilot_hole_range[1])

    width = coupon.station_spacing * (len(pilots) + 1)
    height = (
        screw.counterbore_depth
        + screw.target_engagement
        + coupon.bottom_safety_thickness
    )
    body = _box(0, 0, 0, width, coupon.body_depth, height)

    for index, diameter in enumerate(pilots, start=1):
        x = coupon.station_spacing * index
        y = coupon.body_depth * 0.62
        counterbore = cq.Workplane("XY").center(x, y).circle(screw.counterbore_diameter / 2).extrude(
            -screw.counterbore_depth
        ).translate((0, 0, height))
        pilot = cq.Workplane("XY").center(x, y).circle(diameter / 2).extrude(
            -(screw.counterbore_depth + screw.target_engagement)
        ).translate((0, 0, height))
        label = cq.Workplane("XY", origin=(x, coupon.body_depth * 0.22, height)).text(
            f"{diameter:.1f}",
            4.0,
            -coupon.label_engraving_depth,
            halign="center",
            valign="center",
        )
        body = body.cut(counterbore).cut(pilot).cut(label)

    return ScrewCoupon(body, pilots, width, coupon.body_depth, height)


def build_corner_coupon(standard: MechanicalStandard | None = None) -> CornerCoupon:
    standard = standard or load_mechanical_standard()
    screw = standard.screw
    coupon = standard.corner_coupon

    # The local clearance boss is sized so the locked 12.7 mm screw achieves the
    # configured 7 mm engagement after seating in its flat-bottom counterbore.
    interface_y = screw.counterbore_depth + screw.length_mm - screw.target_engagement
    wall_outer_y = interface_y - standard.nominal_wall_thickness
    receiver_x0 = coupon.segment_length - standard.corner_receiving_zone
    screw_x = min(
        coupon.segment_length - screw.minimum_edge_distance,
        coupon.segment_length
        - coupon.rabbet_width
        - screw.clearance_hole_diameter / 2
        - 2 * coupon.fit_clearance,
    )

    clearance_part = _box(
        0,
        wall_outer_y,
        0,
        coupon.segment_length,
        standard.nominal_wall_thickness,
        coupon.segment_height,
    )

    boss_radius = screw.boss_outside_diameter / 2
    for z in coupon.screw_heights:
        boss = _cylinder_y(boss_radius, interface_y, screw_x, 0, z)
        clearance_bore = _cylinder_y(
            screw.clearance_hole_diameter / 2,
            interface_y + coupon.fit_clearance,
            screw_x,
            -coupon.fit_clearance / 2,
            z,
        )
        counterbore = _cylinder_y(
            screw.counterbore_diameter / 2,
            screw.counterbore_depth + coupon.fit_clearance / 2,
            screw_x,
            -coupon.fit_clearance / 2,
            z,
        )
        clearance_part = clearance_part.union(boss).cut(clearance_bore).cut(counterbore)

    notch_x = coupon.segment_length - coupon.rabbet_width - coupon.fit_clearance
    notch_y = interface_y - coupon.rabbet_depth - coupon.fit_clearance
    rabbet_notch = _box(
        notch_x,
        notch_y,
        0,
        coupon.rabbet_width + coupon.fit_clearance,
        coupon.rabbet_depth + coupon.fit_clearance,
        coupon.segment_height,
    )
    clearance_part = clearance_part.cut(rabbet_notch)

    receiving_part = _box(
        receiver_x0,
        interface_y,
        0,
        standard.corner_receiving_zone,
        coupon.segment_length,
        coupon.segment_height,
    )
    tongue = _box(
        coupon.segment_length - coupon.rabbet_width,
        interface_y - coupon.rabbet_depth,
        0,
        coupon.rabbet_width,
        coupon.rabbet_depth,
        coupon.segment_height,
    )
    receiving_part = receiving_part.union(tongue)

    receiving_zone_end_y = interface_y + standard.corner_receiving_zone
    screw_tip_y = screw.counterbore_depth + screw.length_mm
    centers = tuple((screw_x, interface_y, z) for z in coupon.screw_heights)
    for x, y, z in centers:
        receiver_boss = _cylinder_y(
            boss_radius,
            standard.corner_receiving_zone,
            x,
            y,
            z,
        )
        pilot = _cylinder_y(
            screw.pilot_hole_diameter / 2,
            screw.target_engagement,
            x,
            y,
            z,
        )
        receiving_part = receiving_part.union(receiver_boss).cut(pilot)

    if screw_tip_y > receiving_zone_end_y:
        raise ValueError("locked screw would protrude beyond the configured receiving zone")

    return CornerCoupon(
        clearance_part=clearance_part,
        receiving_part=receiving_part,
        screw_centers=centers,
        interface_y=interface_y,
        screw_tip_y=screw_tip_y,
        receiving_zone_end_y=receiving_zone_end_y,
        fit_clearance=coupon.fit_clearance,
    )


def build_base_coupon(standard: MechanicalStandard | None = None) -> BaseCoupon:
    standard = standard or load_mechanical_standard()
    screw = standard.screw
    coupon = standard.base_coupon
    floor_thickness = standard.nominal_floor_thickness
    wall_y0 = (coupon.floor_depth - standard.nominal_wall_thickness) / 2
    screw_y = coupon.floor_depth / 2

    floor_part = _box(0, 0, 0, coupon.segment_length, coupon.floor_depth, floor_thickness)
    lip = _box(
        0,
        screw_y - coupon.lip_width / 2,
        floor_thickness,
        coupon.segment_length,
        coupon.lip_width,
        coupon.lip_height,
    )
    floor_part = floor_part.union(lip)

    wall_part = _box(
        0,
        wall_y0,
        floor_thickness,
        coupon.segment_length,
        standard.nominal_wall_thickness,
        coupon.wall_height,
    )
    groove = _box(
        -coupon.fit_clearance / 2,
        screw_y - coupon.lip_width / 2 - coupon.fit_clearance,
        floor_thickness - coupon.fit_clearance / 2,
        coupon.segment_length + coupon.fit_clearance,
        coupon.lip_width + 2 * coupon.fit_clearance,
        coupon.lip_height + coupon.fit_clearance,
    )
    wall_part = wall_part.cut(groove)

    interface_z = floor_thickness + coupon.lip_height
    centers = tuple((x, screw_y, interface_z) for x in coupon.screw_positions)
    for x, y, _ in centers:
        clearance = _cylinder_z(
            screw.clearance_hole_diameter / 2,
            floor_thickness + coupon.lip_height + coupon.fit_clearance,
            x,
            y,
            -coupon.fit_clearance / 2,
        )
        counterbore = _cylinder_z(
            screw.counterbore_diameter / 2,
            screw.counterbore_depth + coupon.fit_clearance / 2,
            x,
            y,
            -coupon.fit_clearance / 2,
        )
        pilot = _cylinder_z(
            screw.pilot_hole_diameter / 2,
            screw.target_engagement,
            x,
            y,
            interface_z,
        )
        floor_part = floor_part.cut(clearance).cut(counterbore)
        wall_part = wall_part.cut(pilot)

    screw_tip_z = screw.counterbore_depth + screw.length_mm
    receiving_zone_end_z = floor_thickness + coupon.wall_height
    if screw_tip_z > receiving_zone_end_z:
        raise ValueError("locked screw would protrude beyond the base coupon wall")

    return BaseCoupon(
        floor_part=floor_part,
        wall_part=wall_part,
        screw_centers=centers,
        interface_z=interface_z,
        screw_tip_z=screw_tip_z,
        receiving_zone_end_z=receiving_zone_end_z,
        fit_clearance=coupon.fit_clearance,
    )


def build_roof_coupon(standard: MechanicalStandard | None = None) -> RoofCoupon:
    standard = standard or load_mechanical_standard()
    screw = standard.screw
    coupon = standard.roof_coupon
    roof_thickness = standard.nominal_roof_thickness
    header_y0 = (coupon.roof_depth - standard.nominal_wall_thickness) / 2
    screw_y = coupon.roof_depth / 2
    roof_top_z = coupon.header_height + roof_thickness

    header_part = _box(
        0,
        header_y0,
        0,
        coupon.segment_length,
        standard.nominal_wall_thickness,
        coupon.header_height,
    )
    groove = _box(
        -coupon.fit_clearance / 2,
        screw_y - coupon.rib_width / 2 - coupon.fit_clearance,
        coupon.header_height - coupon.rib_height - coupon.fit_clearance / 2,
        coupon.segment_length + coupon.fit_clearance,
        coupon.rib_width + 2 * coupon.fit_clearance,
        coupon.rib_height + coupon.fit_clearance,
    )
    header_part = header_part.cut(groove)

    roof_part = _box(
        0,
        0,
        coupon.header_height,
        coupon.segment_length,
        coupon.roof_depth,
        roof_thickness,
    )
    rib = _box(
        0,
        screw_y - coupon.rib_width / 2,
        coupon.header_height - coupon.rib_height,
        coupon.segment_length,
        coupon.rib_width,
        coupon.rib_height,
    )
    roof_part = roof_part.union(rib)

    interface_z = coupon.header_height - coupon.rib_height
    centers = tuple((x, screw_y, interface_z) for x in coupon.screw_positions)
    for x, y, _ in centers:
        clearance = _cylinder_negative_z(
            screw.clearance_hole_diameter / 2,
            roof_thickness + coupon.rib_height + coupon.fit_clearance,
            x,
            y,
            roof_top_z + coupon.fit_clearance / 2,
        )
        counterbore = _cylinder_negative_z(
            screw.counterbore_diameter / 2,
            screw.counterbore_depth + coupon.fit_clearance / 2,
            x,
            y,
            roof_top_z + coupon.fit_clearance / 2,
        )
        pilot = _cylinder_negative_z(
            screw.pilot_hole_diameter / 2,
            screw.target_engagement,
            x,
            y,
            interface_z,
        )
        roof_part = roof_part.cut(clearance).cut(counterbore)
        header_part = header_part.cut(pilot)

    screw_tip_z = roof_top_z - screw.counterbore_depth - screw.length_mm
    if screw_tip_z < 0:
        raise ValueError("locked screw would protrude beyond the roof coupon header")

    return RoofCoupon(
        header_part=header_part,
        roof_part=roof_part,
        screw_centers=centers,
        interface_z=interface_z,
        screw_tip_z=screw_tip_z,
        receiving_zone_end_z=0.0,
        fit_clearance=coupon.fit_clearance,
    )


def _export_verified(solid: cq.Workplane, step_path: Path, stl_path: Path) -> dict[str, int]:
    cq.exporters.export(solid, str(step_path))
    cq.exporters.export(solid, str(stl_path), tolerance=0.01, angularTolerance=0.1)
    sizes = {"step_bytes": step_path.stat().st_size, "stl_bytes": stl_path.stat().st_size}
    if min(sizes.values()) <= 0:
        raise ValueError(f"empty CAD export for {step_path.stem}")
    imported = cq.importers.importStep(str(step_path))
    if imported.val().Volume() <= 0:
        raise ValueError(f"STEP round-trip produced no solid for {step_path.stem}")
    return sizes


def export_test_coupons(output_dir: Path, standard: MechanicalStandard | None = None) -> dict:
    standard = standard or load_mechanical_standard()
    output_dir.mkdir(parents=True, exist_ok=True)
    screw_coupon = build_screw_coupon(standard)
    corner_coupon = build_corner_coupon(standard)
    base_coupon = build_base_coupon(standard)
    roof_coupon = build_roof_coupon(standard)

    solids = {
        "screw_test_coupon": screw_coupon.solid,
        "corner_clearance_part": corner_coupon.clearance_part,
        "corner_receiving_part": corner_coupon.receiving_part,
        "base_floor_part": base_coupon.floor_part,
        "base_wall_part": base_coupon.wall_part,
        "roof_header_part": roof_coupon.header_part,
        "roof_panel_part": roof_coupon.roof_part,
    }
    exports = {}
    for name, solid in solids.items():
        step_path = output_dir / f"{name}.step"
        stl_path = output_dir / f"{name}.stl"
        exports[name] = {
            "step": step_path.name,
            "stl": stl_path.name,
            **_export_verified(solid, step_path, stl_path),
        }

    manifest = {
        "status": "production_cad_test_coupons_unvalidated_physically",
        "units": standard.units,
        "locked_screw": {
            "designation": standard.screw.designation,
            "type": standard.screw.screw_type,
            "material": standard.screw.material,
            "head": standard.screw.head,
            "supplier_measurements_confirmed": standard.screw.supplier_measurements_confirmed,
        },
        "screw_coupon": {
            "pilot_diameters_mm": screw_coupon.pilot_diameters,
            "counterbore_diameter_mm": standard.screw.counterbore_diameter,
            "counterbore_depth_mm": standard.screw.counterbore_depth,
        },
        "corner_coupon": {
            "part_count": 2,
            "joint": "stepped_rabbet",
            "fit_clearance_mm": corner_coupon.fit_clearance,
            "clearance_hole_diameter_mm": standard.screw.clearance_hole_diameter,
            "pilot_hole_diameter_mm": standard.screw.pilot_hole_diameter,
            "screw_tip_safety_mm": corner_coupon.receiving_zone_end_y - corner_coupon.screw_tip_y,
            "screw_centers_mm": corner_coupon.screw_centers,
        },
        "base_coupon": {
            "part_count": 2,
            "alignment": "raised_perimeter_lip",
            "fit_clearance_mm": base_coupon.fit_clearance,
            "clearance_hole_diameter_mm": standard.screw.clearance_hole_diameter,
            "pilot_hole_diameter_mm": standard.screw.pilot_hole_diameter,
            "screw_tip_safety_mm": base_coupon.receiving_zone_end_z - base_coupon.screw_tip_z,
            "screw_centers_mm": base_coupon.screw_centers,
        },
        "roof_coupon": {
            "part_count": 2,
            "alignment": "underside_locating_rib",
            "fit_clearance_mm": roof_coupon.fit_clearance,
            "clearance_hole_diameter_mm": standard.screw.clearance_hole_diameter,
            "pilot_hole_diameter_mm": standard.screw.pilot_hole_diameter,
            "screw_tip_safety_mm": roof_coupon.screw_tip_z - roof_coupon.receiving_zone_end_z,
            "screw_centers_mm": roof_coupon.screw_centers,
        },
        "exports": exports,
    }
    (output_dir / "coupon_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
