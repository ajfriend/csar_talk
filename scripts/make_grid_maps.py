# /// script
# dependencies = ["h3>=4", "s2sphere", "numpy", "matplotlib"]
# ///
"""The motivating picture: a patch of an actual DGGS grid, drawn so that
any squish the eye sees is the grid's, not the map's.

Each panel is a stereographic projection centred on the region. It is
conformal: local shapes are exact, only scale drifts (by 1/cos²(θ/2), about
2% at the rim of a 17° patch). An orthographic view would instead squash
the rim radially by cos θ, ~4.5% here, the same order as H3's own squish,
which is precisely the confusion to avoid. Cell boundaries are great-circle
polygons, densified before projection; Natural Earth 110m coastlines give
the eye a scale and a place.

Panels: H3 at a resolution and place where its hexagons are visibly wide
(the icosahedron-edge band over Scandinavia), and S2 near a cube corner
(South Australia), where its quads shear.

Not on a slide: the city-basemap version (make_city_grids.py) reads
better with landmarks; this one is kept as the coastline alternative.

Writes slides/figs/grid_maps.png. The Natural Earth coastline is fetched
into scripts/raw/ on first run.
"""
import json
from pathlib import Path

import h3
import matplotlib.pyplot as plt
import numpy as np
import s2sphere

from _fig import EDGE, FILL, fetch, h3_latlngs, s2_latlngs, save, xyz

COAST_URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_coastline.geojson'
COAST = Path(__file__).resolve().parent / 'raw' / 'ne_110m_coastline.geojson'

# (title, view centre lat, lng, angular radius of the patch in degrees)
PANELS = [
    ('H3, resolution 3', 66.0, 14.0, 17.0),
    ('S2, level 5', -35.0, 135.0, 17.0),
]
EDGE_SAMPLES = 8
COASTLINE = '0.45'


def frame(lat, lng):
    c = xyz(lat, lng)
    e = np.cross([0, 0, 1], c); e /= np.linalg.norm(e)      # east
    n = np.cross(c, e)                                       # north
    return c, e, n


def densify(ring):
    """Great-circle interpolate each edge of a closed ring of unit vectors."""
    out = []
    for a, b in zip(ring, np.roll(ring, -1, axis=0)):
        for t in np.linspace(0, 1, EDGE_SAMPLES, endpoint=False):
            p = (1 - t) * a + t * b
            out.append(p / np.linalg.norm(p))
    return np.array(out)


def project(points, c, e, n):
    """Stereographic from the antipode of c: a point at angle θ from c lands
    at radius tan(θ/2). Conformal. None if any point is on the far hemisphere."""
    d = points @ c
    if np.any(d <= 0):
        return None
    return np.column_stack([points @ e, points @ n]) / (1 + d)[:, None]


def disk_radius(radius_deg):
    return np.tan(np.radians(radius_deg) / 2)


def h3_cells(lat, lng, radius_deg, res):
    k = int(np.ceil(np.radians(radius_deg) * 6371 / h3.average_hexagon_edge_length(res, unit='km') / 1.5)) + 3
    cells = h3.grid_disk(h3.latlng_to_cell(lat, lng, res), k)
    return [np.array([xyz(a, b) for a, b in h3_latlngs(c)]) for c in cells]


def s2_cells(lat, lng, radius_deg, level):
    cap = s2sphere.Cap.from_axis_angle(s2sphere.LatLng.from_degrees(lat, lng).to_point(),
                                       s2sphere.Angle.from_degrees(radius_deg * 1.3))
    cov = s2sphere.RegionCoverer(); cov.min_level = level; cov.max_level = level
    rings = []
    for cid in cov.get_covering(cap):
        rings.append(np.array([xyz(a, b) for a, b in s2_latlngs(cid)]))
    return rings


def coastlines():
    gj = json.loads(fetch(COAST_URL, COAST).read_text())
    for f in gj['features']:
        g = f['geometry']
        lines = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
        for line in lines:
            yield np.array([xyz(la, lo) for lo, la in line])


def panel(ax, title, lat, lng, radius, rings):
    c, e, n = frame(lat, lng)
    r = disk_radius(radius)
    for ring in rings:
        if np.all(ring @ c > np.cos(np.radians(radius * 1.15))):
            xy = project(densify(ring), c, e, n)
            if xy is not None:
                ax.fill(xy[:, 0], xy[:, 1], fc=FILL, ec=EDGE, lw=0.9, alpha=0.75, zorder=2)
    for line in coastlines():
        vis = line @ c > 0
        for seg in np.split(np.arange(len(line)), np.flatnonzero(~vis)):
            seg = seg[vis[seg]] if len(seg) else seg
            if len(seg) > 1:
                xy = project(line[seg], c, e, n)
                ax.plot(xy[:, 0], xy[:, 1], color=COASTLINE, lw=1.1, zorder=3)
    ax.add_patch(plt.Circle((0, 0), r, fc='none', ec='0.8', lw=1, zorder=4))
    ax.set_xlim(-r, r); ax.set_ylim(-r, r)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=15, color='0.25', pad=8)
    # clip everything to the disk
    clip = plt.Circle((0, 0), r, transform=ax.transData)
    for art in ax.patches + ax.lines:
        art.set_clip_path(clip)


def main():
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 6.2))
    (t1, la1, lo1, r1), (t2, la2, lo2, r2) = PANELS
    panel(axes[0], t1, la1, lo1, r1, h3_cells(la1, lo1, r1, 3))
    panel(axes[1], t2, la2, lo2, r2, s2_cells(la2, lo2, r2, 5))
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    save(fig, 'grid_maps.png')


if __name__ == '__main__':
    main()
