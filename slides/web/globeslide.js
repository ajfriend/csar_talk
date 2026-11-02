// Mounts every <canvas data-globe="key"> as an ajglobe globe: every cell
// of one DGGS at one resolution (slides/data/globe/, the dggs_compare data
// release's own binaries, fetched by scripts/make_globes.py), colored by a
// metric on a scale SHARED across the deck's globes so systems compare
// directly. The globe fills the slide; a side panel built here carries the
// title, a toggle between the two metrics (it only swaps the fill
// colours), a horizontal legend with the globe's distribution of the shown
// metric drawn above it (log counts; the hovered cell is marked on both),
// and a fixed two-row readout of the hovered cell's AR and area. Nothing
// in the panel moves on hover.
//
//   hover a cell: it highlights and the panel shows its AR and its area
//   click a cell: csar solves it in the browser (the same wasm the cone
//                 demo runs) and its enclosing ellipse is drawn on the globe
//
// Every globe in the deck shares one view (orientation and zoom) and one
// metric: turn one or flip its toggle and the others follow, so slide to
// slide compares like with like.
//
// Canvas attribute: data-globe="h3_r3", which globe (required).
// Keys steer a focused globe (click it): WASD tilt/spin, Q/E or arrows roll.
import { Orb, lnglatToVec3, geojsonLines } from './vendor/ajglobe.min.js';
import { globes } from '../data/globes.js';
// The solver: csar_viz's loader (it also fetches the wasm for the cone
// slide, memoised, and checks the csar.js / csar.wasm pair match) and the
// ABI's solve. Both come from the same tag as cellslide.js's import; the
// offline profile's import map (offline.html) remaps that base.
import { load as csarLoad } from 'https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@v0.1.3/teec.js';
import { solve as csarSolve } from 'https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@v0.1.3/vendor/csar.js';

// Natural Earth coastlines, fetched once for all the globes. Resolved
// through the import map so the offline profile serves the vendored copy.
const NE = import.meta.resolve('https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/ne_110m_coastline.geojson');
const coast = fetch(NE).then(r => r.json()).then(geojsonLines).catch(() => null);
const TAU = 2 / 3;   // 1 - sigma_0^2: the cross-section's size on the plane b.x = 1
const LOOK_AT = [10, 25];
const MARK = '#c2620a';   // the hovered cell's marker and the solved ellipse

// ---- colour. AR is cool: light to dark through the deck's teal and
// purple (light = round, dark = stretched: a mostly-round globe reads as a
// pale solid on the white slide and the stretch bands pop). Area is WARM
// and diverging, so the two views cannot be mistaken for each other: brown
// for cells smaller than the mean, cream at the mean, orange-red for larger.
const AR_STOPS = [[247,247,250],[200,232,230],[120,205,198],[13,148,136],[40,96,140],[62,52,150],[31,26,102],[18,12,60]];
const AREA_STOPS = [[84,48,5],[140,81,10],[191,129,45],[223,194,125],[250,243,228],[246,178,107],[230,97,1],[179,49,0]];
const lerp = (stops, t) => {
  t = Math.min(1, Math.max(0, t)) * (stops.length - 1);
  const i = Math.min(stops.length - 2, t | 0), f = t - i, a = stops[i], b = stops[i + 1];
  return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f, 255];
};
const lut = stops => Array.from({ length: 256 }, (_, i) => lerp(stops, i / 255));
const rgb = c => `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})`;
// The LUT is linear between evenly spaced stops, which is what a CSS
// gradient does too, so the legend bar is the stops themselves.
const gradient = stops => stops.map((c, i) => `${rgb(c)} ${100 * i / (stops.length - 1)}%`).join(',');

