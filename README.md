# How *Squished* Are Your DGGS Cells? A Spherical Aspect Ratio

Slides for a FOSS4G NA 2026 talk, by AJ Friend.

- **Slides:** [ajfriend.com/csar_talk](https://ajfriend.com/csar_talk/)
- **The metric:** `pip install csar` ([csar_py](https://github.com/ajfriend/csar_py)),
  solver in [csar_zig](https://github.com/ajfriend/csar_zig)
- **The survey and globes:** [ajfriend.com/dggs_compare](https://ajfriend.com/dggs_compare/)
- **The live demo:** [ajfriend.com/csar_viz](https://ajfriend.com/csar_viz/)

## Layout

- `slides/`: a Quarto reveal.js project. `talk.qmd` is the deck; `web/` holds
  the JavaScript that mounts the live shape and globe slides; `figs/` and
  `data/` are prerendered by the scripts and committed.
- `scripts/`: Python figure and data scripts, run with `uv`.
- `beats.md`, `plan.md`: working notes on what the talk has to hit and how it is built.

## Building

Needs [Quarto](https://quarto.org), [just](https://just.systems), and [uv](https://docs.astral.sh/uv/).

```sh
just render   # slides/_site/, self-contained: works with wifi off
just serve    # http://localhost:8000/ (ES modules and wasm need http)
just figs     # regenerate every figure and data file
```

The render first downloads the demo library, coastlines, and MathJax into
`slides/vendor/` (a cache) and serves them from there, so the built deck
has no network dependency. Pushing to `main` renders and deploys it to
GitHub Pages the same way.

## Licence

- Code (`scripts/`, `slides/web/`, the justfile, and configuration): [MIT](LICENSE).
- Slides, figures, and notes (`slides/talk.qmd`, `slides/figs/`, `beats.md`, `plan.md`):
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- `slides/figs/city_grids.jpg` is drawn over OpenStreetMap tiles,
  © OpenStreetMap contributors, [ODbL](https://www.openstreetmap.org/copyright).
- Coastlines are from [Natural Earth](https://www.naturalearthdata.com/) (public domain).
- Globe data under `slides/data/globe/` is from the
  [dggs_compare](https://github.com/ajfriend/dggs_compare) data releases;
  `slides/web/vendor/ajglobe.min.js` is a build of [ajglobe](https://github.com/ajfriend/ajglobe) (MIT).
