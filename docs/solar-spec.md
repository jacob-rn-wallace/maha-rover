# Solar cells: provisions for real cells (replica)

The replica's side panels carry silicon cells in the original's 5 x 3 grid. This is the specification of the current design, then the record
of how it was reached. **Where a later section conflicts with "Current design", the current design wins**; the sections after it are history
and comparison. CAD and checks: `hardware/solar/solar.py` and `hardware/body/body.py`; mockups: `docs/images/solar-cell-mockups.png`.
Everything is ASSUMPTION unless tagged; cell figures are the retailer's and have not been measured.

## Current design (decided 2026-11-07): tiled back-contact pieces, two per slot, buck module

- **Cells:** SunPower-type back-contact silicon (no front busbars: the front is uniformly dark blue-black, as the AnySolar modules look).
  Buy third-cut strips, 125 x 41.6 mm (LinkSolar lots of 20 at US$16.96, which may be a listing error; else full 125 mm cells at US$43.60 for 10 and cut
  thirds). Cut each strip in four: **31 x 41.6 mm pieces, 60 in all, 30 per side**. About 15 strips with no breakage; buy 30.
- **Layout:** the original's 5 x 3 slots, columns on its 71.6 mm pitch, rows at 42.5 mm (the strips are 41.6 mm tall); two pieces per slot, 0.5 mm apart
  (slot width 62.5 mm). The field spans z 192.7 to 317.3 against the original's 196 to 314 (3k). Pieces are plain rectangles 0.8 mm thick (piece,
  adhesive and a clear laminate over it).
