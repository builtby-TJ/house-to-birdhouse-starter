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


def command_generate_coupons(args: argparse.Namespace) -> int:
    # Keep the prototype validate/generate commands usable when the optional
    # production-CAD dependency group is not installed.
    from .coupons import export_test_coupons

    try:
        output_dir = Path(args.output)
        manifest = export_test_coupons(output_dir)
    except (OSError, ValueError) as exc:
        print(f"COUPON GENERATION FAILED: {exc}")
        return 1

    print(json.dumps(manifest, indent=2))
    print(f"Output: {output_dir.resolve()}")
    return 0


def command_generate_blank_shell(args: argparse.Namespace) -> int:
    from .production import export_blank_shell

    try:
        project = load_project(Path(args.project))
        output_dir = Path(args.output)
        manifest = export_blank_shell(project, output_dir)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        print(f"PRODUCTION GENERATION FAILED: {exc}")
        return 1

    print(json.dumps(manifest, indent=2))
    print(f"Output: {output_dir.resolve()}")
    return 0


def command_generate_production(args: argparse.Namespace) -> int:
    from .production import export_production_model

    try:
        project = load_project(Path(args.project))
        output_dir = Path(args.output)
        manifest = export_production_model(project, output_dir)
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        print(f"PRODUCTION GENERATION FAILED: {exc}")
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

    coupons = sub.add_parser(
        "generate-coupons",
        help="Generate Production CAD screw, corner, and base assembly test coupons",
    )
    coupons.add_argument("--output", required=True)
    coupons.set_defaults(func=command_generate_coupons)

    blank_shell = sub.add_parser(
        "generate-blank-shell",
        help="Generate the six-part Production CAD blank shell",
    )
    blank_shell.add_argument("project")
    blank_shell.add_argument("--output", required=True)
    blank_shell.set_defaults(func=command_generate_blank_shell)

    production = sub.add_parser(
        "generate-production",
        help="Generate the six-part Production CAD model with facade reliefs",
    )
    production.add_argument("project")
    production.add_argument("--output", required=True)
    production.set_defaults(func=command_generate_production)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
