# Start Here

## Can this be built for the owner?

Yes. The owner does not need to write the application personally. Development can proceed in this project as a sequence of reviewed code checkpoints, with outside specialists used only where access, physical testing, deployment credentials, or specialized CAD review is required.

## Division of responsibility

### Work that can be produced inside this project

- Product specifications and decision records
- Repository architecture
- Backend and frontend source code
- Parametric CAD scripts
- Data schemas and API contracts
- Automated tests
- Docker configuration
- Sample projects
- Validation logic
- Developer tickets and acceptance criteria
- Handoff packages and code-review guidance

### Work requiring owner or external access

- Purchasing and measuring the exact production screw
- Running physical prints on the target printer
- Confirming fit, finish, assembly force, and outdoor durability
- Creating and paying for cloud/vendor accounts
- Supplying deployment secrets and domain access
- App-store publishing if a native app is later chosen
- Professional security/legal review before public customer use

Those external actions do not require the owner to become a programmer. They can be performed by a contractor, printing service, or designated technical operator using the specifications in this repository.

## What has already been built

The starter contains an executable prototype that:

1. Validates a structured house-project JSON file.
2. Generates front, back, left, and right walls.
3. Generates a simplified gable roof and floor.
4. Adds facade relief features and prototype reinforced screw zones.
5. Exports six STL files.
6. Exports an exploded GLB preview.
7. Writes a machine-readable manifest.
8. Exposes a FastAPI validation/generation API.
9. Runs automated schema and output tests.

## Next implementation checkpoint

The next coding checkpoint is **Production CAD Milestone 1**:

- Install and pin CadQuery/OpenCascade.
- Rebuild one corner joint as a true CAD solid.
- Add true clearance bore, pilot bore, and counterbore geometry.
- Generate a printable corner coupon and screw-boss coupon.
- Export STEP and STL.
- Add dimensional assertions to automated tests.

## Exact first physical action

Select and purchase the intended #4 x 1/2-inch stainless self-tapping pan-head screw. Record:

- Manufacturer
- Part number
- Thread type
- Head diameter
- Head height
- Overall length
- Actual major thread diameter

The current dimensions are appropriate starting values, but the final counterbore must be generated from the selected supplier's screw measurements.

## Handoff instruction

Give a developer the complete repository and instruct them to read, in order:

1. `START_HERE.md`
2. `docs/V1_PRODUCT_SPEC.md`
3. `docs/3MF_Birdhouse_Fastener_Memory.md`
4. `config/mechanical_standard.yaml`
5. `docs/HANDOFF_BUILD_PLAN.md`
6. `docs/CURRENT_STATUS.md`

Their first pull request should complete Production CAD Milestone 1 without changing the locked six-part architecture or fastener standard.
