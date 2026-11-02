"""Shared conventions for the figure scripts: output paths, the deck's
palette, matplotlib setup, saving, and the few geometry helpers every
script otherwise re-spells. Imported by the make_*.py scripts (a script's
own directory is on sys.path), so it declares no dependencies of its own;
the importing script needs numpy, plus matplotlib / s2sphere / h3 for the
helpers it calls (those are imported lazily, so a script without figures,
like score_cities.py, needs none of them).
"""
from pathlib import Path

import numpy as np

SLIDES = Path(__file__).resolve().parent.parent / 'slides'
FIGS = SLIDES / 'figs'
DATA = SLIDES / 'data'

# The deck's purple, and the ellipse's teal.
FILL = '#c7c2ea'     # cell / shape fill
EDGE = '#5b4fcf'     # cell / shape edge
INK = '#1f1a66'      # annotations, stick figures
ELL = '#0d9488'      # the enclosing ellipse
DPI = 200


def fetch(url, path, headers=None):
    """Download `url` to `path` unless it is already there; returns the path."""
    import urllib.request
    path = Path(path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=60) as r:
            path.write_bytes(r.read())
    return path


def save(fig, name, dpi=DPI):
    """Write a figure to slides/figs/ with the deck's dpi and background. A
    .jpg name writes JPEG (for basemap rasters, which PNG stores at ~10x
    the size); .png is the default for line art."""
    out = FIGS / name
    kw = {'pil_kwargs': {'quality': 88, 'optimize': True}} if out.suffix == '.jpg' else {}
    fig.savefig(out, dpi=dpi, facecolor='white', **kw)
    print(f'wrote {out}')


# Figure scripts import pyplot after this module, so the headless backend is
# set first; scripts without figures (score_cities.py) never touch matplotlib.
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass


# ---- geometry -------------------------------------------------------------

def xyz(lat, lng):
    """(lat, lng) degrees -> unit vector."""
    la, lo = np.radians(lat), np.radians(lng)
    return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])


def lnglat(X):
    """(N, 3) unit vectors -> [[lng, lat], ...] degrees, rounded for data files."""
    lat = np.degrees(np.arcsin(X[:, 2]))
    lng = np.degrees(np.arctan2(X[:, 1], X[:, 0]))
    return [[round(float(a), 5), round(float(b), 5)] for a, b in zip(lng, lat)]


def h3_latlngs(cell):
    """An H3 cell's boundary as [(lat, lng)] degrees."""
    import h3
    return list(h3.cell_to_boundary(cell))


def s2_latlngs(cell_id):
    """An S2 cell's four corners as [(lat, lng)] degrees, from a CellId."""
    import s2sphere
    cell = s2sphere.Cell(cell_id)
    lls = [s2sphere.LatLng.from_point(cell.get_vertex(i)) for i in range(4)]
    return [(ll.lat().degrees, ll.lng().degrees) for ll in lls]
