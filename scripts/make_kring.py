# /// script
# dependencies = ["h3>=4", "numpy", "matplotlib", "pillow"]
# ///
"""A 3-ring H3 neighbourhood in Sydney and in Seoul, same resolution, same
map scale: the shape you get when you say "within 3 rings". Built for the
"why shape matters" slide and NOT used there (the neighbours cartoon,
make_neighbors.py, replaced it): a ring of hexagons is a big hexagon whose
bounding box is not square, and H3's area variation shows too, so the
picture says three things at once. Kept as a record of that finding.

Writes slides/figs/kring.png.
"""
import h3
import matplotlib.pyplot as plt
import numpy as np

from _basemap import basemap, finish, merc, merc_per_km, window
from _fig import EDGE, FILL, INK, h3_latlngs

RES, K = 7, 3
PANELS = [('Sydney', -33.87, 151.10), ('Seoul', 37.55, 126.98)]
HALF_KM, ZOOM = 14.0, 12


def neighbourhood(lat, lng):
    centre = h3.latlng_to_cell(lat, lng, RES)
    cells = h3.grid_disk(centre, K)
    outline = h3.cells_to_geo(cells)['coordinates'][0]          # (lng, lat) ring
    return cells, np.array([merc(a, b) for b, a in outline])


def dim_line(ax, p0, p1, label, pad, vertical=False):
    (x0, y0), (x1, y1) = p0, p1
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle='<->', color=INK, lw=1.6, shrinkA=0, shrinkB=0))
    if vertical:
        ax.text(x0 - pad, (y0 + y1) / 2, label, ha='right', va='center', fontsize=14,
                color=INK, rotation=90, fontweight='bold')
    else:
        ax.text((x0 + x1) / 2, y0 - pad, label, ha='center', va='top', fontsize=14,
                color=INK, fontweight='bold')


def panel(ax, name, lat, lng):
    img, extent = basemap(lat, lng, HALF_KM, ZOOM)
    ax.imshow(np.asarray(img), extent=extent, interpolation='bilinear', zorder=1)
    cells, oxy = neighbourhood(lat, lng)
    for c in cells:
        xy = np.array([merc(a, b) for a, b in h3_latlngs(c)])
        ax.fill(xy[:, 0], xy[:, 1], fc=FILL, ec=EDGE, lw=0.8, alpha=0.35, zorder=2)
    ax.plot(oxy[:, 0], oxy[:, 1], color=INK, lw=2.4, zorder=3)
    # bounding-box extents in true km, from the Mercator ring
    (xmin, ymin), (xmax, ymax) = oxy.min(axis=0), oxy.max(axis=0)
    ew, ns = (xmax - xmin) / merc_per_km(lat), (ymax - ymin) / merc_per_km(lat)
    m = 0.06 * (xmax - xmin)
    dim_line(ax, (xmin, ymin - m), (xmax, ymin - m), f'{ew:.1f} km', pad=m * 0.4)
    dim_line(ax, (xmin - m, ymin), (xmin - m, ymax), f'{ns:.1f} km', pad=m * 0.4, vertical=True)
    window(ax, lat, lng, HALF_KM)
    ax.set_title(f'{name}: H3 res {RES}, {K} rings', fontsize=15, color='0.2', pad=8)
    return ew, ns


def main():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.6))
    for ax, (name, lat, lng) in zip(axes, PANELS):
        ew, ns = panel(ax, name, lat, lng)
        print(f'{name}: E-W {ew:.2f} km, N-S {ns:.2f} km, ratio {ew / ns:.3f}')
    finish(fig, 'kring.png')


if __name__ == '__main__':
    main()
