# House-to-Birdhouse Web App — Starter Repository

This repository is the starting implementation for a web application that converts guided house photographs into a six-part, 3D-printable birdhouse kit:

1. Front wall
2. Back wall
3. Left wall
4. Right wall
5. Roof
6. Floor

The intended production output is a multi-plate 3MF project for Bambu Studio, plus individual STEP/STL files, browser-preview geometry, an assembly guide, and a validation report.

## What is working in this starter

- Version 1 product and mechanical specifications
- Locked #4 x 1/2-inch stainless self-tapping screw standard
- Machine-readable mechanical configuration
- JSON Schema for house-project data
- Pydantic project models
- FastAPI project/API scaffold
- Executable prototype geometry generator
- Sample six-part STL and GLB generation
- Automated tests for schema and output structure
- A handoff roadmap for developers

The executable geometry generator is an early prototype, not the final manufacturing CAD kernel. It proves the data flow and six-part output. The production milestone replaces/extends it with CadQuery/OpenCascade solids, true bores, rabbets, STEP export, and tolerance-controlled mating features.

## Run locally

Requires Python 3.11+.

```bash
cd services/cad_engine
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -e '.[dev,production-cad]'

birdhouse-cad generate ../../sample_projects/basic_colonial.json --output ../../generated/basic_colonial
birdhouse-cad validate ../../sample_projects/basic_colonial.json
birdhouse-cad generate-coupons --output ../../generated/test_coupons
birdhouse-cad generate-blank-shell ../../sample_projects/basic_colonial.json --output ../../generated/production_blank_shell
birdhouse-cad generate-production ../../sample_projects/basic_colonial.json --output ../../generated/production_model
```

Production CAD is pinned to CadQuery 2.8.0 and cadquery-ocp/OpenCascade
7.9.3.1.1. The test-coupon command reads all screw and joint dimensions from
`config/mechanical_standard.yaml` and writes verified STEP and STL exports.
The generated set includes screw-fit, corner-joint, raised-lip base-to-wall, and
underside-rib roof-to-header assembly coupons. These remain physically unvalidated until the selected supplier
screw and printed fits are measured.

The blank-shell command generates six CadQuery/OpenCascade solids with STEP and
STL exports, the locked 24-screw layout, floor lips, roof ribs, and true bores.
It remains physically unvalidated and is not labeled print-ready.
The production command adds JSON-defined normalized windows, doors, shutters,
trim, color-group metadata, and the optional functional entrance opening.
Its delivery package includes six STEP/STL pairs, project JSON, exploded GLB,
multi-object 3MF, validation report, hardware list, and assembly instructions.

Start the API:

```bash
uvicorn birdhouse_cad.api:app --reload --port 8000
```

Then open:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## Initial API workflow

```text
POST /v1/projects/validate
POST /v1/models/generate
GET  /v1/models/{job_id}
GET  /v1/models/{job_id}/manifest
```

Projects, revisions, and generation jobs persist in SQLite by default under
`generated_jobs/`. Configure `BIRDHOUSE_DATABASE_PATH` and `BIRDHOUSE_OUTPUT_ROOT`
for deployment storage. PostgreSQL and a durable distributed worker remain deployment work.

The operator web workspace supports four facade photo sets, draggable normalized
features, exact feature dimensions, measurement calibration, revision saves, CAD
generation, and the guided eight-view capture checklist. The vision diagnostic API
checks resolution, exposure, likely blur, and duplicates; it reports whether COLMAP
is installed without ever treating reconstruction output as a print mesh.

## Repository map

```text
apps/web/                    Next.js customer/operator UI scaffold
config/                      Mechanical and printer standards
docs/                        Product specification and handoff plan
sample_projects/             Known-good house inputs
schemas/                     Shared JSON schemas
services/cad_engine/         Python CAD/API service
infrastructure/              Docker Compose and deployment notes
```

## First production objective

Generate a physically validated six-part birdhouse from structured facade measurements before adding automated photogrammetry. The photo pipeline should populate the same project schema rather than bypass the parametric manufacturing engine.
