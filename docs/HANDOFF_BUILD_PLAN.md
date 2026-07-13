# Build and Handoff Plan

## Ownership model

The owner does not need to become the primary programmer. This repository is intended to be handed to a computational-CAD developer and a full-stack developer. The owner remains product decision-maker, supplies representative house photographs, approves simplification rules, and validates printed results.

## Workstream 1 — Manufacturing CAD engine

Primary owner: computational CAD developer.

Deliverables:

- Parametric wall solids
- Gable roof generator
- Floor generator
- Rabbet/lap corner joints
- Base locating lip or groove
- Roof locating ribs
- True screw clearance holes, pilot holes, counterbores, and reinforced bosses
- Door/window/trim relief generators
- STEP, STL, GLB, and 3MF-compatible exports
- Assembly collision and alignment tests

Definition of done:

- Six parts generate from JSON.
- All are valid closed solids.
- Screw centers align.
- Parts fit the printer profile.
- Printed reference assembly fits using the specified screws.

## Workstream 2 — Operator facade editor

Primary owner: full-stack developer with browser-graphics experience.

Deliverables:

- Photo upload and side labeling
- Perspective-correction controls
- Normalized facade coordinate system
- Add, move, resize, duplicate, and delete architectural features
- Known-dimension calibration
- Color/material grouping
- Three-dimensional assembled and exploded previews

## Workstream 3 — Guided photo capture

Deliverables:

- Mobile-friendly progressive web app
- Required shot checklist
- Blur, exposure, duplication, and resolution checks
- House-side and corner labeling
- Retake guidance
- Upload resume and progress state

## Workstream 4 — Reconstruction and vision assistance

Primary owner: computer-vision engineer.

Deliverables:

- COLMAP camera reconstruction
- Sparse/dense geometry diagnostics
- Major wall-plane estimation
- Facade rectification
- Building/obstruction segmentation
- Suggested windows, doors, rooflines, and wall outlines
- Confidence scores and review queue

The vision output must populate the shared project schema. It must not directly create uncontrolled print meshes.

## Workstream 5 — Production platform

Deliverables:

- Authentication
- PostgreSQL project database
- S3-compatible file storage
- Redis/message broker
- Durable workers
- Revisioned project files
- Job retries and error states
- Audit logs
- Data retention/deletion controls
- Operator dashboard

## Recommended hiring order

1. Computational CAD developer
2. Full-stack developer
3. Computer-vision engineer
4. Part-time product/UI designer
5. 3D-print/mechanical QA support

## Suggested paid CAD trial

Ask a candidate to implement one JSON-driven test project containing:

- Four parametric walls
- One gable roof
- One floor
- Alignment joints
- Twenty-four standardized screw locations
- One door and four windows
- Six STL files and one STEP assembly

Evaluate geometric correctness, code organization, tolerance awareness, reproducibility, and ease of changing dimensions.

## Milestones

### M0 — Specification lock

- Confirm actual screw supplier/part number.
- Measure its head diameter and height.
- Approve V1 house limitations.
- Approve target birdhouse dimensions.

### M1 — Six-part CAD proof

- Structured JSON to six solids
- Physical print and screw assembly
- Basic validation report

### M2 — Manual operator product

- Upload four-side photographs
- Trace/correct facades
- Generate downloadable print package

### M3 — Guided customer capture

- Mobile photo workflow
- Quality checks
- Measurement calibration

### M4 — Automated assistance

- Camera reconstruction
- Rectified elevations
- Suggested architectural features

### M5 — Pilot operations

- Payment/order workflow if required
- Operator review queue
- Production logging
- Controlled customer pilot
