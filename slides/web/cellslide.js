// Mounts every <canvas data-cell="…"> in the deck with that cell from
// data/cells.js (scripts/make_cell_examples.py): the cell's vertices and
// the spherical ellipse through them, looked at straight down the cone's
// axis, sized to fill about half the stage. The points are fixed unless
// the canvas also has data-edit. Also the deck's one import of teec.js,
// so the cone slide takes `mount` from here. Pinned to a csar_viz tag via
// jsDelivr (correct content types + CORS for the module and the wasm), so
// the slides don't change when the demo repo does; `just preview` swaps in
// a local checkout.
import { mount } from 'https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@v0.1.0/teec.js';
import { cells } from '../data/cells.js';

export { mount };

for (const cv of document.querySelectorAll('canvas[data-cell]')) {
  mount(cv, {
    points: cells[cv.dataset.cell].points,
    view: { center: 'axis', fit: 0.45 },
    show: { cone: false, axis: false, hull: true },
    interaction: { edit: 'edit' in cv.dataset },
  });
}