- **Electrical (retailer's full-cell figures, 0.625 V and 6.05 A, scaled by piece area):** a piece is 0.625 V, 0.51 A, 0.32 W at one sun; **30 in series per side
  is 18.75 V, 0.51 A, 9.6 W** (three rows of ten at 6.25 V). Voc is assumed 0.70 V a cell: 21.0 V at 25 C, 23.7 V at -20 C (under a buck module's
  28 V, and under the 24 V the listings recommend). Vmp is about 17.3 V on a panel 25 K hotter.
- **Charger:** a cheap buck 2S MPPT module, BQ24650 or CN3722 type (`charger-board-spec.md`): US$11 to 17. The string is well above the pack's 8.4 V.
  Set its input set point near 17.5 V, between the cold and hot Vmp. Two Schottky blocking diodes (one per side) join the sides at the module's input.
- **Assembly:** tab the pieces on the rear (back-contact cells have both polarities there) into rows of ten, bond them to the panel and put a clear
  laminate or coat over them; each row's two ends come inside through the 5 mm holes. Cutting back-contact cells is the hard part: see the cutting
  notes below.
- **Holes:** **12 holes of 5 mm per rover, 6 per side panel**, at x = plus or minus 160.2, one at each end of each row, under the end piece, at the row's
  centre height (z 213, 255, 297). Nothing in the frame lies within 1 mm of a hole's edge, 14 mm deep; the posts are 5.3 mm from the hole edges.
  The real pieces' rear contact positions are not known until a sample arrives, so the holes may move.
- **Wiring:** one series string per side as a serpentine through the six holes: row 1 rear (-) to row 1 front, jumper A (55 mm with slack) to row 2 front,
  row 2 to its rear, jumper B (55 mm) to row 3 rear, row 3 to its front (+). Terminal boards (20 x 8 x 100 mm, one per post, z 205 to 305, on the posts'
  cavity-facing faces; no clashes) hold the jumpers and leads: the front board takes jumper A and the (+) lead, the rear board jumper B and the (-) lead;
  each hole wire is about 31 mm. Leads to the charger: left side 432 mm (-) and 301 mm (+), right side 370 mm (-) and 220 mm (+), 24 AWG; 0.51 A over 1.1 m
  of lead pair drops 0.05 V of 18.8 V.
- **Cost:** about **US$34 to 44 for the cells and US$11 to 17 for the charger: US$45 to 61**, against US$430 to 510 for AnySolar.
- **Not designed:** protection (a fuse in each side's plus lead, bypass diodes per row), the clear laminate, how pieces are held while tabbing, the
  connector between the boards and the charger.
- **Open:** the authenticity of "Maxeon-style" cells from marketplaces, the real pieces' rear pad layout, the true Voc and temperature coefficient, and a
  working cutting method (see the cutting sections below). Buy a few cells first and measure them under a lamp.

Fallbacks, in order: the Futurlec SZGD6030 (US$45, needs the US$156 buck-boost evaluation board), then the one-piece-per-slot tiling.

## Earlier decision: AnySolar (2026-11-07, superseded by the current design above)

**Status: superseded. The owner found the AnySolar price (US$415 to 490 for 30 modules) too high and chose the tiled pieces (current design above).**
The text that follows records the AnySolar decision as made.

The **AnySolar SM261K10TF was chosen as the primary cell**; the Futurlec SZGD6030 below is the fallback.

- **Module:** SM261K10TF, 64 x 45 x 1.2 mm (DigiKey lists 1.5 mm), 5.9 g, ten monocrystalline cells laminated in a 5 x 2 grid,
  25 percent efficiency. Datasheet (Rev. May 2021, typical values at one sun, AM1.5, 25 C): Voc 6.91 V, Isc 109 mA,
  **Vmpp 5.58 V, Impp 102 mA, Pmpp 571 mW**, fill factor above 70 percent, Voc -17.4 mV/K. Plain, no cover or outline.
- **Layout:** the original's 5 x 3 positions: columns on the original's 71.6 mm pitch (7.6 mm gaps), rows at 46 mm instead of 41 so
  the 45 mm modules clear (1 mm gaps). The field spans z 187.5 to 322.5 against the original's 196 to 314 (3k); the lowest row's
  grouser-tip overlap with the wheels is slightly larger than in the original.
- **Solder pads on the back:** each module has its two solder terminals on the BACK face, 22 mm either side of its centre at mid
  height (datasheet drawing; "+" is 10 mm from one end). So the side panel is drilled behind every pad: **2 holes of 3.5 mm per
  module, 30 per side, 60 in all**; the wires are soldered to the pads through the holes and the modules are bonded to the panel.
  The modules are mounted with "+" toward the front on both walls.
- **Soldering:** the laminate (EVA and polymer film) must not be reflowed. The datasheet allows hand soldering at under 260 C for 2 s,
  or an oven-cured silver paste (it names LORD PC10678HV) at 100 C for 30 minutes.
- **Wiring:** three modules in series per column (rows 1 to 3), the five columns in parallel: **Vmpp 16.74 V, Voc 20.73 V, 0.51 A,
  8.5 W per side** at one sun (STC). The string is above the pack's 8.4 V, so a buck charger works.
- **Charger:** with 16.7 V in, a cheap buck 2S MPPT module (5 to 28 V in) is now an option, as well as the BQ25798 (24 V input limit):
  Voc rises with cold, to 22.0 V at 0 C and 23.1 V at -20 C, inside both limits. See `charger-board-spec.md`.
- **Cost:** DigiKey lists the TF part at US$16.32 each, US$13.84 at 10 and US$10.58 at 500, 12 weeks' lead time, 93 in stock when
  seen (the L part, 1.8 mm, is out of stock and its listing differs): 30 modules cost about **US$415 to 490**, against about US$45 for
  the Futurlec cells.
- **Check and numbers:** `hardware/solar/solar.py`; mockup: `docs/images/solar-cell-mockups.png`.

The earlier decision (Futurlec, plain, fallback) and the material below it still stand as the fallback; the "Built in" and "Wiring"
sections below describe the **Futurlec layout** (12 holes per panel between the rows) and no longer match the CAD, which now drills behind
the SM261K10 pads. The section "Wiring and pads for the SM261K10" gives the primary layout.

### Tiling back-contact pieces for the same look (2026-11-07, research)

**What the AnySolar look is.** The SM261K10's front (datasheet drawing) is ten cells in a 5 x 2 grid of 0.3 to 0.78 mm gaps and no
visible contacts; the solder pads are on the back. A conventional silicon cell cannot match that, because it carries silver busbars and
fingers on the front. A **back-contact cell** (the SunPower "C60/E60/Maxeon" type) has no front metal, so the front is uniformly dark
blue-black, and tiles of it with small gaps would look like the AnySolar module. (Whether the Futurlec cell has front contacts was not
found; its page says only "black".) That AnySolar's own cells are back-contact was not confirmed: its Gen3 table has an "S" suffix for rear
pad position, and the datasheet drawing shows rear pads.

**What is on sale.**
- LinkSolar (a small retailer): 125 mm SunPower-type IBC cells, full, 1/2, 1/3 and 1/6 cuts stocked; full cells US$43.60 for 10 (US$4.36
  each), half cuts US$50.32 for 10, a 1/3-cut lot of 20 at US$16.96 (about US$0.85 each; it may be a listing error: verify). Full cell
  3.78 W, 0.625 V, 6.05 A at standard conditions, as read from their guide ([product page](https://linksolar.net/products/sunpower-solar-cells-125mm-cut)).
- Alibaba: 1/3-cut cells, **125 x 41.6 mm**, 24.8 percent, US$0.60 to 0.70 each, minimum 300 pieces (about US$198); generic
  "Maxeon-style" listings whose authenticity was not checked ([example](https://www.alibaba.com/product-detail/sunpower-maxeon-gen-3-Solar-Cells_1700003963864.html)).
- Retail 10-packs of C60/E60 full cells at about US$3.80 to 7 each (earlier notes).

**Two layouts** (arithmetic from LinkSolar's full-cell figures scaled by area, so unverified; one side = 15 slots):

| | One piece per slot | Two pieces per slot |
|---|---|---|
| Piece | 62.5 x 41.6 mm (a 1/3-cut strip cut in half) | 31 x 41.6 mm (a strip cut in four) |
| Pieces per side | 15 | 30 |
| Per piece | 0.63 W, 0.625 V, about 1.0 A | 0.31 W, 0.625 V, about 0.5 A |
| One series string per side | 9.4 V, 1.0 A, about 9.5 W | 18.8 V, 0.5 A, about 9.5 W |
| Charger | still below a safe buck margin (9.4 V against 8.4 V): a buck-boost | buck is enough (but Voc, near 21 V, rises to about 24 V at -20 C: at the BQ25798's limit) |
| Pieces per full cell | 6 | 12 |
| Cells per side, with no breakage | 2.5, so 3 | 2.5, so 3 |

Rows would sit at 42.5 mm pitch (the strips are 41.6 mm tall); columns at the original 71.6 mm. Output is about the AnySolar's 8.5 W a side.

**Cost.** About US$13 to 30 per pair of sides at the retail cell prices, or about US$34 for 40 pre-cut strips from the 1/3-cut lot if the
price is real, and double for breakage: **roughly US$30 to 100 for both panels, against US$415 to 490 for AnySolar**.

**Caveats.**
- Back-contact cells are the hard ones to cut: a heavy copper backing, an interdigitated rear pattern, and each piece must keep access
  to both polarities (see the cutting cautions above). Pre-cut 1/3 strips remove two of the cuts; the strips still have to be halved.
- Each piece needs wires on its back: either soldered to the rear contacts and brought through the panel (as for the AnySolar) or
  carried on a backing. The pad positions depend on the cell, so the holes cannot be drilled until a cell is chosen; drill them with a jig after
  the pieces are laid out.
- The authenticity and grading of "Maxeon-style" cells from marketplaces is not checked.
- Clipped corners: only the pieces from the outer thirds of a pseudo-square cell have one; the middle strip has none.
- The look needs gaps of under 1 mm and, as with the AnySolar module, a clear laminate or coat over the pieces; nothing here has
  been built or photographed.

### Cheapest total (cells and charger, no custom board), 2026-11-07

Prices seen, not quoted orders; both panels (30 slots) unless noted. Charger prices: the LaskaKit CN3722 module is EUR 10.19 (sold out, restock
date given), ended eBay listings for BQ24650 modules showed US$17.10 and EUR 11.88 (so about US$11 to 17); the BQ25798EVM is US$156.45 on TI's page
(availability unclear). Two Schottky blocking diodes (one per side) and wire are about the same in every option and not priced.

| Route | Cells | Charger | Total |
|---|---|---|---|
| **Tiled back-contact pieces, 2 per slot (18.8 V per side), with a cheap buck module** | **US$34 to 44** (15 third-cut strips needed, 30 with a margin for breakage: two LinkSolar lots of 20 at US$16.96 if that price is real, else 10 full cells at US$43.60) | **US$11 to 17** (BQ24650 or CN3722 buck module) | **about US$45 to 61** |
| Tiled pieces, 1 per slot (9.4 V per side), direct charge through a diode and the BMS | US$34 to 44 | about US$0 (a diode) | about US$35 to 45, but gives up 12 to 37 percent of the energy and needs the BMS to tolerate the panel's open-circuit voltage |
| Tiled pieces, 1 per slot, with the BQ25798EVM | US$34 to 44 | US$156 | about US$190 to 200 |
| Futurlec, 60 x 30 mm (7.2 V per side), with the BQ25798EVM | US$40 to 45 | US$156 | about US$196 to 201 |
| AnySolar SM261K10TF (16.7 V per side), with a buck module | US$415 to 490 | US$11 to 17 | about US$430 to 510 |

**Cheapest route that keeps a proper charger: tiled back-contact pieces, two per slot, with a cheap BQ24650 or CN3722 buck module, about
US$45 to 61.** The string (30 pieces per side in series, about 18.8 V at maximum power) is well above the pack, so a buck module works,
and Voc stays inside a 28 V buck module's limit even cold (about 24 V at -20 C by my estimate; the BQ25798's 24 V would not).
It costs a seventh to a tenth of the other routes that have a real charger. What it takes: cutting each third-cut strip into four
31 x 41.6 mm pieces, and wiring 60 pieces. Futurlec and the single-piece tiling both need a buck-boost, and the cheapest off-the-shelf one found
is the US$156 evaluation board, which is why they cost four times as much. A cheaper buck-boost was not found (the ZK-4KX has no MPPT and its price was not found).

### Wiring and pads for the SM261K10 (superseded: price)

Hole ids in `solar.py`: side L or R, column 0 to 4 rear to front, row 0 to 2 bottom to top, pad + or -.

- **Series within a column:** the + pad of the row-j module joins the - pad of the row-(j+1) module above it, behind the panel: ten
  jumpers per side, each about 83 mm of 24 AWG wire with slack (the straight run is 64 mm).
- **Buses:** the - pads of row 0 (bottom) are joined by a bus wire behind the panel, and so are the + pads of row 2 (top); each bus is
  about 370 mm with slack. Both buses end at a terminal board on the front post (20 x 8 x 110 mm, z 200 to 310, clear of the frame
  and contents; modelled in `solar.py`). The outermost holes (the + pad of the front column and the - pad of the rear column, at
  x = plus or minus 165.2) are 1.1 mm from the post's inner face, so wires there leave away from the post.
- **Leads:** from the board to the charger about 180 mm (right) or 260 mm (left); an array current of 0.51 A over 1 m of 24 AWG
  pair drops 0.04 V of 16.7 V. A blocking diode per side joins them at the charger, as before (one side lit at a time).
- **Clearance:** nothing in the frame, standoffs or plates lies within 2.25 mm of a hole's axis, 14 mm deep; the mid rail ends at
  z 185, 24 mm below the lowest pad holes; the top rail starts at z 325, above the top row's holes.
- **Not designed:** how the 60 wires are held behind the panel, a harness for them, protection (fuses, bypass diodes per module
  or column), and the blocking diodes' parts.
- **Voltage limit:** the charger input limit (24 V for the BQ25798) is within 1 V of the string's Voc at -20 C; do not exceed a column
  of three modules in series.

## Silicon: cutting is established practice (2026-11-07)

Background for a build with cut cells; not used by the decided Futurlec build above.

Cutting is established practice, in industry and among hobbyists:
- **Industry:** half-cut cells are a standard format; laser cut-and-cleave is the usual method. Cutting leaves
  unpassivated edges that lower open-circuit voltage; the loss is about 1.2 percent of fill factor before edge
  passivation in one study and about 0.1 percent with an optimised thermal laser separation process in another (lab and
  pilot studies, not one benchmark; higher-efficiency cells lose more) ([pv magazine](https://pv-magazine.com/2021/10/09/the-weekend-read-half-cut-solar-cells-on-edge), [TU Delft](https://repository.tudelft.nl/file/File_867bbb9d-ee6d-4abe-88e9-a94e0b4430a9?preview=1)).
- **Hobbyists:** a university solar-car team cut SunPower back-contact cells into thirds with a fiber laser marker,
  found the settings by trial and error, snapped the pieces apart by hand and estimated about 1 percent loss; an
  Instructables guide and forums describe scoring a bare cell and snapping it; PowerFilm reports a cell cut in three
  gave about 89 percent of its power when the pieces were recombined ([DIY guide](https://www.the-diy-life.com/how-to-split-a-solar-cell-into-two/), [PowerFilm](https://blog.powerfilmsolar.com/education/the-horizon-blog/2018/11/30/whole-cells-vs-cut-cells-whats-the-difference), [forum](https://diydrones.com/forum/topics/breaking-solar-cells-into-pieces)).

Cautions found, none of them showstoppers:
- Only bare cells can be cut; a laminated cell cannot.
- SunPower back-contact cells have a heavy copper backing and an interdigitated rear pattern, which make cutting harder,
  and each piece must keep access to both polarities. Their warranty covers whole cells only. A cut cell can lose fill
  factor badly if cut badly (one example fell to about 15 percent efficiency).
- Forum opinion is split on whether micro-cracks from a home cut spread over time; factory cuts are annealed.
- Scoring with a disc glass cutter was reported to crack cells; a hard scribe or a laser is better.
- No published breakage rate was found for home cutting, so the cost estimate's doubling is a guess.

Practical steps: buy spares (at least twice the cells needed), cut test pieces first, check the rear contact layout of the
chosen cell before cutting, and measure the cut pieces' voltage and current under a lamp. Choosing a conventional
front-and-back-contact cell instead of a back-contact one avoids the rear-pattern difficulty; this was not compared in detail.

## Which cell (open)

The yields above assume a cell can be cut anywhere. Real cells constrain the cuts, so the cell product matters:
- **Conventional front-and-back-contact cells** carry two or three full-width busbars (tabs) on the front. A cut piece must keep a
  segment of a busbar for each polarity: the how-to below says to cut parallel to the tab lines so each piece keeps full tabs.
  Cutting a three-busbar cell into three strips parallel to the busbars and then across them keeps a busbar on every piece, but
  the strips are about 41 mm wide and 125 mm long, so a strip gives one full 69 mm piece plus a short one: about 3 full pieces
  per cell rather than 4, which would make 5 cells per side. This reasoning is mine, not from a source.
- **Back-contact cells** (the C60 class) have all contacts on the rear, in an interdigitated pattern and with a heavy copper
  backing; cutting them is harder and each piece must keep access to both polarities (see the cautions above), and Gen III is
  no longer made.
- **Pre-cut candidate:** the 156 x 60 mm laser-cut cell (0.55 V, 2500 mA) is already cut, but only gives 2 pieces of 69 x 39 mm.

Choosing the cell is the next decision: look for a conventional mono cell near 125 to 156 mm with its busbar spacing and
purchase price, then recompute the pieces per cell.

## Search for cells that need one cut or none (2026-11-07)

Looked for silicon cells that give the 69 x 39 mm outline by cutting in half, or already have clipped corners.

**No such cell was found.** A half of a standard cell is far larger than 69 x 39 mm (125 x 125 gives 125 x 62.5; 78 x 78 gives
78 x 39, 9 mm too long; 156 x 156 gives 156 x 78). A half that is 69 x 39 mm would need a parent cell of about 69 x 78 or
138 x 39 mm, which was not found on sale. On clipped corners: a pseudo-square cell has four clipped corners, so a half cut
across its middle keeps two on one long edge, like the original's half-wafer cells (my geometry, not a source); that only
helps if the half is the right size.

Nearest products found (retailer pages; none states corner clips):

| Product | Size | Rating | Cuts needed | Fit |
|---|---|---|---|---|
| Futurlec SZGD6030, mono, black | 60 x 30 x 2.8 mm | 0.48 V, 280 mA, 17 percent; Isc 302 mA; test light not stated; US$1.50 each, US$1.35 from 25, US$1.20 from 100 | none | 4.5 mm smaller than the outline on every side (the F2 5 mm class); 2.8 mm thick against the 1.0 mm stack, so it stands 1.8 mm proud |
| Conrad 19 12 93, mono | 96 x 66 mm, 24 g | 0.5 V, 800 mA (2008 datasheet) | one cut across the long side gives 66 x 48 mm | 3 mm short and 9 mm too tall; the datasheet forbids modifying the product "for safety reasons"; availability not checked |
| Silicon Solar laser-cut cell | 156 x 60 mm | 0.55 V, 2500 mA | one cut gives 78 x 60 mm | 9 mm long and 21 mm tall; no good |

([Futurlec](https://futurlec.com/solar/szgd6030.shtml), [Conrad datasheet](https://asset.conrad.com/media10/add/160267/c1/-/gl/000191293DS01/tehnicni-podatki-191293-conrad-components-yh-66x96-solarni-modul.pdf))
The Silicon Solar 0.55 V, 200 mA cell page returned an error and was not read.

**New option F4: Futurlec SZGD6030, no cutting.** 15 per side, 30 in all, about US$40 to 45. Wired as the serpentine: 7.2 V
(15 x 0.48 V), which the BQ25798's 3.6 to 24 V input accepts. Output is uncertain because the test light is not stated:
at the listed 280 mA it is 2.0 W a side; if that rating is at one sun, 17 percent of 18 cm2 would give about 0.64 A and
about 4.6 W a side (my arithmetic). The 2.8 mm thickness suggests an encapsulated cell on a substrate, which also means the
pieces cannot be cut. It needs the border and the printed cover of F2 to look like a 69 x 39 mm cell.

**Another route, not off the shelf:** cut a 125 mm cell into six pieces of about 60 x 40 mm (2 across, 3 down; 40 mm is 1 mm
over the 39 mm cell height), so three cells a side. Two more cuts per cell than F1 would need, but all parallel or
perpendicular to the busbars, and only the four corner pieces would have a clipped corner.

## AnySolar modules close to 69 x 39 mm (2026-11-07)

Checked AnySolar's full Gen3 list ([anysolar.biz/Gen3](https://anysolar.biz/Gen3): 83 standard 1.8 mm and 67 thin 1.2 mm parts, all
listed at 25 percent cell efficiency) and the Gen2 list ([anysolar.biz/Gen2](https://anysolar.biz/Gen2)). AnySolar sells
monocrystalline **modules of several cells in series**, not single cells, so the voltage is 0.69 V times the cell count (Voc).
**No part is 69 x 39 mm.** The closest, by size:

| Part (standard 1.8 mm / thin 1.2 mm) | Size (mm) | Cells in series | Voc | Pmax (listed) | Against the 69 x 39 slot |
|---|---|---|---|---|---|
| SM261K10L / SM261K10TF | 64 x 45 | 10 | 6.91 V | 571 mW | 5 mm short, 6 mm tall: the best match by shape and area (28.8 against 26.9 cm2), but 4 mm taller than the 41 mm row pitch |
| SM141K10L / SM141K10TF | 70 x 23 | 10 | 6.91 V | 307 mW | 1 mm long, 16 mm short in height; fits the slot, length exact |
| SM261K05L / SM261K05TF | 67 x 25 | 5 | 3.45 V | 285 mW | 2 mm short, 14 mm short in height |
| SM401K08L / SM401K08TF | 90 x 40 | 8 | 5.53 V | 702 mW | height right (40 against 39), 21 mm too long |
| SM351K09L / SM351K09TF | 57 x 64 | 9 | 6.22 V | 695 mW | too tall |
| SM531K08L / SM531K08TF | 89 x 52 | 8 | 5.53 V | 913 mW | too long and tall |

Other sizes near it are smaller (SM101K12L 45 x 32, SM141K10LV 45 x 36) or wider (SM531K10L 89 x 65). The thin (TF) parts are 1.2 mm
thick against 1.8 mm, and the Futurlec cell's 2.8 mm. Prices were not found (DigiKey's pages returned an error); the parts are
sold through DigiKey. One DigiKey listing gives a thickness of 1.50 mm for the SM811K08TF where AnySolar's table gives 1.2 mm.

What this changes if AnySolar were used instead of the Futurlec cells (my arithmetic from the listed values):
- **Output:** 15 x SM141K10 gives 4.6 W per side at the listed rating (one sun, presumably standard test conditions), at 25 percent
  efficiency; 15 x SM261K10 would give 8.6 W. The Futurlec build is 2 to 4.6 W with an unstated test light.
- **Voltage, so the charger:** each module is already 3.4 to 6.9 V open-circuit. Three SM141K10 in series (a column of 3) give
  about 20.7 V Voc and, taking Vmp at 0.81 of Voc as for the SM451K08L (4.46 V of 5.53 V), about 16.8 V; five columns in parallel
  per side would make the 5 x 3 grid one string per column. That is well above the pack's 8.4 V, **so a cheap buck 2S MPPT module
  (BQ24650 or CN3722 type, 5 to 28 V in) would work, with no buck-boost board** (the BQ25798's 24 V input limit would
  also hold, with 20.7 V Voc). It removes the charger problem in `charger-board-spec.md`.
- **Look:** each module shows several small cells in a row with the module's own outline; the module is 23 mm tall against the
  original's 39 mm cell, leaving 18 mm gaps above and below each in its slot, or one of the 64 x 45 parts nearly fills it.
- **Not checked:** each module's Vmp and Imp, its terminals (the datasheets would say), and price.

This is an alternative, not a change of decision: the Futurlec build stays unless chosen otherwise.

## For builders: cutting references

- **"How to Split a Solar Cell Into Two"**, Instructables ([link](https://www.instructables.com/How-to-Split-a-Solar-Cell-Into-Two/)).
  The page body could not be fetched here (only its title and its three-step structure came through), so it was not read. The
  same-titled article on The DIY Life by Michael Klements, 2016, was read
  ([link](https://www.the-diy-life.com/how-to-split-a-solar-cell-into-two/)); it appears to be the same guide, but that is not confirmed.
  Its method: lay the cell face down, lay a ruler along the line, run a sharp craft knife lightly and repeatedly along the ruler
  until the cell begins to part, then lift the ruler and break it along the line. It warns not to press hard, that cells are
  "extremely fragile", and to cut parallel to the tabs so each half keeps its full tabs; a half produces half the power at the
  same voltage. It gives no soldering advice and names no cell type; it is for small cells.
- Limits for this project: a craft-knife score is a hand cut, so expect ragged edges and a millimetre or two of error,
  which is why a 2 mm tolerance is accepted above; it describes cutting a cell in two, not into four pieces with clipped corners
  (the clips are not cut by it); and only bare, unlaminated cells can be cut. A fibre laser (as a university team used on
  SunPower cells) or a scribe cutter gives cleaner results than a knife, with no source for a breakage rate.

## Where the field sits on the wall (corrected 2026-11-07)

The model's cell field was centred on the wall (z 233.5), an assumption. A pixel scan of the original's side view ([S5] Fig. 15,
`original-dimensions.md` 3k) puts the cells at **z 196 to 314**, centre 255, so the field moved up 21.5 mm. With the old position the
lowest row sat well over the wheels in a side view (its bottom edge at 173 against the rim tops at 200); the original's bottom edge is at 196, just level with them. Hole rows, terminal boards and lead lengths below use the new
position.

## Fill options for silicon

Each cell position is 69 x 39 mm (the original's half-wafer size). From a 125 x 125 mm C60-class cell (2 mm edge margin,
0.5 mm saw kerf, a simple packing), one side's 15 positions need:

| Option | Piece | Active area | Pieces per cell | Cells per side | Output per side at one sun | Look from outside |
|---|---|---|---|---|---|---|
| F1. Full outline, "half-cut" | 69 x 39 mm, clipped corners | 26.5 cm2 | 4 | 4 | 8.7 V, 1.03 A, **9.0 W** | matches the original's cells |
| F2. Smaller real cells, inset 2 mm | 65 x 35 mm | 22.8 cm2 | 4 | 4 | 8.7 V, 0.88 A, **7.7 W** | a 2 mm dark border |
| F2. Smaller real cells, inset 5 mm | 59 x 29 mm | 17.1 cm2 | 8 | 2 | 8.7 V, 0.66 A, **5.8 W** | a 5 mm border |
| F3. Tiled small pre-cut cells | 52 x 19 mm, 2 per position | 19.8 cm2 (73 percent of the outline) | bought pre-cut, 100 to a pack | 60 pieces for both sides | listed: 15 V, 0.40 A, 6.0 W; one reviewer measured 2.7 W | two small cells inside each outline |

Output scales with area; the pieces' voltage is taken as 0.582 V and cutting losses are ignored. F3 uses the AOSHIKE-type
polycrystalline micro cells (listed 0.5 V and 400 mA, one reviewer measured 0.65 V and 140 mA, so treat 2.7 to 6 W as the
range); the other options use the C60-class entry. Wiring: F1 and F2 are one series string of 15 cells (8.7 V). F3 is
30 pieces in series (15 V at the listed rating, 20 V at the measured one) or 2 in parallel per position with 15
positions in series (7.5 V, 0.8 A listed).

Trade-offs:
- **F1** keeps the original's look and the highest output, but needs the most cuts and the tightest ones: every piece is
  a full 69 x 39 mm with clipped corners, and breakage costs a whole cell's worth of pieces.
- **F2** is the forgiving version: smaller pieces are easier to place, the border can hide cut edges and cell tolerances,
  and a 5 mm inset gets 8 pieces per cell. The cost is output (6 to 8 W per side against 9 W) and, unless the border is
  dark and matched to the cover, a different look. The outline is then drawn by a printed or laminated cover.
- **F3** needs no cutting and no cutting skill, but is less well documented (the listed ratings look high for a
  polycrystalline cell), covers only 73 percent of each outline, and takes 30 pieces per side to wire. It is the fallback if
  cutting turns out badly.

Cost per panel (cells only, prices seen): F1 and F2 at 2 mm need 4 cells, about US$15, and F2 at 5 mm needs 2 cells, about
US$7.5; double each for breakage. No price for the F3 pack was found.

Decision: F1 as the target, with F2 at a 2 mm inset as the accepted tolerance, and F3 as the fallback if cutting fails.
Before cutting for the panel, cut a spare cell to the F1 size, measure the pieces under a lamp, and count how many are
within 2 mm of the outline.

With F1 or F2 the six holes per side serve a serpentine: row 1 left and row 3 right carry the two external leads, and the
other four holes take the two jumpers between rows, which run inside the cavity. With F3 the same holes serve whichever
series and parallel layout is chosen.

## What the original uses

The cell grid is 5 x 3 per side of about 69 x 39 mm with 6.5 mm clipped bottom corners (`original-dimensions.md` 3g,
derived), the size of a standard 26.5 cm2 triple-junction cell cut in half; the cover glass is 200 um cerium-doped
borosilicate [S10]; the supplier is not named. The stated peak generation is 15 W [S3].

## Cell data read for this note

| Cell | Figures | Caveat |
|---|---|---|
| CESI CTJ30 (triple junction, the size class above) | datasheet v2025.1 table: Voc 2.6 V, Jsc 17.8, Jm 17.1 mA/cm2, Vm 2.3 V, Pmax 39.8 mW/cm2, 29.1 percent, beginning of life | read from text extracted from the PDF, so the column alignment is unchecked; test conditions not read; thickness and mass of the standard cell not found (the thin version is 80 um, 50 mg/cm2) |
| Spectrolab UTJ, 26.62 cm2 bare | Voc 2.718 V, Isc 0.459 A, Vmp 2.417 V, fill factor 86.7 percent | from a NASA paper, a production-cell figure the paper gives alongside research results; not a datasheet |
| Silicon, C60-class 125 x 125 mm | 22.5 percent, 0.582 V, 5.93 A | a rounded database entry, not a measured pair; a retail "C60 5x5" listing gives 0.6 V and 3.6 W |

Availability and price of space-grade triple-junction cells were not looked up; they are sold for flight, so a hobby
build would need surplus or a supplier willing to sell a few. Treat option A below as the original's choice, and option B
as the practical one (with the fill options above).

## Electrical options (derived)

| | Option A: triple junction | Option B: silicon cut to 69 x 39 |
|---|---|---|
| Per cell | 2.3 V, 0.45 A, 1.05 W (AM0, beginning of life) | 0.58 V, 1.03 A, 0.60 W (one sun, perpendicular; cutting losses ignored) |
| One row of 5 in series | 11.5 V, 0.45 A, 5.2 W | 2.9 V, 1.03 A |
| One side, 3 rows in parallel | 11.5 V, 1.36 A, **15.6 W** | too low in voltage |
| One side, all 15 in one series string | 34.5 V | 8.7 V, 1.03 A, **9.0 W** |
| Charger | buck MPPT, input above 13 V (5 x 2.6 V open circuit) | buck-boost MPPT, input about 8.7 V |

The triple-junction side comes to 15.6 W at normal incidence, within 5 percent of the stated 15 W peak [S3] if one
side faces the sun at a time. That is a consistency check on the numbers, not proof the original is wired that way.
Both sides together would be 31 W but only one faces the sun. Output on a near-vertical panel scales with
cos(sun elevation minus 10 degrees) times the cosine of the azimuth off the panel normal: 0.94 at 30 degrees
elevation, 0.77 at 50, 0.50 at 70.

For the 2S pack (8.4 V full, 43 Wh) a side delivers roughly 9 to 16 W at best, against about 35 W driving
(`electronics-spec.md`): solar charges the pack, it does not run the rover.

## Built in

- **Stack.** The panel carries a 1.0 mm stack: insulating film (the panel is conductive aluminium), adhesive, cell,
  and cover glass. The dummy plates use the same thickness, so the envelope will not change. Real cells need
  an insulating layer; the film and adhesive are not chosen.
- **Wire holes.** Twelve 5 mm holes, six per side panel: one beside each end of each cell row, 17 mm outboard of the
  end cell's centre (x = plus or minus 160.2, under the cell's outer half). Hole row heights z 235, 275 and 316. All string
  ends come inside the cavity, so the series and parallel wiring is chosen on a terminal block and either option
  above can be wired. The holes are under the dummy cells and so invisible; real cells will need their rear contact
  and a lead brought to the hole, which depends on the cell type.
- **Clearance.** Nothing in the frame, standoffs, bearing plates or shaft path lies within 6 mm of any hole's axis,
  14 mm deep. The nearest member is the top side rail, 9 mm above the highest hole row (centre to rail); the mid rail is 50 mm below the lowest; the posts are 5 mm from the
  hole edges. Wires should pass between the panel and the mid rail and drop to the floor.
- **Harness.** The longest straight run from a hole to the charge controller is 363 mm; allow about 470 mm of wire per
  lead. Grommets for the 12 holes are not chosen.
- **Charge controller.** A 50 x 30 x 12 mm box is reserved in the front compartment of the interior (x 112, y -70,
  on the floor, 30 g assumed), clear of the other parts. The part is not chosen: it must be an MPPT charger for a 2S
  lithium pack (8.4 V, constant current then constant voltage) taking the input of the chosen option, with at least
  2 A out for option A.

## Off-the-shelf silicon cells near 69 x 39 mm (searched 2026-11-07)

No cell of about 69 x 39 mm was found. The nearest products:

| Product | Size | Rating | Notes |
|---|---|---|---|
| Silicon Solar, laser-cut monocrystalline cell | 156 x 60 mm | 0.55 V, 2500 mA, 1.38 W | sold in small or large quantities; yields only 2 pieces of 69 x 39 mm (against about 4 from a 125 x 125 mm cell) |
| AOSHIKE-type micro cell, 100-pack | 52 x 19 mm | 0.5 V, 400 mA listed | polycrystalline; one reviewer measured 0.65 V and 140 mA under bright light, so the listed current is doubtful |
| Full cells (C60-class, Maxeon Gen III) | 125 x 125 mm, 150 um thick | 0.58 V, 5.9 A | no pre-cut versions found; Gen III is no longer manufactured |
| Industry 1/3-cut and shingled cells | not found in small lots | | these exist in modules but were not found as loose cells for hobby use |

So the realistic route is to cut full cells to the 69 x 39 mm outline, as the cost estimate assumes. Alternatives:
tile several small pre-cut cells behind a printed or laminated cover that draws the 69 x 39 mm outline, or let the
real cells be smaller than the dummy cells, since from outside only the outline and the dark colour show.

## Wiring for the Futurlec fallback and single-cell options (history; the current design's wiring is above)

Check and numbers: `hardware/solar/solar.py`. Hole ids: side L or R, row 1 (bottom) to 3 (top), end F (front, +x) or R
(rear, -x), e.g. L2F. Each hole sits in the 11 mm gap above its row, 20.5 mm up the slope from the row's centre, at x = plus or minus 160.2
(z 235, 275 and 316). The holes clear every cell (checked against all 30 cells with the 3 mm stack); the top row's holes are 9 mm below
the top side rail, the mid rail is 50 mm below the lowest holes, and the posts are 5 mm from the hole edges.

**Terminal boards.** One small board (20 x 8 x 90 mm, ASSUMPTION) lies on the cavity-facing face of each of the four posts at
z 205 to 305 (centred on the cell field), on the inner face of the vertical post. Fit checked: no clash with the frame, standoffs, plates or contents. The front board of a side takes
the three front holes of that side, the rear board the three rear holes, so each hole wire is 30 to 40 mm long. Holes are
5 mm; a bundled pair of 24 AWG wires fits, with a grommet.

**The decided build (Futurlec cells), and silicon cut to size: one 15-cell series string per side (serpentine).** Polarity is set
by how the cells are wired. The Futurlec cell's leads or pads are not described on its page, so how a wire reaches each cell
is open; the 11 mm gaps above and between the rows give room to take it from the cell to the hole.

```
row 3   rear  <-- jumper B --+                          front (+) --> lead + to the charger
row 2   rear  --> ... -->  front  --- jumper A ---+
row 1   rear (-) --> ... --> front -----------------+
          ^ lead - to the charger
```
Row 1 runs rear to front, jumper A joins row 1's front hole to row 2's front hole, row 2 runs front to rear, jumper B joins
row 2's rear hole to row 3's rear hole, and row 3 runs rear to front. Jumper A sits on the front board, jumper B on the
rear board; the (-) lead leaves the rear board (hole 1R) and the (+) lead the front board (hole 3F). Lengths with
30 percent slack: jumpers about 53 mm each; leads, left side 438 mm (-) and 319 mm (+), right side 380 mm (-) and
247 mm (+), to the charge controller at the front floor. All 24 AWG. Using 84 milliohm per metre (the standard value for 24 AWG
copper), 15 Futurlec cells at 0.28 A over 1.1 m of lead pair drop 0.03 V of 7.2 V, and 0.06 V at 0.64 A (under 1 percent);
silicon cut to 69 x 39 mm at 1.03 A would drop 0.10 V of 8.7 V.

**Silicon, F3 (tiled 52 x 19 mm cells).** The same serpentine, with 10 pieces per row (5 positions, 2 pieces each): 5 V per row
at the listed 0.5 V, 15 V per side (20 V at the reviewer's 0.65 V). The alternative, the two pieces of each position in
parallel and 15 positions in series, doubles the tabs in each row and gives 7.5 V and 0.8 A listed; the same six holes serve it.

**Triple junction (option A).** Rows in parallel instead: each row of 5 is a string of its own, 11.5 V, 0.45 A. The three front
holes become the plus side and the three rear holes the minus side: a plus bus on the front board with one blocking diode per row
(so a shaded row is not driven backwards by the others) and a minus bus on the rear board. Side leads then carry 1.36 A: 24 AWG
over 1.1 m drops 0.13 V of 11.5 V.

**Both sides to the charger.** One side faces the sun at a time and the other may be dark or shaded, so the two sides cannot
simply be joined: a dark side would load the lit one. Either a blocking diode in each side's plus lead (a Schottky drop, typically
0.3 to 0.5 V from memory, costs about 3 to 6 percent of 8.7 V), then joined at the charger, or a charger with two inputs. The
choice goes with the charger (`electronics-spec.md`).

**Protection, not designed:** a fuse or resettable fuse in each side's plus lead; a bypass diode across each row so one shaded
row does not throttle the string (the two ends of a row are 320 mm apart, so it needs a 420 mm wire back to the diode, and it
is optional for a first pass); a connector between each side's boards and the charger so a panel can come off.

## Cost per panel (rough, prices seen 2026-11-07)

"Panel" here is one side's 15 cells. Only the cell prices below were found; everything else is unpriced.

**Option B, silicon cut from C60-class cells.** Single C60 or E60 cells were listed at about US$3.60 to 3.80 each
(a 150-cell pack at about $3.59 a cell; one retail 20-cell pack at about $7 a cell; bulk factory listings at $0.50 to $2.30
but with minimum orders of 150 and up). Each 125 x 125 mm cell yields about 4 pieces of 69 x 39 mm (a simple packing, not
optimised), so 15 pieces need 4 cells, about **US$15 per panel** with no breakage. Cutting silicon cells breaks many, so
budget twice that: **US$30 per panel**. The same listings warn that the Gen III cells are no longer made, so supply may be thin.
Not priced: tabbing ribbon, solder and flux, insulating film, adhesive, cover glass or encapsulant, and the 2 mm aluminium
panel itself.

**Option A, triple-junction cells.** No per-cell price was found for any supplier (CESI, CAVU Aerospace, Rikei, AZUR
and others route requests to quotes). For scale only: NanoAvionics lists a complete 20 W CubeSat GaAs panel from
EUR 12,800, about EUR 640 per watt. At that rate one 15.6 W side would be about EUR 10,000 (derived; a flight-qualified
assembled panel, so not a bare-cell price). A bare-cell quote and minimum order size would be needed.

**Shared, not per panel:** the charge controller, fuses, diodes and grommets.

## Open

- Which cells: the electrical option, a supplier, and the real cell outline and rear contact. The 69 x 39 mm clipped
  outline holds for a half-cut triple-junction cell; silicon cut to that outline needs a cutting method.
- The charge controller (shortlist in `electronics-spec.md`: a buck-boost is needed for the 8.7 V silicon string), fuses, diodes, terminal board parts and the grommets.
- Bonding and insulating the cells, interconnect tabs, and cover glass or encapsulation.
- Testing. Output at the actual sun angle on the panels is not measured; the table is arithmetic from datasheet values.
- Whether to put a dark border and the clipped outline on the dummy cells so they look like the real ones; they are
  plain clipped plates in the CAD.
