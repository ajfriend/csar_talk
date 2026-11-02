// Mounts every <canvas data-cell="…"> in the deck with that point set from
// data/cells.js (scripts/make_cell_examples.py) or data/shapes.js
// (scripts/make_stretch.py), looked at straight down the cone's axis. Also
// the deck's one import of teec.js, so the cone slide takes `mount` from
// here. Pinned to a csar_viz tag via jsDelivr (correct content types + CORS
// for the module and the wasm), so the slides don't change when the demo
// repo does; `just preview` swaps in a local checkout.
//
// Canvas attributes (the HTML contract):
//   data-cell="key"       which point set (required)
//   data-show="hull,rim"  overlays to draw, in teec's own vocabulary (cone,
//                         rim, axis, hull, outline, points); listed ones on,
//                         the rest off. Default: hull, rim, points.
//   data-nums             caption the canvas with its numbers (IPQ if the
//                         set has one, and AR), from the same data as the points
//   data-edit             the points can be dragged
// On the canvas or any ancestor:
//   data-dist="2.4"       a fixed camera distance instead of fitting the rim,
//                         so shapes compared across canvases share one scale
// Canvases on one slide share a camera: spin either and both turn.
import { mount } from 'https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@v0.1.3/teec.js';
import { cells } from '../data/cells.js';
import { shapes } from '../data/shapes.js';

const sets = { ...cells, ...shapes };
const TOGGLES = ['cone', 'rim', 'axis', 'hull', 'outline', 'points'];
const showSpec = list =>
  Object.fromEntries(TOGGLES.map(k => [k, list.split(',').includes(k)]));

export { mount };

for (const cv of document.querySelectorAll('canvas[data-cell]')) {
  const d = cv.dataset, set = sets[d.cell];
  const dist = cv.closest('[data-dist]')?.dataset.dist;
  const slide = cv.closest('section');
  cv.teec = mount(cv, {
    points: set.points,
    view: { center: 'axis', ...(dist ? { dist: Number(dist) } : { fit: 0.45 }) },
    show: showSpec(d.show ?? 'hull,rim,points'),
    interaction: { edit: 'edit' in d },
    // onView fires only on user input, and setView does not fire it, so
    // mirroring one camera onto the slide's other canvases cannot loop.
    onView: view => {
      for (const other of slide.querySelectorAll('canvas[data-cell]'))
        if (other !== cv) other.teec?.setView({ frame: view });
    },
  });
  if ('nums' in d) {
    const p = document.createElement('p');
    p.className = 'nums';
    p.textContent = (set.ipq != null ? `IPQ ${set.ipq.toFixed(3)}   ` : '') + `AR ${set.ar.toFixed(2)}`;
    cv.after(p);
  }
}
