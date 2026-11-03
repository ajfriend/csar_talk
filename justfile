# csar_talk tasks. Run `just` to list.

default:
    @just --list

# Self-contained: everything the deck fetches from the network is first
# downloaded into slides/vendor/ (a cache, gitignored) and served from there
# through the import map, so the same build works with wifi off. The Pages
# workflow runs this too.
#
# Render the deck into slides/_site/
render: fetch
    rm -rf slides/_site/vendor
    quarto render slides

# Serve the rendered deck. ES modules and wasm need http, not file://.
serve port="8000":
    @echo "http://localhost:{{port}}/"
    uv run --no-project -m http.server {{port}} -d slides/_site

# Render and open in the browser
show: render
    open slides/_site/index.html

# Local csar_viz checkout, for previewing the demo slides against unmerged
# csar_viz changes. The deck imports teec.js from a csar_viz tag on jsDelivr
# (cellslide.js, globeslide.js, countryslide.js, and importmap.html: bump
# them together); the recipes read it from cellslide.js.
csar_viz := "../../csar_all/csar_viz"
teec_cdn := `grep -o "https://cdn.jsdelivr.net/gh/ajfriend/csar_viz@[^/]*/" slides/web/cellslide.js`
# the coastline base, read from the one place it lives
ne_cdn := `grep -o "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@[^/]*/geojson/" slides/web/globeslide.js`

# Preview with the demo slides loading teec.js from the LOCAL csar_viz checkout.
# Works on a copy of the render output, so `render`/`show` stay clean. Ctrl-C stops the server.
preview: render
    rm -rf slides/_preview && cp -R slides/_site slides/_preview
    # Same origin as the deck (a symlink inside the copy), since a
    # cross-origin module import needs CORS headers a dev server does not send.
    ln -sfn "$(cd {{csar_viz}} && pwd)" slides/_preview/csar_viz
    sed -i '' 's|{{teec_cdn}}|http://localhost:8000/csar_viz/|g' slides/_preview/web/*.js
    @echo "deck: http://localhost:8000/   (csar_viz from {{csar_viz}})"
    (sleep 0.5; open http://localhost:8000/) &
    uv run --no-project -m http.server 8000 -d slides/_preview --bind 127.0.0.1

# The demo library with its wasm pair (refetched when the pin in cellslide.js
# changes), the coastlines, and MathJax. Skipped when present.
#
# Download what the deck fetches from the network into slides/vendor/
fetch:
    #!/usr/bin/env sh
    set -eu
    v=slides/vendor
    mkdir -p "$v/ne" "$v/mathjax"
    [ "$(cat "$v/csar_viz/TAG" 2>/dev/null)" = "{{teec_cdn}}" ] || {
      rm -rf "$v/csar_viz" && mkdir -p "$v/csar_viz/vendor"
      curl -sSfL \
        "{{teec_cdn}}teec.js" -o "$v/csar_viz/teec.js" \
        "{{teec_cdn}}vendor/csar.js" -o "$v/csar_viz/vendor/csar.js" \
        "{{teec_cdn}}vendor/csar.wasm" -o "$v/csar_viz/vendor/csar.wasm"
      echo "{{teec_cdn}}" > "$v/csar_viz/TAG"
    }
    [ -f "$v/ne/ne_110m_coastline.geojson" ] || curl -sSfL "{{ne_cdn}}ne_110m_coastline.geojson" -o "$v/ne/ne_110m_coastline.geojson"
    # MathJax, pinned, from the npm tarball: the script and its whole font
    # directory (it loads fonts lazily, so a hand-picked list would drift)
    [ -f "$v/mathjax/tex-chtml-full.js" ] || curl -sSfL https://registry.npmjs.org/mathjax/-/mathjax-3.2.2.tgz \
      | tar -xz -C "$v/mathjax" --strip-components=2 package/es5/tex-chtml-full.js package/es5/output/chtml/fonts/woff-v2

# Run every figure/data script (writes slides/figs/ and slides/data/)
figs:
    cd scripts && for f in make_*.py; do echo "$f"; uv run "$f"; done

# Remove render output
clean:
    -rm -rf slides/_site slides/_preview slides/.quarto

# Also remove the Python env, downloaded data, and the vendor cache

purge: clean
    -rm -rf scripts/.venv scripts/raw slides/vendor
