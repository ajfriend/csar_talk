"""Shared basemap glue for the figure scripts: OpenStreetMap raster tiles,
fetched once into raw/tiles/ and mosaicked in Web Mercator. Imported by the
make_*.py scripts (a script's own directory is on sys.path), so it declares
no dependencies of its own; the importing script needs numpy and pillow.

Web Mercator is conformal, so at city scale every local shape drawn over
these tiles is true to the sphere. Windows are specified in TRUE ground
kilometres so panels at different latitudes show the same extent despite
Mercator's scale growing with latitude.
"""
from pathlib import Path

import numpy as np
from PIL import Image

from _fig import fetch, save

TILES = Path(__file__).resolve().parent / 'raw' / 'tiles'
TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
ATTRIB = '© OpenStreetMap contributors'
R = 6378137.0
KM_PER_DEG = 111.32   # of latitude; of longitude, times cos(lat)


def merc(lat, lng):
    return R * np.radians(lng), R * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))


def merc_per_km(lat):
    """Mercator metres per true kilometre at this latitude (scale 1/cos φ)."""
    return 1000.0 / np.cos(np.radians(lat))


def tile_xy(lat, lng, z):
    n = 2 ** z
    x = (lng + 180) / 360 * n
    y = (1 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2 * n
    return x, y


def tile_bounds_merc(x, y, z):
    w = 2 * np.pi * R / 2 ** z
    return (-np.pi * R + x * w, np.pi * R - (y + 1) * w, -np.pi * R + (x + 1) * w, np.pi * R - y * w)


def fetch_tile(z, x, y):
    p = fetch(TILE_URL.format(z=z, x=x, y=y), TILES / f'{z}_{x}_{y}.png',
              headers={'User-Agent': 'csar-talk-figure/1.0 (ajfriend@gmail.com)'})
    return Image.open(p).convert('RGB')


def half_deg(lat, half_km, margin=1.15):
    """Degrees of latitude and longitude that cover ±half_km around a
    latitude, with a margin, for choosing tiles and cells."""
    d = half_km / KM_PER_DEG * margin
    return d, d / np.cos(np.radians(lat))


def basemap(lat, lng, half_km, z):
    """Mosaic the tiles covering ±half_km around a centre; return
    (image, extent in mercator m)."""
    dlat, dlng = half_deg(lat, half_km)
    x0, y0 = tile_xy(lat + dlat, lng - dlng, z)
    x1, y1 = tile_xy(lat - dlat, lng + dlng, z)
    xs, ys = range(int(x0), int(x1) + 1), range(int(y0), int(y1) + 1)
    mosaic = Image.new('RGB', (256 * len(xs), 256 * len(ys)))
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            mosaic.paste(fetch_tile(z, x, y), (256 * i, 256 * j))
    left, _, _, top = tile_bounds_merc(xs[0], ys[0], z)
    _, bottom, right, _ = tile_bounds_merc(xs[-1], ys[-1], z)
    return mosaic, (left, right, bottom, top)


def window(ax, lat, lng, half_km):
    """Square window of ±half_km of true ground distance around a centre."""
    cx, cy = merc(lat, lng)
    hw = half_km * merc_per_km(lat)
    ax.set_xlim(cx - hw, cx + hw); ax.set_ylim(cy - hw, cy + hw)
    ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor('0.75')


def finish(fig, name, **save_kw):
    """The OSM credit (required by the tile licence), layout, and save."""
    fig.text(0.995, 0.012, ATTRIB, ha='right', va='bottom', fontsize=7.5, color='0.4')
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, name, **save_kw)
