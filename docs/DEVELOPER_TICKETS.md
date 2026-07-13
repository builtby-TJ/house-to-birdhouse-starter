# Developer Ticket Queue

## CAD-001 — Production CAD environment

Create a reproducible Python 3.11 container with pinned CadQuery/OpenCascade dependencies. Add a smoke test that exports a valid STEP cube and STL cube.

**Acceptance criteria**

- Container builds from a clean machine.
- STEP and STL exports are non-empty.
- Dependency versions are documented and pinned.

## CAD-002 — Screw coupon

Generate a configurable coupon containing pilot holes of 2.1, 2.2, and 2.3 mm plus counterbores based on the selected physical screw.

**Acceptance criteria**

- Dimensions come from `mechanical_standard.yaml`.
- Hole labels are embossed or engraved.
- STEP and STL export successfully.

## CAD-003 — Corner assembly coupon

Generate two wall segments with a stepped rabbet alignment joint and two screw positions.

**Acceptance criteria**

- Parts self-locate at 90 degrees.
- Clearance holes are in the first part.
- Pilot holes are in the receiving part.
- Screw tips cannot protrude into the interior.
- Automated assembly alignment test passes.

## CAD-004 — Base assembly coupon

Generate a floor segment and wall segment using the raised locating lip and two upward screws.

## CAD-005 — Roof assembly coupon

Generate a wall header and roof segment using an underside locating rib and two downward screws.

## CAD-006 — Complete blank shell

Generate four blank walls, roof, and floor from structured dimensions. No facade decorations are required yet.

## CAD-007 — Facade feature system

Add parametric windows, doors, trim, shutters, and material/color groups using normalized coordinates.

## API-001 — Persistent project model

Replace the development job registry with PostgreSQL-backed projects, revisions, files, and jobs.

## UI-001 — Operator facade editor

Create four facade workspaces supporting photo placement and draggable normalized rectangles for doors and windows.

## CAPTURE-001 — Guided photo checklist

Create the front/right/back/left mobile capture sequence with required and optional shots.

## VISION-001 — COLMAP diagnostic worker

Accept project images and return camera-registration statistics, sparse cloud, and a diagnostic preview. Do not create the final print mesh from the raw reconstruction.
