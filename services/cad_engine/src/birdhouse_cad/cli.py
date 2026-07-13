from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import ValidationError

from .geometry import export_parts
from .models import HouseProject


def load_project(path: Path) -> HouseProject:
    data = json.loads(path.read_text(encoding="utf-8"))
    return HouseProject.model_validate(data)


def command_validate(args: argparse.Namespace) -> int:
    try:
        project = load_project(Path(args.project))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print(f"VALID: {project.project_name}")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    try:
        project = load_project(Path(args.project))
        output_dir = Path(args.output)
        manifest = export_parts(project, output_dir)
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        print(f"GENERATION FAILED: {exc}")
        return 1

    print(json.dumps(manifest, indent=2))
    print(f"Output: {output_dir.resolve()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="birdhouse-cad")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a house-project JSON file")
    validate.add_argument("project")
    validate.set_defaults(func=command_validate)

    generate = sub.add_parser("generate", help="Generate prototype six-part geometry")
    generate.add_argument("project")
    generate.add_argument("--output", required=True)
    generate.set_defaults(func=command_generate)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
