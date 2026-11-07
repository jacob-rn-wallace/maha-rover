<p align="center">
  <img src="graphic-design/headers/almaha-header-edge-coarse.svg" alt="al-maha: a crescent Earth beside the Moon as a 15-degree trapezoid mosaic, with the al-maha Kufic wordmark between them" width="100%">
</p>

# المَهَا (al-maha)

An open-source, full-size replica of the UAE's **Rashid** lunar rover. It aims to look like the original and work roughly the way it does, in the spirit of Sawppy or the Beatty sisters' rover replicas, and to follow the original's dimensions wherever they are known.

*Al-maha* (المَهَا) is the Arabian oryx, and also the word for the oryx's eyes in classical Arabic poetry.

> **Status: early design, nothing built yet.** Branding is done. The original's dimensions are recorded with sources in [`docs/original-dimensions.md`](docs/original-dimensions.md); most outer dimensions are sourced (wheels, plan, height, stowed envelope, sidewall angle, cell grid), and gaps remain in the original's suspension and drivetrain layout and the exact solar cell part. First-pass CAD exists for the wheel, the body and its T-slot chassis, solar cells, mast, drive motors and suspension, with checks that the parts fit and clear each other. There is an electronics and actuator shortlist, a mass budget and a parts list skeleton. Everything is a first pass: each spec says what is sourced and what is a guess. Joints, fasteners, panel fixing and most wiring are not designed.

## Goal
A rover that a person can build and afford, at the original's size (about 470 x 500 mm, 200 mm wheels, 700 mm tall with the mast up), that is recognisably Rashid and drives, pans and tilts a mast-mounted camera and shows a live camera view. The mast is fixed for now; stowing it is deferred. The mass target is the original's 10 kg: the first pass is sized for 10 kg without optimising weight (the first estimate is about 9 kg, mostly guesses), and a second pass trims the build to 10 kg if the real parts come out over.

**Matched to the original where the sources allow:** the wedge body with 10 degree sides, the skeletonized grouser wheels, the 5 x 3 solar cell fields on both sloped faces, the mast and its camera head, and the overall envelope. Where a dimension is known, it is used and cited; where it isn't, the choice is labelled as an assumption.

**Free to differ:** materials, internal structure, motors, electronics and battery (off-the-shelf parts). The original is a flight vehicle in magnesium alloy; the replica is a T-slot aluminium frame with sheet panels. Out of scope for now: stowing the mast. Out of scope: flight qualification, thermal and vacuum fidelity, and the science instruments.

For reference, the primary sources (MBRSC conference material and the instrument teams' *Space Science Reviews* papers) give a 10 kg rover, 470 x 505 mm in plan and 700 mm tall with the mast deployed, on four wheels of 200 mm diameter and about 80 mm width. Each dimension in this repo cites its source or is marked unverified, and open conflicts are listed alongside.

This is an independent hobby project, not affiliated with or endorsed by MBRSC.

## What's here
| Path | Contents |
|---|---|
| [`docs/`](docs/original-dimensions.md) | Sourced record of the original's dimensions, with a source tag and status on every value. The replica's specifications: [wheel](docs/wheel-spec.md), [drive](docs/drive-spec.md), [suspension](docs/suspension-spec.md), [chassis](docs/frame-spec.md), [body interior](docs/interior-spec.md), [mast](docs/mast-spec.md), [solar cells](docs/solar-spec.md). Also an [electronics shortlist](docs/electronics-spec.md), a [mass budget](docs/mass-budget.md) of the original, and a [parts list skeleton](docs/bom.md) |
| [`graphic-design/`](graphic-design/README.md) | Square Kufic wordmark and an Earthset mosaic poster, plus the Python scripts that generate them |
| [`hardware/`](hardware/) | Parametric CAD (build123d, STEP output) with built-in fit checks: [wheel](hardware/wheel/wheel.py), [body envelope](hardware/body/body.py) and [interior](hardware/body/interior.py), [drive motor mounting](hardware/drive/motor.py), [suspension](hardware/suspension/arms.py), [mast](hardware/mast/mast.py), [T-slot chassis](hardware/chassis/frame.py), [solar provisions](hardware/solar/solar.py), and the [mass budget script](hardware/mass/budget.py) |

## Running the CAD
```
python3 -m venv .venv
.venv/bin/pip install -r hardware/wheel/requirements.txt     # build123d
.venv/bin/python hardware/chassis/frame.py                   # or any script above
```
Each script prints its checks (fits, clearances, masses) and writes STEP files to an `out/` folder beside it. The scripts import one another (the body model builds the mast, the chassis builds on the interior), so run them from the repository root.

## Regenerating the graphics
```
pip install -r requirements.txt
python3 graphic-design/scripts/build_wordmark.py            # wordmark SVG
cd graphic-design/scripts/mosaic && python3 header.py edge-coarse   # README header
```
Details and the other scripts are in [`graphic-design/README.md`](graphic-design/README.md).

## For builders
Cutting silicon cells is how the replica's solar panels are made. The how-to
[How to Split a Solar Cell Into Two](https://www.instructables.com/How-to-Split-a-Solar-Cell-Into-Two/) (Instructables; the same-titled
article on [The DIY Life](https://www.the-diy-life.com/how-to-split-a-solar-cell-into-two/) describes a craft-knife score and snap, cutting
parallel to the cell's tabs so each piece keeps them) is a good starting point. Cells are fragile and break often: buy at least twice the
number you need and cut a spare first. Our notes, with the wiring, the yield and the caveats, are in [`docs/solar-spec.md`](docs/solar-spec.md).

## Contributing
Corrections to Rashid's dimensions are the most valuable contribution, ideally with a primary source (MBRSC material, mission documentation, or photographs with known scale). The most useful missing facts are listed in section 7 of [`docs/original-dimensions.md`](docs/original-dimensions.md). Arabic readers' feedback on wordmark legibility is also wanted.

## License model
- **Code** (scripts, firmware, tooling) is licensed under **Apache-2.0** (see [`LICENSE`](LICENSE)).
- **Hardware designs, mechanical documentation and bills of materials** are licensed under **CERN-OHL-S-2.0**, strongly reciprocal (see [`LICENSE-HARDWARE.txt`](LICENSE-HARDWARE.txt)).
- **Graphics and other documentation** (wordmark, poster, headers, READMEs) are licensed under **CC BY 4.0** (see [`LICENSE-DOCUMENTATION.txt`](LICENSE-DOCUMENTATION.txt)).

Unless otherwise noted, files are licensed according to the category they fall under. Third-party material, including the NASA photographs, is not covered by these licences; see [`NOTICE.md`](NOTICE.md).
