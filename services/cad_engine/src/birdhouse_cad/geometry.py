from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable

import numpy as np
import trimesh

from .models import Facade, HouseProject


@dataclass(frozen=True)
class GeneratedPart:
    name: str
    mesh: trimesh.Trimesh


def _box(extents: Iterable[float], center: Iterable[float]) -> trimesh.Trimesh:
    mesh = trimesh.creation.box(extents=np.asarray(list(extents), dtype=float))
    mesh.apply_translation(np.asarray(list(center), dtype=float))
    return mesh


def _feature_reliefs(
    facade: Facade,
    facade_width: float,
    facade_height: float,
    wall_thickness: float,
    axis: str,
) -> list[trimesh.Trimesh]:
    meshes: list[trimesh.Trimesh] = []
    for feature in facade.features:
        fw = facade_width * feature.width
        fh = facade_height * feature.height
        fx = facade_width * (feature.x + feature.width / 2.0) - facade_width / 2.0
        fz = facade_height * (feature.y + feature.height / 2.0)
        relief = max(feature.relief_mm, 0.3)

        if axis == "x":
            feature_mesh = _box(
                (fw, relief, fh),
                (fx, wall_thickness / 2.0 + relief / 2.0, fz),
            )
        else:
            feature_mesh = _box(
                (relief, fw, fh),
                (wall_thickness / 2.0 + relief / 2.0, fx, fz),
            )
        meshes.append(feature_mesh)
    return meshes


def _bosses_for_wall(width: float, wall_height: float, thickness: float, axis: str) -> list[trimesh.Trimesh]:
    """Prototype receiving zones. Production CAD replaces these with bored solids."""
    boss_diameter = 9.0
    boss_depth = 8.0
    positions = [
        (-width * 0.28, 12.0),
        (width * 0.28, 12.0),
        (-width * 0.28, wall_height - 12.0),
        (width * 0.28, wall_height - 12.0),
    ]
    meshes: list[trimesh.Trimesh] = []
    for lateral, z in positions:
        cylinder = trimesh.creation.cylinder(radius=boss_diameter / 2.0, height=boss_depth, sections=32)
        if axis == "x":
            transform = trimesh.transformations.rotation_matrix(math.radians(90), [1, 0, 0])
            cylinder.apply_transform(transform)
            cylinder.apply_translation([lateral, -boss_depth / 2.0 + thickness / 2.0, z])
        else:
            transform = trimesh.transformations.rotation_matrix(math.radians(90), [0, 1, 0])
            cylinder.apply_transform(transform)
            cylinder.apply_translation([-boss_depth / 2.0 + thickness / 2.0, lateral, z])
        meshes.append(cylinder)
    return meshes


def _wall_part(name: str, width: float, height: float, thickness: float, facade: Facade, axis: str) -> GeneratedPart:
    if axis == "x":
        wall = _box((width, thickness, height), (0, 0, height / 2.0))
    else:
        wall = _box((thickness, width, height), (0, 0, height / 2.0))

    components = [wall]
    components.extend(_feature_reliefs(facade, width, height, thickness, axis))
    components.extend(_bosses_for_wall(width, height, thickness, axis))
    return GeneratedPart(name=name, mesh=trimesh.util.concatenate(components))


def _roof_part(project: HouseProject) -> GeneratedPart:
    width = project.model.width_mm + 2 * project.roof.overhang_mm
    slope_run = project.model.depth_mm / 2.0 + project.roof.overhang_mm
    pitch = math.radians(project.roof.pitch_degrees)
    slope_length = slope_run / math.cos(pitch)
    thickness = project.roof.thickness_mm

    left = _box((width, slope_length, thickness), (0, -slope_run / 2.0, 0))
    right = _box((width, slope_length, thickness), (0, slope_run / 2.0, 0))
    left.apply_transform(trimesh.transformations.rotation_matrix(pitch, [1, 0, 0]))
    right.apply_transform(trimesh.transformations.rotation_matrix(-pitch, [1, 0, 0]))

    roof_height = math.tan(pitch) * slope_run
    left.apply_translation([0, 0, project.model.wall_height_mm + roof_height / 2.0])
    right.apply_translation([0, 0, project.model.wall_height_mm + roof_height / 2.0])

    ridge = _box((width, 6.0, 6.0), (0, 0, project.model.wall_height_mm + roof_height))
    return GeneratedPart(name="roof", mesh=trimesh.util.concatenate([left, right, ridge]))