// ---- the shared scales, from the globes actually on slides. AR: floor 1,
// ceiling the largest AR on any of them (the full range, so every cell of
// every system is on the axis), with a square-root stretch so the 1.0-1.3
// band where hexagonal grids live still gets room. Area: symmetric in
// log(cell/mean) about 1, so x2 and x0.5 are equally far.
const canvases = [...document.querySelectorAll('canvas[data-globe]')];
const shown = canvases.map(cv => globes[cv.dataset.globe]);
const arMax = Math.max(...shown.map(g => g.ar.max));
const areaSpan = Math.max(...shown.flatMap(g => [Math.log(g.area.max), -Math.log(g.area.min)]));
const METRICS = {
  ar:   { stops: AR_STOPS, lut: lut(AR_STOPS), t: v => Math.sqrt((v - 1) / (arMax - 1)),
          ticks: ['1', (1 + 0.25 * (arMax - 1)).toFixed(2), arMax.toFixed(2)],   // the middle one sits mid-bar under the stretch
          fmt: v => v.toFixed(3) },
  area: { stops: AREA_STOPS, lut: lut(AREA_STOPS), t: v => 0.5 + Math.log(v) / (2 * areaSpan),
          ticks: [`×${Math.exp(-areaSpan).toFixed(2)}`, '×1', `×${Math.exp(areaSpan).toFixed(2)}`],
          fmt: v => `×${v.toFixed(3)}` },
};
// Where a value sits along the legend, 0..1: the colour's own placement,
// so the histogram, the bar, and the fill agree cell for cell.
const along = (m, v) => Math.min(1, Math.max(0, m.t(v)));
const HBINS = 48;
const histogram = (m, v) => {
  const counts = new Uint32Array(HBINS);
  for (let i = 0; i < v.length; i++) counts[Math.min(HBINS - 1, (along(m, v[i]) * HBINS) | 0)]++;
  return counts;
};

const bin = async (path, Ctor) => new Ctor(await (await fetch(path)).arrayBuffer());
// The wasm loads with the page, so the first click does not wait.
const solver = csarLoad().catch(() => null);

// The enclosing ellipse of a solved cell as a closed ring of unit vectors:
// on the plane b.x = 1 the cross-section is the ellipse with semi-axes
// sqrt(TAU)/sigma_1, sqrt(TAU)/sigma_2 along Q's columns 1 and 2 (the same
// construction as the cone demo's rim); each point is then pushed to the sphere.
function rim(r, n = 180) {
  const q = j => [r.Q[j], r.Q[3 + j], r.Q[6 + j]];
  const b = q(0), f1 = q(1), f2 = q(2);
  const a1 = Math.sqrt(TAU) / r.sigma[1], a2 = Math.sqrt(TAU) / r.sigma[2];
  const out = new Float32Array(3 * (n + 1));
  for (let k = 0; k <= n; k++) {
    const t = 2 * Math.PI * k / n, c = a1 * Math.cos(t), s = a2 * Math.sin(t);
    const p = [b[0] + c * f1[0] + s * f2[0], b[1] + c * f1[1] + s * f2[1], b[2] + c * f1[2] + s * f2[2]];
    const l = Math.hypot(p[0], p[1], p[2]);
    out.set([p[0] / l, p[1] / l, p[2] / l], 3 * k);
  }
  return out;
}

// ---- the deck-wide state: one metric, one view. A view only goes to
// globes whose slide is laid out (reveal keeps nearby slides laid out at
// opacity 0, and a hidden globe would redraw on every drag frame); a slide
// becoming current picks the shared view up then. setView is idempotent,
// so the echo from a synced globe's own viewchange stops there.
let metric = 'ar';
let view = null;
const refreshers = [];   // one per globe, re-fills it for the current metric
const present = cv => cv.closest('section')?.classList.contains('present');
const syncView = from => {
  view = from.orb.getView();
  for (const cv of canvases) if (cv !== from && present(cv)) cv.orb.setView(view);
};
const syncMetric = m => { if (m === metric) return; metric = m; for (const f of refreshers) f(); };
Reveal.on('slidechanged', e => {
  const cv = e.currentSlide.querySelector('canvas[data-globe]');
  if (cv && view) cv.orb.setView(view);
});

