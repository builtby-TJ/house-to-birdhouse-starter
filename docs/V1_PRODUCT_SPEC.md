# Version 1 Product Specification

## Goal

Accept guided photographs and corrected facade data for a residential house, then generate six independently printable parts that assemble into a recognizable birdhouse using one standardized screw type.

## Supported house geometry

- One rectangular main footprint
- One or two stories represented as a single facade height
- Front, back, left, and right facade panels
- Gable roof in the first production release
- Rectangular doors and windows
- Shallow facade relief for trim, shutters, siding, brick, and foundation
- Optional functional bird entrance opening

## Deferred geometry

- Curved walls
- Freeform roof surfaces
- Multiple attached wings
- Full decks, complex railings, and landscaping
- Automatic reconstruction of every decorative object
- Direct unattended printing

## Customer workflow

1. Create a project.
2. Identify the front of the house.
3. Capture at least two photographs of each side plus corner transition photographs.
4. Enter one known measurement.
5. Review corrected front, back, left, and right elevations.
6. Confirm doors, windows, roof type, entrance-hole location, and colors.
7. Preview the assembled and exploded model.
8. Generate and download the print package.

## Output package

- Multi-plate 3MF project
- Front, back, left, right, roof, and floor files
- STEP and STL where supported
- GLB browser preview
- Project JSON
- Validation report
- Assembly instructions
- Hardware list

## Acceptance standard

The system is commercially useful when an operator can correct four facade elevations and the software automatically creates six printable, physically fitting parts without manual CAD editing.
