<p align="center">
  <img src="graphic-design/headers/almaha-header-edge-coarse.svg" alt="al-maha: a crescent Earth beside the Moon as a 15-degree trapezoid mosaic, with the al-maha Kufic wordmark between them" width="100%">
</p>

# المَهَا (al-maha)

An open-source replica of the UAE's **Rashid** lunar rover, built to match the original's dimensions as faithfully as possible.

*Al-maha* (المَهَا) is the Arabian oryx, and also the word for the oryx's eyes in classical Arabic poetry.

> **Status: early.** Branding is done. The rover engineering has not started: the original's dimensions still need to be sourced, and there is no CAD or BOM yet. Everything below says what exists and what doesn't.

## Goal
Reproduce Rashid (MBRSC, Dubai) at the original's dimensions. Press reports give roughly 10 kg, 50 x 50 cm and four wheels. Those are secondary figures and will be replaced by primary sources as they are found. Each dimension in this repo should cite its source or be marked unverified.

This is an independent hobby project, not affiliated with or endorsed by MBRSC.

## What's here
| Path | Contents |
|---|---|
| [`graphic-design/`](graphic-design/README.md) | Square Kufic wordmark and an Earthset mosaic poster, plus the Python scripts that generate them |
| `hardware/` | *Not yet created.* Planned home for CAD, drawings and the BOM |

## Provisional design notes
Early planning (a 15 degree wedge body around a 6U CubeSat envelope, 200 x 80 mm wheels, rocker suspension with Ackermann steering) came from brainstorming before the project became a faithful replica. It is **unverified against the original** and will be overridden wherever it conflicts with real Rashid dimensions.

## Regenerating the graphics
```
pip install -r requirements.txt
python3 graphic-design/scripts/build_wordmark.py            # wordmark SVG
cd graphic-design/scripts/mosaic && python3 header.py edge-coarse   # README header
```
Details and the other scripts are in [`graphic-design/README.md`](graphic-design/README.md).

## Contributing
Corrections to Rashid's dimensions are the most valuable contribution, ideally with a primary source (MBRSC material, mission documentation, or photographs with known scale). Arabic readers' feedback on wordmark legibility is also wanted.

## Licence
Code is MIT, hardware design files are CERN-OHL-P-2.0, and graphics and documentation are CC BY 4.0. See [`LICENSE.md`](LICENSE.md) for the breakdown and third-party notices, including the NASA photo credit.
