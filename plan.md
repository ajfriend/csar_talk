# Plan: FOSS4G NA 2026 talk on spherical aspect ratio (csar)

Talk: "How Squished Are Your DGGS Cells? A Spherical Aspect Ratio"
Slot: 25 minutes. Proposal text: `../proposals/ar.md`. Must mention H3.

## Decisions

- **Quarto + reveal.js**, authored in markdown (`talk.qmd`). Same stack as
  `~/work/h3c2p_talk_prep`, which already proved out iframed interactive
  HTML, fullscreen embeds, and a publish step.
- **No executed code cells.** Quarto renders markdown only. Every figure,
  table, and data file is prerendered by scripts under `scripts/` and driven
  by the `justfile`. The deck references static outputs in `slides/figs/`
  and globe data in `slides/data/`.
- **`uv` + `justfile`** manage the Python environment and every task
  (render, figs, serve, publish). No bare python; PEP 723 or `pyproject.toml`
  for deps.
- **Interactive globes via ajglobe, vendored.** `slides/web/vendor/ajglobe.min.js`
  (provenance beside it): dist/ is not committed upstream and the package is
  not on npm. Globe data is the dggs_compare data release's own binaries,
  fetched by `scripts/make_globes.py`. Superseded the earlier plan to iframe
  the live site (2026-11-02).
- **csar_viz only for the cone plot**, as a canvas mounted with its
  `teec.js` library imported from jsDelivr at a csar_viz tag (v0.1.5 now; bump in
  `slides/web/cellslide.js` and the justfile together). Optionally its `playground.html` for the 2D C(A, b)
  intuition slide.
- **One self-contained build.** The deck's JS imports the demo library
  from jsDelivr at a csar_viz tag, but `just render` first downloads that,
  the coastlines, and MathJax into `slides/vendor/` and an import map
  points every fetch at those copies, so the same build works online and
  off (verified with every request on localhost). The Pages workflow runs
  the same recipe. An earlier online/offline split (two builds into one
  folder, whichever ran last) was folded into this on 2026-11-03.
- **One repo, published to GitHub Pages by a GitHub Actions workflow**
  on push to main. Render output is never committed. This replaces the
  prep-repo + rendered-repo pair used for h3c2p. The workflow only needs
  Quarto (`quarto-dev/quarto-actions/setup`) plus
  `actions/upload-pages-artifact` and `actions/deploy-pages`, since every
  figure is prerendered and committed under `slides/figs/`. No Python in CI.
- **Web slides are the primary artifact.** Export a PDF handout afterward
  as a fallback only.

## Layout

Two top-level folders, plus the justfile and this plan.

```
csar_talk/
  plan.md
  justfile                 every task; run from the repo root
  scripts/                 all Python: figure + data scripts, no CLI args
    pyproject.toml         deps (csar, sparea, h3, pyarrow, matplotlib, ...)
    uv.lock
    make_*.py              one script per figure or data product
    raw/                   downloaded dggs_compare Parquet releases, gitignored
  slides/                  a self-contained Quarto project
    _quarto.yml            output-dir: _site
    talk.qmd               the deck (markdown only)
    style.css
    web/                   talk-owned globe pages, one per globe slide;
                           each imports ajglobe from the CDN and loads data/
    figs/                  prerendered PNG/SVG outputs, written by scripts,
                           committed
    data/                  per-globe AR data (JSON or quantized binary),
                           written by scripts, committed
    _site/                 render output, gitignored
  .github/workflows/pages.yml   render slides/ with Quarto, deploy to Pages
```

`talk.qmd` lives in `slides/` rather than the top level because Quarto
resolves images, iframes, and CSS relative to the document, and the Pages
workflow renders and uploads one directory.

## Justfile targets

All run from the repo root; Python targets `cd scripts` and use `uv run`.

- `render`: `quarto render slides`
- `serve`: `uv run -m http.server` on `slides/_site/` (ES modules + wasm
  need http)
