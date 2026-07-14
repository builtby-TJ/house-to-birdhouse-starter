from __future__ import annotations

import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

import cadquery as cq
import trimesh

from .mechanical import MechanicalStandard, load_mechanical_standard
from .models import Facade, HouseProject


@dataclass(frozen=True)
class ProductionPart:
    name: str
    solid: cq.Workplane


def _centered_box(dx: float, dy: float, dz: float, z: float) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz).translate((0, 0, z))


def _cylinder_z(radius: float, length: float, x: float, y: float, z: float) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(0, 0, 1))
    return cq.Workplane(obj=solid)


def _cylinder_y(radius: float, length: float, x: float, y: float, z: float) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(x, y, z), cq.Vector(0, 1, 0))
    return cq.Workplane(obj=solid)


def _wall(
    name: str,
    width: float,
    height: float,
    thickness: float,
    standard: MechanicalStandard,
    corner_role: str,
    facade: Facade | None = None,
    entrance_hole_diameter: float | None = None,
) -> ProductionPart:
    screw = standard.screw
    wall = _centered_box(width, thickness, height, height / 2)
    lateral = (-width * 0.28, width * 0.28)

    for x in lateral:
        wall = wall.cut(
            _cylinder_z(screw.pilot_hole_diameter / 2, screw.target_engagement, x, 0, 0)
        )
        wall = wall.cut(
            _cylinder_z(
                screw.pilot_hole_diameter / 2,
                screw.target_engagement,
                x,
                0,
                height - screw.target_engagement,
            )
        )

    corner_diameter = (
        screw.clearance_hole_diameter if corner_role == "clearance" else screw.pilot_hole_diameter
    )
    for x in (-width / 2 + screw.minimum_edge_distance, width / 2 - screw.minimum_edge_distance):
        for z in (height * 0.35, height * 0.65):
            bore = _cylinder_y(
                corner_diameter / 2,
                thickness + 0.4,
                x,
                -thickness / 2 - 0.2,
                z,
            )
            wall = wall.cut(bore)
            if corner_role == "clearance":
                counterbore = _cylinder_y(
                    screw.counterbore_diameter / 2,
                    screw.counterbore_depth + 0.2,
                    x,
                    -thickness / 2 - 0.1,
                    z,
                )
                wall = wall.cut(counterbore)

    if facade is not None:
        for feature in facade.features:
            feature_width = width * feature.width
            feature_height = height * feature.height
            feature_x = width * (feature.x + feature.width / 2 - 0.5)
            feature_z = height * (feature.y + feature.height / 2)
            relief = max(feature.relief_mm, 0.3)
            detail = cq.Workplane("XY").box(feature_width, relief, feature_height).translate(
                (feature_x, thickness / 2 + relief / 2, feature_z)
            )
            wall = wall.union(detail)

    if entrance_hole_diameter is not None:
        entrance = _cylinder_y(
            entrance_hole_diameter / 2,
            thickness + 0.4,
            0,
            -thickness / 2 - 0.2,
            height * 0.72,
        )
        wall = wall.cut(entrance)

    if not wall.val().isValid():
        raise ValueError(f"invalid production wall: {name}")
    return ProductionPart(name, wall)


