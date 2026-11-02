# /// script
# dependencies = ["h3>=4", "s2sphere", "numpy", "matplotlib", "pillow"]
# ///
"""The opening picture: DGGS cells over a city basemap, so the squish reads
in a context the eye already knows.

Panels: H3 over Sydney (its roundest), H3 over Seoul (squished, AR ~1.21),
S2 over Osaka (next to an S2 cube corner, AR ~1.7). The cities are the
extremes from scripts/score_cities.py, which scores ~70 major cities.

Every panel shows the same TRUE ground extent (±HALF_KM), so cell sizes
compare across latitudes despite Mercator's scale growing with latitude.
H3 res 6 cells are ~7 km across; S2 level 10 cells ~9 km.

Basemap: OpenStreetMap raster tiles, fetched once into scripts/raw/tiles/
and mosaicked in Web Mercator (scripts/_basemap.py). At city scale, shape
matches the sphere, so the squish on screen is the grid's, not the map's.
Cell boundaries are projected vertex-wise (edges are a few km, straight to
the pixel).

Writes slides/figs/city_grids.jpg.
"""
import h3
import matplotlib.pyplot as plt
import numpy as np
import s2sphere
from matplotlib.colors import to_rgba

from _basemap import basemap, finish, half_deg, merc, window
from _fig import EDGE, FILL, h3_latlngs, s2_latlngs

# (title, system, resolution, centre lat, lng)
PANELS = [
    ('H3 in Sydney', 'h3', 6, -33.87, 151.15),
    ('H3 in Seoul', 'h3', 6, 37.55, 126.98),
    ('S2 in Osaka', 's2', 10, 34.70, 135.50),
]
HALF_KM = 38.0          # true ground half-width of every panel
ZOOM = 10               # tile zoom; ~150 m/px here


def h3_rings(lat, lng, res, k):
    for c in h3.grid_disk(h3.latlng_to_cell(lat, lng, res), k):
        yield [merc(a, b) for a, b in h3_latlngs(c)]


def s2_rings(lat, lng, level, dlat, dlng):
    rect = s2sphere.LatLngRect.from_point_pair(
        s2sphere.LatLng.from_degrees(lat - dlat, lng - dlng),
        s2sphere.LatLng.from_degrees(lat + dlat, lng + dlng))
    cov = s2sphere.RegionCoverer(); cov.min_level = level; cov.max_level = level
    for cid in cov.get_covering(rect):
        yield [merc(a, b) for a, b in s2_latlngs(cid)]


def panel(ax, title, system, res, lat, lng):
    img, extent = basemap(lat, lng, HALF_KM, ZOOM)
    ax.imshow(np.asarray(img), extent=extent, interpolation='bilinear', zorder=1)
    dlat, dlng = half_deg(lat, HALF_KM, margin=1.7)
    rings = h3_rings(lat, lng, res, 12) if system == 'h3' else s2_rings(lat, lng, res, dlat, dlng)
    for ring in rings:
        xy = np.array(ring)
        # a translucent fill with an opaque edge, in one artist
        ax.fill(xy[:, 0], xy[:, 1], fc=to_rgba(FILL, 0.3), ec=EDGE, lw=1.4, zorder=2)
    window(ax, lat, lng, HALF_KM)
    ax.set_title(title, fontsize=15, color='0.2', pad=8)


def main():
    fig, axes = plt.subplots(1, len(PANELS), figsize=(4.2 * len(PANELS), 4.75))
    for ax, p in zip(axes, PANELS):
        panel(ax, *p)
    # JPEG at 150 dpi: the slide shows it ~1000 px wide; the PNG was 3 MB.
    finish(fig, 'city_grids.jpg', dpi=150)


if __name__ == '__main__':
    main()
