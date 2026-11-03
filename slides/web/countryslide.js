// Mounts <canvas data-countries> as a globe of every country (Natural Earth
// 110m, slides/data/countries.js from scripts/make_countries.py): hover a
// country and it lights up; click it and csar solves the enclosing cone of
// its vertices in the browser and draws the ellipse, with the name and CSAR
// in a fixed readout beside the globe. The same globe library, solver, and
// ellipse construction as the DGGS globe slides. Keys steer a focused globe.
import { Orb, lnglatToVec3 } from './vendor/ajglobe.min.js';
import { countries } from '../data/countries.js';
import { load as csarLoad } from 'https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@v0.1.5/teec.js';
import { solve as csarSolve } from 'https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@v0.1.5/vendor/csar.js';
import { rim, MARK, coast } from './globeslide.js';

const LOOK_AT = [10, 25];
const FILL = [199, 194, 234, 255], HOVER = [120, 100, 220, 255], PICKED = [91, 79, 207, 255];

// Flatten the countries into the globe's polygon layout: one feature per
// polygon (outer ring + holes), and which country each feature belongs to.
const lnglat = [], starts = [0], polys = [0], owner = [];
for (let c = 0; c < countries.length; c++) {
  for (const poly of countries[c].polys) {
    for (const ring of poly) {
      for (const [lng, lat] of ring) lnglat.push(lng, lat);
      starts.push(lnglat.length / 2);
    }
    polys.push(starts.length - 1);
    owner.push(c);
  }
}
const geometry = { lnglat: new Float32Array(lnglat), starts: new Uint32Array(starts), polys: new Uint32Array(polys) };

const solver = csarLoad().catch(() => null);

for (const cv of document.querySelectorAll('canvas[data-countries]')) {
  const orb = new Orb(cv, { background: '#ffffff', sphere: '#e9ebf0', interaction: { keys: true } });
  orb.lookAt(...LOOK_AT);

  const hud = document.createElement('div');
  hud.className = 'globe-hud';
  hud.innerHTML = `
    <h2>Countries</h2>
    <table class="readout">
      <tr><th>country</th><td class="v-name">—</td></tr>
      <tr><th>CSAR</th><td class="v-ar">—</td></tr>
    </table>`;
  cv.after(hud);
  const vName = hud.querySelector('.v-name'), vAr = hud.querySelector('.v-ar');

  let hovered = -1, picked = -1;
  const fill = i => owner[i] === picked ? PICKED : owner[i] === hovered ? HOVER : FILL;
  const layer = orb.polygons({ ...geometry, fill });

  orb.on('hover', e => {
    const c = e.index == null ? -1 : owner[e.index];
    if (c === hovered) return;
    hovered = c;
    layer.update({ fill });
    if (picked < 0) vName.textContent = c < 0 ? '—' : countries[c].name;
  });

  // click: the enclosing cone of every vertex of the country, all its polygons
  let ellipse = null;
  orb.on('click', async e => {
    if (e.index == null || !await solver) return;
    picked = owner[e.index];
    layer.update({ fill });
    const pts = [];
    for (const poly of countries[picked].polys) for (const ring of poly) for (const [lng, lat] of ring) pts.push(...lnglatToVec3(lng, lat));
    let r = null;
    try { r = csarSolve(pts); } catch {}
    const ok = r?.status === 'converged';
    ellipse?.remove();
    ellipse = ok ? orb.lines({ xyz: rim(r), starts: new Uint32Array([0, 181]), color: MARK, width: 3 }) : null;
    vName.textContent = countries[picked].name;
    vAr.textContent = ok ? r.aspectRatio.toFixed(2) : 'no hemisphere holds it';
  });

  coast.then(lines => { if (lines) orb.lines({ ...lines, color: '#64748b', width: 1 }); });
}
