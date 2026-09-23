# Project instructions

Do not inspect these directories unless explicitly asked to:

- .venv/
- venv/
- node_modules/
- tmp/
- temp/
- data/
- dumps/
- dist/
- build/
- docs/
- .cache/
- \*.egg-info/
- jupyter/.ipynb_checkpoints/
- main\*.py
- __pycache__

For repository analysis, first inspect:
- README.md
- pyproject.toml / package.json / Cargo.toml / setup.py
- src/
- pyresearch/
- tests/
- docker-compose.yml
- Dockerfile

Prefer grep/find over reading large files.
Do not read generated datasets, logs, dumps, virtualenvs or dependency directories.

## Coding Standards
- Follow PEP-8 (max line length: 79 chars).
- Reply in Russian.
- Code, comments, and docstrings must be in English.
- **Always update `requirements.txt` whenever a new Python dependency is installed.**

## Quality Control
- Run `flake8 . --exclude=.venv` to check for PEP-8 violations.
- Run `python -m unittest -v` to run unit tests.
