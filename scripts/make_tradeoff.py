# /// script
# dependencies = ['matplotlib', 'numpy', 'pyarrow']
# ///
"""Shape versus area, one point per system: the worst cell's aspect ratio
against the spread of cell areas, with the ideal grid (round cells, one
size) as a star. The six systems are the ones on the globe slides, at
the survey's own matched working resolutions (its manifest's target_res,
about 0.1 km² per cell).

Computed from the dggs_compare data release's tables, fetched into
scripts/raw/tables/ on first run: at these resolutions each table is a
point-drawn sample of a million cells, so the extremes are the sample's
(the open-questions slide says so). The coarse globe tables are not used:
there the area spread is wider and the pentagons show.

Writes slides/figs/tradeoff.png and prints the numbers (the median is the
one the trade-off slide's notes quote).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyarrow.parquet as pq

from _fig import EDGE, ELL, INK, RELEASE_URL, fetch, save

RAW = Path(__file__).resolve().parent / 'raw' / 'tables'

# system -> (table in the release, where the label goes)
SYSTEMS = {
    'H3':       ('h3-h3_r9',          'left'),
    'S2':       ('s2-s2_r15',         'left'),
    'ISEA7H':   ('isea7h-dggal_r10',  'below'),
    'IVEA7H':   ('ivea7h-dggal_r10',  'above'),
    'A5':       ('a5-a5_r14',         'above'),
    'rHEALPix': ('rhealpix-dggal_r9', 'below'),
}
OFFSET = {'left': (10, 0, 'left', 'center'), 'above': (0, 10, 'center', 'bottom'),
          'below': (0, -10, 'center', 'top')}


def stats(table):
    """(max AR, area max ÷ min, median AR) of one table."""
    path = fetch(f'{RELEASE_URL}{table}.parquet', RAW / f'{table}.parquet')
    t = pq.read_table(path, columns=['ar', 'area'])
    ar, area = t['ar'].to_numpy(), t['area'].to_numpy()
    return float(ar.max()), float(area.max() / area.min()), float(np.median(ar))


def main():
    fig, ax = plt.subplots(figsize=(9, 6.2))
    for name, (table, where) in SYSTEMS.items():
        max_ar, area_ratio, median_ar = stats(table)
        print(f'{name:9s} {table:20s} max AR {max_ar:.3f}  area max/min {area_ratio:.3f}  median AR {median_ar:.3f}')
        ax.plot(max_ar, area_ratio, 'o', ms=11, mfc=EDGE, mec='white', mew=1.2, zorder=3)
        dx, dy, ha, va = OFFSET[where]
        ax.annotate(name, (max_ar, area_ratio), xytext=(dx, dy), textcoords='offset points',
                    ha=ha, va=va, fontsize=13, color=INK)
    ax.plot(1, 1, '*', ms=20, mfc=ELL, mec='white', mew=1, zorder=3)
    ax.annotate('ideal', (1, 1), xytext=(12, -2), textcoords='offset points',
                ha='left', va='center', fontsize=13, color=ELL)
    ax.set_xlabel('worst cell aspect ratio', fontsize=13)
    ax.set_ylabel('cell area ratio', fontsize=13)
    ax.set_xlim(0.93, 2.52); ax.set_ylim(0.9, 2.2)
    ax.grid(True, color='0.9', lw=0.8); ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('0.6')
    ax.tick_params(colors='0.35', labelsize=12)
    fig.tight_layout()
    save(fig, 'tradeoff.png')


if __name__ == '__main__':
    main()