for (const cv of canvases) {
  const key = cv.dataset.globe;
  const orb = new Orb(cv, { background: '#ffffff', sphere: '#e9ebf0', interaction: { keys: true } });
  orb.lookAt(...LOOK_AT);
  cv.orb = orb;
  orb.on('viewchange', () => syncView(cv));

  // ---- the side panel. A div, not an aside: reveal's theme positions
  // every aside absolutely. Every element has a fixed slot, so hovering
  // the globe changes numbers, never layout.
  const hud = document.createElement('div');
  hud.className = 'globe-hud';
  hud.innerHTML = `
    <h2>${globes[key].label.replace(', ', '<br>')}</h2>
    <p class="toggle"><button data-m="ar">aspect ratio</button><button data-m="area">relative area</button></p>
    <canvas class="hist" width="300" height="56"></canvas>
    <div class="bar"><i></i></div>
    <div class="ticks"><span></span><span></span><span></span></div>
    <table class="readout">
      <tr><th>AR</th><td class="v-ar">—</td></tr>
      <tr><th>relative area</th><td class="v-area">—</td></tr>
    </table>`;
  cv.after(hud);
  for (const b of hud.querySelectorAll('.toggle button')) b.addEventListener('click', () => syncMetric(b.dataset.m));
  const vAr = hud.querySelector('.v-ar'), vArea = hud.querySelector('.v-area');
  const hist = hud.querySelector('canvas.hist'), hctx = hist.getContext('2d');
  const showLegend = () => {
    const m = METRICS[metric];
    hud.querySelector('.bar i').style.background = `linear-gradient(90deg,${gradient(m.stops)})`;
    hud.querySelectorAll('.ticks span').forEach((el, i) => { el.textContent = m.ticks[i]; });
    for (const b of hud.querySelectorAll('.toggle button')) b.classList.toggle('on', b.dataset.m === metric);
  };
  showLegend();

  (async () => {
    const base = `data/globe/${key}`;
    const [pos, starts, ar, area] = await Promise.all([
      bin(`${base}_pos.f32`, Float32Array), bin(`${base}_idx.u32`, Uint32Array),
      bin(`${base}_ar.f32`, Float32Array), bin(`${base}_area.f32`, Float32Array),
    ]);
    const vals = { ar, area };
    const hists = { ar: histogram(METRICS.ar, ar), area: histogram(METRICS.area, area) };
    let hovered = null;   // the hovered cell's value of the current metric, for the marker
    const drawHist = () => {
      const m = METRICS[metric], counts = hists[metric];
      const W = hist.width, H = hist.height;
      hctx.clearRect(0, 0, W, H);
      const bw = W / HBINS, logmax = Math.log(Math.max(...counts) + 1);
      for (let i = 0; i < HBINS; i++) {
        if (!counts[i]) continue;
        const h = (Math.log(counts[i] + 1) / logmax) * (H - 2);
        hctx.fillStyle = rgb(m.lut[Math.round(255 * (i + 0.5) / HBINS)]);
        hctx.fillRect(i * bw, H - h, Math.max(1, bw - 0.8), h);
      }
      if (hovered != null) {
        const x = along(m, hovered) * W;
        hctx.strokeStyle = MARK; hctx.lineWidth = 2;
        hctx.beginPath(); hctx.moveTo(x, 0); hctx.lineTo(x, H); hctx.stroke();
      }
    };
    const fill = () => { const m = METRICS[metric], v = vals[metric]; return i => m.lut[(along(m, v[i]) * 255) | 0]; };
    const layer = orb.polygons({ lnglat: pos, starts, fill: fill() });
    drawHist();
    refreshers.push(() => { layer.update({ fill: fill() }); hovered = null; showLegend(); drawHist(); });

    // hover: highlight, both numbers in their fixed slots, a marker on the histogram
    let last = null;
    orb.on('hover', e => {
      const i = e.index ?? null;
      if (i === last) return;
      last = i;
      orb.highlight(i ?? -1, layer);
      vAr.textContent = i == null ? '—' : METRICS.ar.fmt(ar[i]);
      vArea.textContent = i == null ? '—' : METRICS.area.fmt(area[i]);
      hovered = i == null ? null : vals[metric][i];
      drawHist();
    });

    // click: solve the cell and draw its enclosing ellipse (replacing the last)
    let ellipse = null;
    orb.on('click', async e => {
      if (e.index == null) return;
      if (!await solver) return;
      const pts = [];
      for (let k = starts[e.index]; k < starts[e.index + 1]; k++) pts.push(...lnglatToVec3(pos[2 * k], pos[2 * k + 1]));
      let r;
      try { r = csarSolve(pts); } catch { return; }
      if (r.status !== 'converged') return;
      ellipse?.remove();
      ellipse = orb.lines({ xyz: rim(r), starts: new Uint32Array([0, 181]), color: MARK, width: 3 });
      vAr.textContent = r.aspectRatio.toFixed(3);
    });

    // Coastlines in a slate that reads on both the pale and the saturated
    // globes. Without a network the cells still draw.
    const lines = await coast;
    if (lines) orb.lines({ ...lines, color: '#64748b', width: 1 });
  })();
}
