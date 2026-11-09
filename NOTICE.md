# Licensing and notices

maha-rover uses a split-license model, the same as megadroid. Unless otherwise noted, files are licensed according to the category they fall under.

| What | Licence | File |
|---|---|---|
| Code: scripts, firmware, tooling (`graphic-design/scripts/`, future `firmware/`, `software/`) | Apache-2.0 | [`LICENSE`](LICENSE) |
| Hardware: CAD, drawings, schematics, mechanical documentation, bill of materials (future `hardware/`) | CERN-OHL-S-2.0 | [`LICENSE-HARDWARE.txt`](LICENSE-HARDWARE.txt) |
| Graphics and other documentation: wordmark, poster, headers, social preview, READMEs | CC BY 4.0 | [`LICENSE-DOCUMENTATION.txt`](LICENSE-DOCUMENTATION.txt) |

## Third-party material
- NASA / Artemis II photographs, April 6, 2026, credit "NASA". NASA media is generally not copyright-restricted, but
  these images are **not** covered by the licences above. Files in `graphic-design/source-photos/`:
  - `art002e009288orig.jpg`: "Earthset", https://www.nasa.gov/image-detail/art002e009288/
  - `art002e009285~large.jpg`: "The Edge of Two Worlds", https://www.nasa.gov/image-detail/amf-art002e009285/
  - `art002e021110~large.jpg`: "Capturing the Details of the Moon and the Beauty of Earth", https://www.nasa.gov/image-detail/amf-art002e021110/
  - `art002e021219~large.jpg`: "Earthset on the Far Side", https://www.nasa.gov/image-detail/amf-art002e021219/
- Lunar terrain for the simulation, `sim/public/terrain/atlas_5km.png` and `.json`: a 5 x 5 km window cut from the LROC NAC digital terrain model NAC_DTM_ATLAS_E468N0446
  (Arizona State University, 2012; the elevation values, rescaled to 16 bit; no other change). The LROC team states that data products on the LROC Data Node of the PDS and the NASA PDS interfaces are in the
  public domain (https://lroc.im-ldi.com/about/terms, read 2026-11-08); the file came from pds.lroc.im-ldi.com. Credit as the LROC team asks: NASA/GSFC/Arizona State University. Reference: Henriksen et al., Icarus (2016),
  doi 10.1016/j.icarus.2016.05.012. Not covered by the licences above.
- Lunar terrain ring for the simulation, `sim/public/terrain/ring.png`, `ring_mask.png`, `ring.json` and `docs/images/viewshed-ring-preview.png`: heights resampled from the LROC Atlas DTM above and from the LOLA gridded map LDEM_128 (NASA/GSFC, PDS Geosciences Node), with a computed visibility mask.
  The LOLA archive's own terms of use have not been read yet (the hand-off records this): confirm that they allow redistribution of derived heights before the site is published.
- The poster, headers and social preview are derivatives of those photographs; only the original mosaic and wordmark layout is under CC BY 4.0.
- "Rashid" and the Emirates Lunar Mission marks belong to MBRSC / UAE entities. This is an independent,
  unofficial replica and is not affiliated with or endorsed by MBRSC. The al-maha wordmark is original and
  does not reproduce the official mission logo.