- `data`: fetch dggs_compare Parquet releases into `scripts/raw/`
- `figs`: run every `scripts/make_*.py`; static plots to `slides/figs/`,
  globe data to `slides/data/`
- `fetch`: download the vendored libraries into `slides/vendor/` (run by
  `render`)
- `pdf`: reveal.js print-to-PDF via decktape or Chrome, for the handout
- `publish`: just `git push`; the Pages workflow renders and deploys
- `clean` / `purge`

## Figure and demo inventory

Static (scripts -> slides/figs/):

1. Squished H3 hexagons, a few resolutions and locations. The visual hook.
2. Why shape matters: neighbor distances, gradient stencil, convolution
   kernel on a squished vs round cell.
3. Enclosing-ellipse-on-sphere diagram: points on sphere, the cone, the
   ellipse cross section, major/minor axes.
4. AR histograms across H3, S2, A5, ISEA7H, IVEA7H, rHEALPix at area-matched
   resolutions (from dggs_compare `out/histograms.png` or regenerated).
5. AR vs resolution per system (`by_res_*.png`).
6. AR vs IPQ scatter, and the "kink cells" that show where IPQ and AR
   disagree.
7. Summary table of per-system stats.
8. Ellipsoid generalization sketch for the closing (from
   `csar_all/skar_notes/ellipsoid_sphere_distortion_and_transforms.md`).

Interactive (web/ -> iframed):

- G1. AR heatmap globe, one per DGGS, switchable. ajglobe. Precomputed AR
  per cell shipped as data. No live solving.
- G2. Side-by-side globes for two systems at matched resolution.
- C1. Cone demo: click points on the sphere, watch the enclosing cone and
  ellipse update. A canvas in the slide, mounted with csar_viz's `teec.js`
  library (imported from ajfriend.com/csar_viz), so the slide chooses the
  points, view, and overlays, and fragments can change them. Small point
  sets only.
- C2 (optional). 2D playground for C(A, b), if the math slide needs it.

## Example cells (found 2026-09-02; the slides and their script were cut 2026-11-03)

