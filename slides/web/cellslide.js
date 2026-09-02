// A per-cell slide: the cell's vertices and the spherical ellipse through
// them, looked at straight down the cone's axis. Cells come from
// data/cells.js (scripts/make_cell_examples.py).
import { mount } from 'https://ajfriend.com/csar_viz/teec.js';
import { byKey } from '../data/cells.js';

export function mountCell(canvasId, key) {
  const cell = byKey[key];
  return mount(document.getElementById(canvasId), {
    points: cell.points,
    view: { center: 'axis', dist: cell.dist },
    show: { cone: false, axis: false, hull: true },
    interaction: { edit: false },
  });
}
