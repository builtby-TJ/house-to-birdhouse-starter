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
- STEP round-trip, STL watertightness, solid validity, dimensional, and assembly-alignment assertions.

Verification result: `6 passed`. The original sample also continues to generate six watertight reported meshes and its exploded GLB preview.

The coupon manifest intentionally reports `production_cad_test_coupons_unvalidated_physically`. The selected screw supplier dimensions have not been confirmed, and no physical fit/print test has been performed. Docker is not available in the verification environment, so the updated container smoke test could not be executed here.