def _floor(project: HouseProject, standard: MechanicalStandard) -> ProductionPart:
    width = project.model.width_mm
    depth = project.model.depth_mm
    thickness = standard.nominal_floor_thickness
    lip_width = standard.base_coupon.lip_width
    lip_height = standard.base_coupon.lip_height
    inset = project.model.wall_thickness_mm / 2
    screw = standard.screw

    floor = _centered_box(width, depth, thickness, thickness / 2)
    floor = floor.union(_centered_box(width - 2 * inset, lip_width, lip_height, thickness + lip_height / 2).translate((0, -depth / 2 + inset, 0)))
    floor = floor.union(_centered_box(width - 2 * inset, lip_width, lip_height, thickness + lip_height / 2).translate((0, depth / 2 - inset, 0)))
    floor = floor.union(_centered_box(lip_width, depth - 2 * inset, lip_height, thickness + lip_height / 2).translate((-width / 2 + inset, 0, 0)))
    floor = floor.union(_centered_box(lip_width, depth - 2 * inset, lip_height, thickness + lip_height / 2).translate((width / 2 - inset, 0, 0)))

    stations = (
        (-width * 0.28, -depth / 2 + inset),
        (width * 0.28, -depth / 2 + inset),
        (-width * 0.28, depth / 2 - inset),
        (width * 0.28, depth / 2 - inset),
        (-width / 2 + inset, -depth * 0.28),
        (-width / 2 + inset, depth * 0.28),
        (width / 2 - inset, -depth * 0.28),
        (width / 2 - inset, depth * 0.28),
    )
    for x, y in stations:
        floor = floor.cut(_cylinder_z(screw.clearance_hole_diameter / 2, thickness + lip_height + 0.2, x, y, -0.1))
        floor = floor.cut(_cylinder_z(screw.counterbore_diameter / 2, screw.counterbore_depth + 0.1, x, y, -0.1))
    return ProductionPart("floor", floor)


def _roof(project: HouseProject, standard: MechanicalStandard) -> ProductionPart:
    width = project.model.width_mm + 2 * project.roof.overhang_mm
    run = project.model.depth_mm / 2 + project.roof.overhang_mm
    pitch = math.radians(project.roof.pitch_degrees)
    slope = run / math.cos(pitch)
    thickness = project.roof.thickness_mm
    ridge_z = project.model.wall_height_mm + run * math.tan(pitch)
    mid_z = (project.model.wall_height_mm + ridge_z) / 2

    left = cq.Workplane("XY").box(width, slope, thickness).rotate((0, 0, 0), (1, 0, 0), project.roof.pitch_degrees).translate((0, -run / 2, mid_z))
    right = cq.Workplane("XY").box(width, slope, thickness).rotate((0, 0, 0), (1, 0, 0), -project.roof.pitch_degrees).translate((0, run / 2, mid_z))
    ridge = _centered_box(width, thickness, thickness, ridge_z)
    roof = left.union(right).union(ridge)

    rib_width = standard.roof_coupon.rib_width
    rib_height = standard.roof_coupon.rib_height
    for y in (-project.model.depth_mm / 2, project.model.depth_mm / 2):
        rib = _centered_box(project.model.width_mm, rib_width, rib_height, project.model.wall_height_mm - rib_height / 2).translate((0, y, 0))
        roof = roof.union(rib)
    return ProductionPart("roof", roof)


def build_blank_shell(
    project: HouseProject, standard: MechanicalStandard | None = None
) -> dict[str, ProductionPart]:
    standard = standard or load_mechanical_standard()
    t = project.model.wall_thickness_mm
    h = project.model.wall_height_mm
    return {
        "front_wall": _wall("front_wall", project.model.width_mm, h, t, standard, "clearance"),
        "back_wall": _wall("back_wall", project.model.width_mm, h, t, standard, "clearance"),
        "left_wall": _wall("left_wall", project.model.depth_mm, h, t, standard, "pilot"),
        "right_wall": _wall("right_wall", project.model.depth_mm, h, t, standard, "pilot"),
        "roof": _roof(project, standard),
        "floor": _floor(project, standard),
    }


def build_production_model(
    project: HouseProject, standard: MechanicalStandard | None = None
) -> dict[str, ProductionPart]:
    standard = standard or load_mechanical_standard()
    t = project.model.wall_thickness_mm
    h = project.model.wall_height_mm
    return {
        "front_wall": _wall(
            "front_wall",
            project.model.width_mm,
            h,
            t,
            standard,
            "clearance",
            project.facades.front,
            project.model.entrance_hole_diameter_mm,
        ),
        "back_wall": _wall(
            "back_wall", project.model.width_mm, h, t, standard, "clearance", project.facades.back
        ),
        "left_wall": _wall(
            "left_wall", project.model.depth_mm, h, t, standard, "pilot", project.facades.left
        ),
        "right_wall": _wall(
            "right_wall", project.model.depth_mm, h, t, standard, "pilot", project.facades.right
        ),
        "roof": _roof(project, standard),
        "floor": _floor(project, standard),
    }


