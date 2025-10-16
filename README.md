## CSCA5922

University of Colorado Boulder – CSCA5622  
Author: Adrian Gomez  
Contact: adrian.gomez-1@colorado.edu

### Python environment

This repository uses [uv](https://docs.astral.sh/uv/) to manage the Python environment.

1. Create and populate the virtual environment:
   ```bash
   uv sync
   ```
2. (Optional) Install the environment as a Jupyter kernel so it can be selected in notebooks:
   ```bash
   uv run python -m ipykernel install --user --name csca5922 --display-name "Python (csca5922)"
   ```
3. Launch JupyterLab:
   ```bash
   uv run jupyter lab
   ```

The key dependencies (such as `jupyterlab` and `ipykernel`) are declared in `pyproject.toml`. `uv sync` will resolve and install them into a local `.venv` directory.

### Project Artifacts

- Notebook: [notebooks/report.ipynb](notebooks/report.ipynb)
- Presentation (PDF): [docs/presentation.pdf](docs/presentation.pdf)
