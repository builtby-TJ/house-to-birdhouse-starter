# Current Build Status

## Completed software milestones

- Reproducible CadQuery/OpenCascade container image
- Parametric screw-fit, corner, base, and roof assembly coupons
- JSON-driven six-part production CAD kernel
- True pilot holes, clearance holes, counterbores, floor lips, and roof ribs
- Normalized facade windows, doors, shutters, trim, color groups, and entrance opening
- STEP, STL, exploded GLB, and multi-object 3MF delivery package
- Validation report, hardware list, project JSON, and assembly instructions
- Persistent revisioned projects and generation jobs
- Interactive four-facade operator editor
- Guided eight-view photo capture checklist
- Resolution, exposure, blur, duplicate, and COLMAP-availability diagnostics
- Automated backend, export, API, web, and container validation

## Ready to test

The application is ready for local operator-workflow and software-output testing.
Generated production CAD remains marked `production_cad_unvalidated_physically`.

## External blockers to print-ready certification

- Select and purchase the exact #4 x 1/2-inch stainless self-tapping pan-head screw.
- Record its supplier, part number, head diameter, head height, thread diameter, and actual length.
- Print the coupons and record pilot, rabbet, lip, and rib fit results.
- Feed confirmed measurements and fit compensation back into the mechanical standard.
- Print and assemble a complete reference house.

## Deployment work not required for local product testing

- PostgreSQL adapter and migration strategy
- S3-compatible object storage
- Redis-backed distributed workers and retries
- Authentication, authorization, retention controls, and audit-log policy
- Hosted COLMAP worker and representative customer photo corpus
- Payment/order workflow and production operations dashboard
