# /// script
# dependencies = ["matplotlib", "numpy"]
# ///
"""Cartoon for "why shape matters": two neighbouring cells, stretched, with
a person at the far end of each. They are neighbours; they are also far
apart. (Kimerling's criterion 5: points in a cell should be close
together.) No title, no second panel: the picture is the whole joke.

Writes slides/figs/neighbors.png.
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

from _fig import EDGE, FILL, INK, save

STRETCH = 3.0


def hexagon(cx):
    """Pointy-top regular hexagon (circumradius 1) centred at (cx, 0), then
    x-stretched. Pointy-top, so horizontal neighbours share a vertical edge."""
    t = np.radians(np.arange(30, 390, 60))
    return np.column_stack([(cx + np.cos(t)) * STRETCH, np.sin(t)])


def person(ax, x, y, h=0.7):
    """Stick figure standing on (x, y), total height h: head on top, arms
    from the shoulders angled down and out, legs from the hips."""
    r = 0.17 * h
    head_c = y + h - r
    shoulder = head_c - r - 0.02 * h
    hip = y + 0.32 * h
    ax.add_patch(plt.Circle((x, head_c), r, fc='white', ec=INK, lw=2, zorder=5))
    ax.plot([x, x], [hip, shoulder], color=INK, lw=2, zorder=5)
    ax.plot([x - 0.24 * h, x, x + 0.24 * h], [shoulder - 0.2 * h, shoulder, shoulder - 0.2 * h],
            color=INK, lw=2, zorder=5)
    ax.plot([x - 0.18 * h, x, x + 0.18 * h], [y, hip, y], color=INK, lw=2, zorder=5)


def bubble(ax, x, y, text):
    ax.annotate(text, xy=(x, y), xytext=(x, y + 0.9), fontsize=17, ha='center', va='center',
                color=INK, zorder=6,
                bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=INK, lw=1.4),
                arrowprops=dict(arrowstyle='-', color=INK, lw=1.2, shrinkB=6))


def main():
    fig, ax = plt.subplots(figsize=(12.4, 3.1))
    w = np.sqrt(3) / 2                     # two neighbours share the edge at x = 0
    for cx in (-w, w):
        ax.add_patch(Polygon(hexagon(cx), closed=True, fc=FILL, ec=EDGE, lw=2, zorder=2))
    left, right = (-w - 0.62) * STRETCH, (w + 0.62) * STRETCH    # the far end of each cell
    person(ax, left, -0.33); person(ax, right, -0.33)
    bubble(ax, left, 0.42, 'are you close?')
    bubble(ax, right, 0.42, 'right next to you!')
    ax.set_xlim(-2 * w * STRETCH - 0.3, 2 * w * STRETCH + 0.3); ax.set_ylim(-1.15, 1.9)
    ax.set_aspect('equal'); ax.axis('off')
    fig.tight_layout()
    save(fig, 'neighbors.png')


if __name__ == '__main__':
    main()
