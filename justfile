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

# Run every figure/data script (writes slides/figs/ and slides/data/)
figs:
    cd scripts && for f in make_*.py; do echo "$f"; uv run "$f"; done

# Remove render output
clean:
    -rm -rf slides/_site slides/.quarto

# Also remove the Python env and downloaded data
purge: clean
    -rm -rf scripts/.venv scripts/raw