Enumerated every H3 cell at res 0-2 and every S2 cell at L0-3 with csar
(dggs_compare's tables subsample above r0/L3). The coarsest resolution
that shows each system's real spread:

- H3 res 2 (~3° cells): AR 1.000 to 1.226. Res 0 tops out at 1.07, res 1
  at 1.14 (and only with a 7-vertex cell); finer resolutions stay at
  ~1.22-1.25. Round: 828007fffffffff. Squished: 82082ffffffffff.
- S2 level 3 (~12° cells): AR 1.009 to 1.548. L2 gives 1.04-1.39 at 23°;
  L5+ settles at ~1.68. Round: 0fc0000000000000. Squished: 2ac0000000000000.

Each gets a slide (slides/web/cellslide.js mounts every `canvas[data-cell]`);
the camera closes in on cells this small, so csar_viz's distance floor is 1.02.

## Talk skeleton (drafted 2026-11-01 in slides/talk.qmd; ~21 min talking)

Scope decisions, against the proposal (`../proposals/ar.md`):

- **Spherical only.** The ellipsoid is one slide: Gauss says no
  ellipsoid-to-sphere map is both conformal and equal-area, so area and
  shape use different auxiliary spheres (authalic vs conformal latitude);
  the shape difference is at most ~0.2%. Left as an open modeling choice.
- **IPQ by the analytic response curve** (`scripts/make_ipq_curve.py`,
  numbers from `csar_paper/positioning-notes.md`), not per-cell IPQ.
  dggs_compare issue 90 (per-cell IPQ) stays open; not needed for the talk.
- ~~Globes iframed from the live site.~~ Superseded: local ajglobe globes
  (see the decisions above).
- **The trade-off figure is computed from the release tables** (scripts/make_tradeoff.py);
  the histogram figures were copied from dggs_compare/out (histograms,
  area_histograms, tradeoff). Four systems in the headline figures;
  IVEA7H and rHEALPix only on the site. Per-resolution plots cut: AR is
  resolution-stable, said in one sentence.
- Convex optimization is two slides: global optimum + certificate (with
  the declarative/agents point as one spoken sentence), then the software.

Budget as first drafted (superseded: the live budget is the table in
`beats.md`; minute targets are in the speaker notes):

| section | slides | min |
|---|---|---|
| title, about me | 2 | 1 |
| problem: many DGGSs, area is the usual axis, shape is the other | 3 | 2 |
| hook: round vs squished H3 and S2 cells | 4 | 2 |
| why squish matters | 1 | 1.5 |
| definition, math, live demo | 3 | 4 |
| convex + certified; the software | 2 | 2 |
| survey: tradeoff, histograms, globes, table | 4 | 5 |
| vs IPQ | 1 | 1.5 |
| ellipsoid, the open question | 1 | 1 |
| close + links | 2 | 1.5 |
| | | 21.5 |

Still to do before the talk:

1. ~~Merge and deploy csar_viz `close-zoom`.~~ Done 2026-11-02 (PR #8 there);
   the hosted teec.js now has `view.fit` and the 1.02 floor; csar_viz is
   tagged v0.1.5 (hull-lift fix, outline overlay, synced cameras, points toggle, ellipse axes) and the deck imports that
   tag via jsDelivr.
2. ~~Screenshot of the globes tab for the fallback slide.~~ Moot: the globe
   slides now draw from local data (`scripts/make_globes.py`, ajglobe
   vendored); only the coastlines come from a CDN, and they fail soft.
3. ~~A figure for "why squish matters".~~ Done: the neighbours cartoon
   (`scripts/make_neighbors.py`). A k-ring version was built and dropped
   (`scripts/make_kring.py` records why).
4. ~~IVEA7H and rHEALPix rows in the summary table.~~ Done; both have globes too.
5. Native per-cell timing line on the software slide (csar_zig/bench).
6. ~~dggs_compare `?embed` mode.~~ Moot: no iframe; see 2.
7. ~~Pages workflow and the slides URL on the thanks slide.~~ Done 2026-11-02
   (`.github/workflows/pages.yml`; the site is ajfriend.com/csar_talk, the
   user site's domain over the repo name, like dggs_compare).
8. Timed run-through; cut S2-round and section-title slides first if long.

## Embedding notes

- ~~Iframes with `data-preload` on globe slides.~~ No iframes remain.
- Iframe steals keyboard focus after interaction. Add the click-outside or
  Escape handler used in h3c2p, or a visible "back to slides" affordance.
- Every interactive slide gets a static PNG fallback slide right after it,
  hidden in the normal flow (or a keyboard shortcut) for projector trouble.
- Keep globe data small: one file per system at the resolution shown, AR as
  float16 or quantized uint8 with a colormap in JS. CET-R2 for the colormap.
- Test on the laptop while mirroring at 1080p, since the projector path
  is where WebGL frame rates fall over.

## Open questions

- Final package name (skar_py is being renamed). Decide before slides are
  public.
- Which systems make the cut for the survey slides. Proposal lists H3, S2,
  A5, ISEA7H, IVEA7H, rHEALPix. dggs_compare has more.
- Whether to show the dual or duality certificate at all, or just say
  "certified" and point at the paper.

## Next steps

1. `git init`; create `slides/` with `_quarto.yml`, `talk.qmd`, and
   `style.css` + reveal config copied from h3c2p_talk_prep. Gitignore
   `slides/_site/`, `scripts/raw/`, `scripts/.venv/`.
2. `scripts/pyproject.toml` + `uv sync`; smoke-test `just render` on a
   stub deck. Add the Pages workflow and confirm it deploys the stub.
3. Enable GitHub Pages on csar_viz; get one CDN-loaded ajglobe globe and
   the cone iframe rendering in the deck.
4. Write the figure scripts against dggs_compare data.
5. Draft slides against the skeleton, then cut to 25 minutes.
