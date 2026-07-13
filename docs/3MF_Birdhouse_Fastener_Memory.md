# Project Memory — Screw and Fastener Standard for 3MF Birdhouse Kit

## Purpose

This document records the locked screw/fastener decision for the 3D-printed six-piece birdhouse kit. It should be kept with the project files so future modeling, 3MF exports, assembly instructions, and hardware sourcing all use the same fastener standard.

## Product Context

The birdhouse will be produced as a ready-to-assemble kit, not as a fully assembled product. The box should include:

- 6 separately printed 3MF house parts
- 24 screws, plus a few extras
- a small included screwdriver
- printed/photo assembly instructions
- packaging suitable for a premium real-estate closing gift

The finished product is intended to function as an outdoor birdhouse, so the fastener system should be simple for the customer while still being suitable for long-term exterior exposure.

## Six-Part 3MF Assembly

The model should be designed as six separate printable parts from the beginning:

1. Base plate / floor
2. Front wall panel
3. Back wall panel
4. Left wall panel
5. Right wall panel
6. Roof assembly

The model should not be designed as one solid 3D model and then split apart afterward. Each part should include its own mating geometry, screw pockets, alignment features, and reinforced screw-receiving areas.

## Locked Fastener Direction

Use self-tapping screws directly into printed plastic.

Heat-set brass inserts are not being used for this version because they add tooling, installation time, and customer complexity. The goal is for the recipient to assemble the birdhouse with a simple included hand screwdriver.

## Locked Screw Standard

Use:

**#4 stainless steel self-tapping pan-head screws**

Preferred general specification:

- Size: #4
- Length: 1/2 inch
- Material: stainless steel
- Head style: pan head
- Drive style: Phillips or Torx
- Quantity: 24 screws total
- Extras: include 2–4 spare screws in the kit
- Tool: include the matching small screwdriver or driver bit

Preferred default:

**#4 × 1/2 in stainless steel self-tapping pan-head screw**

## Why Pan Head Instead of Countersunk Flat Head

The preferred design is a pan-head screw seated inside a counterbored pocket, not a flat-head screw seated in a conical countersink.

Reason:

- A pan-head screw clamps against a flat surface.
- A counterbored recess can hide the screw head while avoiding wedge pressure.
- A countersunk flat-head screw can create splitting or stress in printed plastic if overtightened.
- A counterbored pan-head pocket is more forgiving for a non-technical customer assembling the kit by hand.

The screw should sit flush or slightly below the exterior surface, but the recess should be a flat-bottom counterbore rather than a conical countersink unless future testing proves countersunk screws are acceptable.

## Wall and Boss Thickness Standard

Recommended geometry for the 3MF files:

| Area | Target Thickness |
|---|---:|
| General exterior wall panels | 4.0 mm |
| Base plate | 5.0–6.0 mm |
| Roof shell | 4.0–5.0 mm |
| Wall bottom sill receiving zone | 8.0–10.0 mm |
| Wall top header receiving zone | 8.0–10.0 mm |
| Vertical corner screw-receiving zone | 8.0–10.0 mm |
| Local screw boss outside diameter | 8.0–10.0 mm minimum |

The screw should not rely on a plain thin wall for holding strength. Every screw location should have a reinforced boss, rib, sill, header, or thickened receiving area.

## Hole Geometry Starting Point

Use the following as the starting geometry unless a specific screw supplier provides different dimensions:

| Feature | Recommended Starting Geometry |
|---|---:|
| Pilot hole into receiving plastic | 2.2 mm |
| Acceptable pilot-hole range | 2.1–2.3 mm |
| Clearance hole through first part | 3.0–3.2 mm |
| Counterbore diameter for screw head | 5.8–6.2 mm |
| Counterbore depth | 1.8–2.2 mm, or enough for chosen screw head |
| Minimum plastic around pilot hole | 3.0 mm radial minimum |
| Minimum screw-center distance from outside edge | 5.5–6.5 mm minimum |
| Target screw engagement into receiving plastic | approximately 6–8 mm |

The final counterbore diameter and depth should be checked against the actual #4 screw selected for sourcing, because pan-head diameter and height vary by manufacturer.

## Screw Layout

Total screws: **24**

### Base Plate to Wall Sill Plates — 8 Screws

- 2 screws per wall
- Screws pass upward from the base plate into the bottom sill of each wall panel
- Screw heads are recessed into the underside or lower surface of the base plate
- Wall panels need reinforced lower sill receiving zones

### Corner Wall-to-Wall Joints — 8 Screws

- 2 screws per corner
- 4 corners total
- Screws pass through the face of one wall panel into the edge of the adjacent wall panel
- Each corner should include lap, rabbet, or alignment geometry so screws clamp the joint but do not provide all alignment

### Roof to Wall Header Plates — 8 Screws

- 2 screws per wall
- Screws pass downward through the roof assembly into the top header of each wall panel
- Screw heads are recessed into the roof surface
- Each wall panel needs a reinforced top header receiving zone

## Alignment Features Required

The screws should clamp the parts together, but alignment should come from the printed geometry.

Include:

- Base plate groove or raised alignment lip
- Wall bottom tabs or sill features
- Rabbet or lap-style vertical corner joints
- Roof underside locating ribs
- Reinforced screw bosses
- Clear assembly orientation features so the customer cannot easily reverse parts

## Customer Assembly Notes

The kit should be designed so the customer uses one screw type and one included screwdriver.

Instructions should say:

- Do not overtighten.
- Tighten until the screw head is seated and the parts are snug.
- Stop when the screw is flush or slightly below the recessed pocket.
- Do not keep turning after resistance increases sharply.
- Assemble on a flat table.
- Confirm all wall panels are seated in the base before tightening roof screws.

The hardware bag should include:

- 24 required #4 stainless self-tapping screws
- 2–4 spare screws
- 1 small matching screwdriver or driver bit

## Outdoor Use Notes

Because the birdhouse is intended for outdoor use:

- Use stainless steel screws, not plain steel.
- Avoid black oxide screws for exterior use.
- Avoid zinc-plated screws if long-term weather exposure is a major goal.
- Keep screw tips from protruding into the bird cavity.
- Avoid sharp internal edges.
- Include drainage holes in the base.
- Include ventilation under the roof/eaves.
- Prefer PETG, ASA, or another outdoor-suitable filament over PLA for final outdoor use.

## Current Locked Decision

The project should proceed using:

**#4 × 1/2 in stainless steel self-tapping pan-head screws, seated in recessed counterbored pockets, with 4.0 mm nominal wall panels and 8.0–10.0 mm reinforced screw-receiving zones.**

This decision should be treated as the fastener standard for all six 3MF files unless intentionally revised later.
