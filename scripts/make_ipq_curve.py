# /// script
# dependencies = ['matplotlib', 'numpy', 'scipy']
# ///
'''IPQ's response to pure elongation, next to AR's.

For an ellipse with semi-axes a >= b, AR = a/b and the planar isoperimetric
quotient is IPQ = 4*pi*A / P^2 (exact perimeter via the complete elliptic
integral). Regular polygons give the class baselines (hexagon, square,
triangle). The point of the picture: in the AR 1.0 to 1.3 band where every
hexagonal DGGS's cells live, IPQ moves by under 2%, less than a third of the
hexagon-to-square class gap. Numbers from csar_paper/positioning-notes.md.

Writes slides/figs/ipq_vs_ar.png.
'''
from pathlib import Path

import matplotlib
import numpy as np
from scipy.special import ellipe

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'slides' / 'figs' / 'ipq_vs_ar.png'

AR_MAX = 2.4
BAND = (1.0, 1.3)   # where hexagonal DGGS cells live

# hex DGGS reference points: (label, AR) at the working resolutions
MARKS = [('H3 max', 1.2173, (12, 8), 'left'),
         ('ISEA7H max', 1.3498, (10, -30), 'left'),
         ('S2 max', 1.6970, (10, -22), 'left'),
         ('A5 median', 2.1296, (-10, -32), 'right')]


def ellipse_ipq(ar):
    '''IPQ of an ellipse with semi-axes ar and 1 (so AR = ar).'''
    a, b = ar, 1.0
    area = np.pi * a * b
    m = 1 - (b / a) ** 2
    perim = 4 * a * ellipe(m)
    return 4 * np.pi * area / perim**2


def ngon_ipq(n):
    '''IPQ of a regular n-gon: pi / (n tan(pi/n)).'''
    return np.pi / (n * np.tan(np.pi / n))


def main():
    ar = np.linspace(1.0, AR_MAX, 400)
    ipq = ellipse_ipq(ar)

    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=200)
    ax.axvspan(*BAND, color='0.92', zorder=0)
    ax.text(np.mean(BAND), 0.57, 'hexagonal DGGS\ncells live here',
            ha='center', va='center', fontsize=10, color='0.35')

    ax.plot(ar, ipq, color='C0', lw=2.5, label='ellipse, exact perimeter')
    for name, n in [('regular hexagon', 6), ('regular square', 4),
                    ('regular triangle', 3)]:
        y = ngon_ipq(n)
        ax.axhline(y, color='0.55', lw=1.2, ls='--', zorder=1)
        ax.text(1.02, y + 0.008, f'{name}  {y:.3f}', ha='left',
                va='bottom', fontsize=9.5, color='0.35')

    for label, x, off, ha in MARKS:
        y = ellipse_ipq(x)
        ax.plot([x], [y], 'o', color='C0', ms=7, zorder=3)
        ax.annotate(f'{label}\nAR {x:.2f}, IPQ {y:.3f}', (x, y), xytext=off,
                    textcoords='offset points', fontsize=9, ha=ha,
                    color='0.25')

    ax.set_xlim(1.0, AR_MAX)
    ax.set_ylim(0.55, 1.02)
    ax.set_xlabel('aspect ratio (a / b)')
    ax.set_ylabel('isoperimetric quotient  4πA / P²')
    ax.set_title('IPQ barely moves where DGGS cells live;\n'
                 'polygon class moves it more than elongation does')
    ax.grid(alpha=0.3)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT)
    print(f'wrote {OUT}')
    print(f'IPQ loss at AR 1.3: {100 * (1 - ellipse_ipq(1.3)):.1f}%')
    print(f'hex->square class gap: {ngon_ipq(6) - ngon_ipq(4):.3f}')


if __name__ == '__main__':
    main()
