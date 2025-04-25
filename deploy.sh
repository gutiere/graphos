rm -rf dist
rm -rf *.egg-info
uv sync
uv run setup.py sdist
uv run -m twine upload dist/*
