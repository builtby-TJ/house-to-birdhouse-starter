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
pip install -e .

birdhouse-cad generate ../../sample_projects/basic_colonial.json --output ../../generated/basic_colonial
birdhouse-cad validate ../../sample_projects/basic_colonial.json
```

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

The starter uses an in-process job registry for local development. Production should use PostgreSQL, object storage, Redis, and a durable worker queue.

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
