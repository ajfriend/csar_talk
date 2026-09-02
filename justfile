# csar_talk tasks. Run `just` to list.

default:
    @just --list

# Render the deck into slides/_site/
render:
    quarto render slides

# Serve the rendered deck. ES modules and wasm need http, not file://.
serve port="8000":
    @echo "http://localhost:{{port}}/"
    uv run --no-project -m http.server {{port}} -d slides/_site

# Render and open in the browser
show: render
    open slides/_site/index.html

# Local csar_viz checkout, for previewing the cone slide before its Pages
# site exists (or with unmerged csar_viz changes).
csar_viz := "../../csar_all/csar_viz"

# Preview with the cone slide loading teec.js from the LOCAL csar_viz checkout. Ctrl-C stops the server.
preview: render
    # Same origin as the deck (a symlink inside the render output), since a
    # cross-origin module import needs CORS headers a dev server does not send.
    ln -sfn "$(cd {{csar_viz}} && pwd)" slides/_site/csar_viz
    sed -i '' 's|https://ajfriend.com/csar_viz/|http://localhost:8000/csar_viz/|g' slides/_site/index.html
    @echo "deck: http://localhost:8000/   (csar_viz from {{csar_viz}})"
    (sleep 0.5; open http://localhost:8000/) &
    uv run --no-project -m http.server 8000 -d slides/_site --bind 127.0.0.1

# Run every figure/data script (writes slides/figs/ and slides/data/)
figs:
    cd scripts && for f in make_*.py; do echo "$f"; uv run "$f"; done

# Remove render output
clean:
    -rm -rf slides/_site slides/.quarto

# Also remove the Python env and downloaded data
purge: clean
    -rm -rf scripts/.venv scripts/raw
