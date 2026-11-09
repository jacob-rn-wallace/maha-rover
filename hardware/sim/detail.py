"""Visual-only detail for the simulation model: cast edges, lid seams, screws, a hex gland, lens rings, bracket bolts.

None of this is in the CAD checks or the mass budget (screw and gland masses are in the allowances of docs/replica-mass.md).
Sizes marked ASSUMPTION are not from a drawing; they only make the model look like the parts it stands for.  Rover frame, mm.
"""
import math

from build123d import (Axis, BuildPart, BuildSketch, Box, Cylinder, Locations, Plane, Pos, RegularPolygon, Rot, Sphere, extrude, fillet)


def soften(shape, radius, axis=Axis.Z):
    """Round the edges parallel to `axis` (a cast box's corners); returns the shape unchanged if the fillet fails."""
    try:
        edges = shape.edges().filter_by(axis)
        return fillet(edges, radius)
    except Exception:
        return shape


def seam(shape, normal, pos, width=0.7, depth=0.5):
    """Cut a thin groove round the shape at `pos` along the `normal` axis (0, 1, 2 = x, y, z): the seam between a die-cast box and its lid."""
    bb = shape.bounding_box()
    size = [bb.size.X, bb.size.Y, bb.size.Z]
    ctr = [(bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2]
    out, inn = list(size), list(size)
    for i in range(3):
        if i == normal:
            out[i] = inn[i] = width
        else:
            out[i] += 2.0
            inn[i] -= 2 * depth
    c = list(ctr)
    c[normal] = pos
    return shape - (Pos(*c) * Box(*out) - Pos(*c) * Box(*inn))


def cap_screw(x, y, z, direction, d=4.0, head_d=7.0, head_h=3.0):
    """Socket-head cap screw head standing on a surface at (x, y, z), pointing along `direction` ('+x', '-y', '+z', ...)."""
    head = Cylinder(head_d / 2, head_h) - Pos(0, 0, head_h / 2 - 0.9) * Cylinder(d * 0.42, 1.2)   # hex socket approximated as a round recess
    rot = {"+z": Rot(0, 0, 0), "-z": Rot(180, 0, 0), "+x": Rot(0, 90, 0), "-x": Rot(0, -90, 0), "+y": Rot(-90, 0, 0), "-y": Rot(90, 0, 0)}[direction]
    off = {"+z": (0, 0, head_h / 2), "-z": (0, 0, -head_h / 2), "+x": (head_h / 2, 0, 0), "-x": (-head_h / 2, 0, 0), "+y": (0, head_h / 2, 0), "-y": (0, -head_h / 2, 0)}[direction]
    return Pos(x + off[0], y + off[1], z + off[2]) * rot * head


def gland_pg7(x, z, y_wall, out=12.0):
    """PG7 cable gland standing out from the -y wall at `y_wall`: a hex body against the wall and a domed cap nut."""
    with BuildPart() as hexb:
        with BuildSketch(Plane.XZ):
            RegularPolygon(7.5, 6)
        extrude(amount=5.0)                                   # Plane.XZ normal is -Y: extrudes outward from y = 0 to -5
    body = Pos(x, y_wall, z) * hexb.part
    cap = Pos(x, y_wall - 5.0 - 3.5, z) * Rot(90, 0, 0) * Cylinder(5.6, 7.0)
    dome = Pos(x, y_wall - out + 4.2, z) * Sphere(4.2)
    return body + cap + dome


def lens_detail(lens):
    """4 mm CS lens: grooved focus ring and a front retaining ring; returns (barrel, front_glass, ring)."""
    bb = lens.bounding_box()
    cy, cz = (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2
    xf = bb.max.X
    barrel = lens
    for k in range(6):                                           # focus ring grooves
        xg = xf - 9.0 - 1.6 * k
        barrel = barrel - Pos(xg, cy, cz) * Rot(0, 90, 0) * (Cylinder(16.0, 0.7) - Cylinder(14.2, 0.7))
    barrel = barrel - Pos(xf - 0.6, cy, cz) * Rot(0, 90, 0) * Cylinder(10.5, 1.2)     # pocket for the retaining ring, so no two faces are coplanar (they z-fought as a jagged line)
    ring = Pos(xf - 0.7, cy, cz) * Rot(0, 90, 0) * (Cylinder(10.3, 1.0) - Cylinder(7.4, 1.0))
    glass = Pos(xf - 0.9, cy, cz) * Rot(0, 90, 0) * Cylinder(7.6, 0.4)
    return barrel, glass, ring


def bracket_bolts(bracket):
    """Two M5 button-head bolts through the sheet bracket's web into the extrusion (ASSUMPTION: heights 555 and 585, on the extrusion axis)."""
    bb = bracket.bounding_box()
    xc = (bb.min.X + bb.max.X) / 2
    return [cap_screw(xc, 22.0, z, "+y", d=5.0, head_d=9.5, head_h=3.0) for z in (555.0, 585.0)]