def _floor_part(project: HouseProject) -> GeneratedPart:
    width = project.model.width_mm
    depth = project.model.depth_mm
    thickness = 5.5
    floor = _box((width, depth, thickness), (0, 0, thickness / 2.0))

    lip_height = 4.0
    lip_width = 4.0
    components = [floor]
    components.append(_box((width - 8, lip_width, lip_height), (0, -depth / 2 + 8, thickness + lip_height / 2)))
    components.append(_box((width - 8, lip_width, lip_height), (0, depth / 2 - 8, thickness + lip_height / 2)))
    components.append(_box((lip_width, depth - 8, lip_height), (-width / 2 + 8, 0, thickness + lip_height / 2)))
    components.append(_box((lip_width, depth - 8, lip_height), (width / 2 - 8, 0, thickness + lip_height / 2)))
    return GeneratedPart(name="floor", mesh=trimesh.util.concatenate(components))


def generate_parts(project: HouseProject) -> Dict[str, GeneratedPart]:
    t = project.model.wall_thickness_mm
    h = project.model.wall_height_mm
    parts = {
        "front_wall": _wall_part("front_wall", project.model.width_mm, h, t, project.facades.front, "x"),
        "back_wall": _wall_part("back_wall", project.model.width_mm, h, t, project.facades.back, "x"),
        "left_wall": _wall_part("left_wall", project.model.depth_mm, h, t, project.facades.left, "y"),
        "right_wall": _wall_part("right_wall", project.model.depth_mm, h, t, project.facades.right, "y"),
        "roof": _roof_part(project),
        "floor": _floor_part(project),
    }
    return parts


def export_parts(project: HouseProject, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    parts = generate_parts(project)
    manifest_parts = []

    preview_meshes = []
    preview_offsets = {
        "front_wall": (-project.model.width_mm * 0.65, 0, 0),
        "back_wall": (project.model.width_mm * 0.65, 0, 0),
        "left_wall": (0, -project.model.depth_mm * 0.85, 0),
        "right_wall": (0, project.model.depth_mm * 0.85, 0),
        "roof": (0, 0, project.model.wall_height_mm * 0.35),
        "floor": (0, 0, -25),
    }

    for name, part in parts.items():
        stl_path = output_dir / f"{name}.stl"
        part.mesh.export(stl_path)
        bounds = part.mesh.bounds.tolist()
        manifest_parts.append(
            {
                "name": name,
                "file": stl_path.name,
                "watertight": bool(part.mesh.is_watertight),
                "bounds_mm": bounds,
                "faces": int(len(part.mesh.faces)),
                "vertices": int(len(part.mesh.vertices)),
            }
        )
        preview = part.mesh.copy()
        preview.apply_translation(preview_offsets[name])
        preview_meshes.append(preview)

    preview = trimesh.Scene(preview_meshes)
    preview_path = output_dir / "exploded_preview.glb"
    preview.export(preview_path)

    manifest = {
        "project_name": project.project_name,
        "generator": "birdhouse-cad prototype 0.1.0",
        "status": "prototype_geometry",
        "part_count": len(parts),
        "parts": manifest_parts,
        "preview": preview_path.name,
        "known_limitations": [
            "Prototype bosses do not yet contain subtractive pilot holes or counterbores.",
            "Production CAD must use CadQuery/OpenCascade for tolerance-controlled solids and STEP export.",
            "Roof geometry is a simplified proof of pipeline output."
        ]
    }
    return manifest
