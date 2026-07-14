# Starter Build Report

Date: 2026-07-13

## Verification performed

- Installed the Python package in editable mode.
- Ran the automated test suite.
- Validated the included sample project.
- Generated all six prototype STL files.
- Generated an exploded GLB preview.
- Confirmed the six reported meshes are watertight according to Trimesh.

## Test result

```text
3 passed
```

## Generated sample files

- `generated/basic_colonial/front_wall.stl`
- `generated/basic_colonial/back_wall.stl`
- `generated/basic_colonial/left_wall.stl`
- `generated/basic_colonial/right_wall.stl`
- `generated/basic_colonial/roof.stl`
- `generated/basic_colonial/floor.stl`
- `generated/basic_colonial/exploded_preview.glb`
- `generated/basic_colonial/manifest.json`

## Important limitation

The current output is a working software prototype demonstrating the six-part pipeline. It is not yet approved for physical production because true pilot bores, counterbores, rabbet tolerances, roof locating ribs, and final screw engagement must be implemented and physically validated in the production CAD milestone.

## Production CAD Milestone 1 update

The `production-cad-milestone-1` branch adds CadQuery/OpenCascade test geometry without replacing the six-part prototype generator:

- A parametric screw coupon with 2.1, 2.2, and 2.3 mm blind pilot bores, flat-bottom 6.0 x 2.0 mm counterbores, and engraved labels.
- A two-piece 90-degree corner coupon with a 0.2 mm-clearance stepped rabbet, two 3.1 mm clearance bores, two 2.2 mm pilot bores, and 2.0 mm modeled screw-tip safety.
- A two-piece base assembly coupon with a raised locating lip, clearance-matched wall groove, and two upward screw stations.
- A two-piece roof assembly coupon with an underside locating rib, clearance-matched header groove, and two downward screw stations.
- STEP round-trip, STL watertightness, solid validity, dimensional, and assembly-alignment assertions.

Verification result: `6 passed`. The original sample also continues to generate six watertight reported meshes and its exploded GLB preview.

CAD-006 adds a JSON-driven six-part CadQuery blank shell with four walls, a gable
roof, and a raised-lip floor. It exports STEP and watertight STL files while retaining
the explicit physically-unvalidated production status.

CAD-007 adds normalized facade reliefs and color-group metadata to the production
wall solids, plus the optional functional entrance opening from the shared schema.

API-001 now has persistent, revisioned projects and generation-job records using a
local SQLite deployment profile. The storage boundary is isolated for a later
PostgreSQL adapter; distributed workers and object storage remain deployment work.

UI-001 and CAPTURE-001 now provide an interactive four-facade editor and guided
eight-view capture checklist. VISION-001 has a diagnostic-only image quality endpoint
and an explicit COLMAP availability boundary; COLMAP is not installed in this environment.

The coupon manifest intentionally reports `production_cad_test_coupons_unvalidated_physically`. The selected screw supplier dimensions have not been confirmed, and no physical fit/print test has been performed. Docker is not available in the verification environment, so the updated container smoke test could not be executed here.