def export_blank_shell(project: HouseProject, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    parts = build_blank_shell(project)
    exports: dict[str, dict[str, object]] = {}
    for name, part in parts.items():
        step = output_dir / f"{name}.step"
        stl = output_dir / f"{name}.stl"
        cq.exporters.export(part.solid, str(step))
        cq.exporters.export(part.solid, str(stl), tolerance=0.01, angularTolerance=0.1)
        imported = cq.importers.importStep(str(step))
        if imported.val().Volume() <= 0:
            raise ValueError(f"STEP round-trip produced no solid for {name}")
        bounds = part.solid.val().BoundingBox()
        exports[name] = {
            "step": step.name,
            "stl": stl.name,
            "bounds_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
            "step_bytes": step.stat().st_size,
            "stl_bytes": stl.stat().st_size,
        }

    manifest = {
        "project_name": project.project_name,
        "generator": "birdhouse-cad production blank shell",
        "status": "production_cad_unvalidated_physically",
        "part_count": len(parts),
        "screw_standard": "#4 x 1/2 in stainless self-tapping pan-head",
        "modeled_screw_count": 24,
        "parts": exports,
        "known_limitations": [
            "Supplier screw dimensions have not been confirmed.",
            "Joint fits have not been validated with a physical print.",
            "Facade reliefs are added by the next production CAD ticket.",
        ],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def export_production_model(project: HouseProject, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    parts = build_production_model(project)
    exports: dict[str, dict[str, object]] = {}
    for name, part in parts.items():
        step = output_dir / f"{name}.step"
        stl = output_dir / f"{name}.stl"
        cq.exporters.export(part.solid, str(step))
        cq.exporters.export(part.solid, str(stl), tolerance=0.01, angularTolerance=0.1)
        imported = cq.importers.importStep(str(step))
        if imported.val().Volume() <= 0:
            raise ValueError(f"STEP round-trip produced no solid for {name}")
        exports[name] = {
            "step": step.name,
            "stl": stl.name,
            "step_bytes": step.stat().st_size,
            "stl_bytes": stl.stat().st_size,
        }

    package_files = _write_delivery_package(project, output_dir, exports)
    manifest = {
        "project_name": project.project_name,
        "generator": "birdhouse-cad production facade model",
        "status": "production_cad_unvalidated_physically",
        "part_count": len(parts),
        "modeled_screw_count": 24,
        "feature_count": sum(len(facade.features) for facade in (
            project.facades.front,
            project.facades.back,
            project.facades.left,
            project.facades.right,
        )),
        "color_groups": project.colors,
        "entrance_hole_diameter_mm": project.model.entrance_hole_diameter_mm,
        "parts": exports,
        "package_files": package_files,
        "known_limitations": [
            "Supplier screw dimensions have not been confirmed.",
            "Joint and facade relief fits have not been validated with a physical print.",
            "3MF multi-plate packaging remains open.",
        ],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def _write_delivery_package(
    project: HouseProject, output_dir: Path, exports: dict[str, dict[str, object]]
) -> dict[str, str]:
    project_path = output_dir / "project.json"
    project_path.write_text(project.model_dump_json(indent=2), encoding="utf-8")

    meshes = {
        name: trimesh.load_mesh(output_dir / str(files["stl"]))
        for name, files in exports.items()
    }
    scene = trimesh.Scene()
    offset = 0.0
    for name, mesh in meshes.items():
        placed = mesh.copy()
        placed.apply_translation((offset - placed.bounds[0][0], 0, 0))
        scene.add_geometry(placed, node_name=name, geom_name=name)
        offset += float(placed.extents[0]) + 20.0
    preview_path = output_dir / "exploded_preview.glb"
    scene.export(preview_path)

    package_3mf = output_dir / "print_package.3mf"
    _write_3mf(package_3mf, meshes)

    maximum = 300.0
    validation = {
        "status": "geometry_valid_unvalidated_physically",
        "all_parts_watertight": all(bool(mesh.is_watertight) for mesh in meshes.values()),
        "all_parts_within_bambu_h2d_conservative_profile": all(
            all(float(value) <= maximum for value in mesh.extents) for mesh in meshes.values()
        ),
        "printer_profile_max_mm": [maximum, maximum, maximum],
        "supplier_screw_measurements_confirmed": False,
        "physical_print_fit_confirmed": False,
    }
    validation_path = output_dir / "validation_report.json"
    validation_path.write_text(json.dumps(validation, indent=2), encoding="utf-8")

    hardware = {
        "screw": "#4 x 1/2 in stainless self-tapping pan-head",
        "required_quantity": 24,
        "spare_quantity": 4,
        "driver": "matching Phillips or Torx screwdriver for selected supplier screw",
        "supplier_part_number": None,
    }
    hardware_path = output_dir / "hardware_list.json"
    hardware_path.write_text(json.dumps(hardware, indent=2), encoding="utf-8")

    instructions_path = output_dir / "assembly_instructions.md"
    instructions_path.write_text(
        """# Birdhouse assembly instructions

1. Seat the four wall panels on the floor locating lips.
2. Install the eight base screws upward through the recessed floor holes.
3. Close the four stepped wall corners and install two screws per corner.
4. Seat the roof locating ribs in the wall-header grooves.
5. Install the eight roof screws downward through the recessed roof holes.
6. Stop if plastic splits, a screw spins freely, or a tip becomes visible.

This package is not physically validated. Confirm supplier screw dimensions and complete a printed fit test before customer use.
""",
        encoding="utf-8",
    )
    return {
        "project": project_path.name,
        "preview": preview_path.name,
        "3mf": package_3mf.name,
        "validation_report": validation_path.name,
        "hardware_list": hardware_path.name,
        "assembly_instructions": instructions_path.name,
    }


def _write_3mf(path: Path, meshes: dict[str, trimesh.Trimesh]) -> None:
    namespace = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", namespace)
    model = ET.Element(f"{{{namespace}}}model", {"unit": "millimeter", "xml:lang": "en-US"})
    resources = ET.SubElement(model, f"{{{namespace}}}resources")
    build = ET.SubElement(model, f"{{{namespace}}}build")
    offset = 0.0
    for object_id, (name, mesh) in enumerate(meshes.items(), start=1):
        obj = ET.SubElement(resources, f"{{{namespace}}}object", {"id": str(object_id), "name": name, "type": "model"})
        mesh_element = ET.SubElement(obj, f"{{{namespace}}}mesh")
        vertices = ET.SubElement(mesh_element, f"{{{namespace}}}vertices")
        for x, y, z in mesh.vertices:
            ET.SubElement(vertices, f"{{{namespace}}}vertex", {"x": str(float(x)), "y": str(float(y)), "z": str(float(z))})
        triangles = ET.SubElement(mesh_element, f"{{{namespace}}}triangles")
        for v1, v2, v3 in mesh.faces:
            ET.SubElement(triangles, f"{{{namespace}}}triangle", {"v1": str(int(v1)), "v2": str(int(v2)), "v3": str(int(v3))})
        ET.SubElement(build, f"{{{namespace}}}item", {"objectid": str(object_id), "transform": f"1 0 0 0 1 0 0 0 1 {offset} 0 0"})
        offset += float(mesh.extents[0]) + 20.0

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>"""
    relationships = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", content_types)
        package.writestr("_rels/.rels", relationships)
        package.writestr("3D/3dmodel.model", ET.tostring(model, encoding="utf-8", xml_declaration=True))
