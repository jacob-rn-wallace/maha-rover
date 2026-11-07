<p align="center">
  <img src="graphic-design/headers/almaha-header-edge-coarse.svg" alt="al-maha: a crescent Earth beside the Moon as a 15-degree trapezoid mosaic, with the al-maha Kufic wordmark between them" width="100%">
</p>

# المَهَا (al-maha)

An open-source, full-size replica of the UAE's **Rashid** lunar rover. It aims to look like the original and work roughly the way it does, in the spirit of Sawppy or the Beatty sisters' rover replicas, and to follow the original's dimensions wherever they are known.

*Al-maha* (المَهَا) is the Arabian oryx, and also the word for the oryx's eyes in classical Arabic poetry.

> **Status: early.** Branding is done. The original's dimensions are recorded with sources in [`docs/original-dimensions.md`](docs/original-dimensions.md); most outer dimensions are sourced (wheels, plan, height, stowed envelope, sidewall angle, cell grid), and gaps remain in the suspension and drivetrain layout and the exact solar cell part. CAD exists for the wheel, the body, solar cells and mast (as a dimensional envelope), the drive motor mounting and the suspension. There is a mass budget and a skeleton parts list. Nothing has been built yet. Everything below says what exists and what doesn't.

## Goal
A rover that a person can build and afford, at the original's size (about 470 x 500 mm, 200 mm wheels, 700 mm tall with the mast up), that is recognisably Rashid and drives, deploys a mast and shows a live camera view.

**Matched to the original where the sources allow:** the wedge body with 10 degree sides, the skeletonized grouser wheels, the 5 x 3 solar cell fields on both sloped faces, the stowing and deploying mast, and the overall envelope. Where a dimension is known, it is used and cited; where it isn't, the choice is labelled as an assumption.

**Free to differ:** materials, internal structure, motors, electronics and battery (off-the-shelf parts), and mass. The original is a 10 kg flight vehicle in magnesium alloy; the replica is not. Out of scope: flight qualification, thermal and vacuum fidelity, and the science instruments.

For reference, the primary sources (MBRSC conference material and the instrument teams' *Space Science Reviews* papers) give a 10 kg rover, 470 x 505 mm in plan and 700 mm tall with the mast deployed, on four wheels of 200 mm diameter and about 80 mm width. Each dimension in this repo cites its source or is marked unverified, and open conflicts are listed alongside.

This is an independent hobby project, not affiliated with or endorsed by MBRSC.

## What's here
| Path | Contents |
|---|---|
| [`docs/`](docs/original-dimensions.md) | Sourced record of the original's dimensions, with a source tag and status on every value; the replica's [wheel](docs/wheel-spec.md), [drive](docs/drive-spec.md) and [suspension](docs/suspension-spec.md) specifications; a [mass budget](docs/mass-budget.md); a [parts list skeleton](docs/bom.md) |
| [`graphic-design/`](graphic-design/README.md) | Square Kufic wordmark and an Earthset mosaic poster, plus the Python scripts that generate them |
| [`hardware/`](hardware/) | Parametric CAD (build123d, STEP output): [wheel](hardware/wheel/wheel.py), [body envelope](hardware/body/body.py), [drive motor mounting](hardware/drive/motor.py), [suspension](hardware/suspension/arms.py), and the [mass budget script](hardware/mass/budget.py) |

## Regenerating the graphics
```
pip install -r requirements.txt
python3 graphic-design/scripts/build_wordmark.py            # wordmark SVG
cd graphic-design/scripts/mosaic && python3 header.py edge-coarse   # README header
```
Details and the other scripts are in [`graphic-design/README.md`](graphic-design/README.md).

## Contributing
Corrections to Rashid's dimensions are the most valuable contribution, ideally with a primary source (MBRSC material, mission documentation, or photographs with known scale). The most useful missing facts are listed in section 7 of [`docs/original-dimensions.md`](docs/original-dimensions.md). Arabic readers' feedback on wordmark legibility is also wanted.

## License model
- **Code** (scripts, firmware, tooling) is licensed under **Apache-2.0** (see [`LICENSE`](LICENSE)).
- **Hardware designs, mechanical documentation and bills of materials** are licensed under **CERN-OHL-S-2.0**, strongly reciprocal (see [`LICENSE-HARDWARE.txt`](LICENSE-HARDWARE.txt)).
- **Graphics and other documentation** (wordmark, poster, headers, READMEs) are licensed under **CC BY 4.0** (see [`LICENSE-DOCUMENTATION.txt`](LICENSE-DOCUMENTATION.txt)).

Unless otherwise noted, files are licensed according to the category they fall under. Third-party material, including the NASA photographs, is not covered by these licences; see [`NOTICE.md`](NOTICE.md).
