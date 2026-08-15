# BEAST Installation Guide

This guide explains how to install **BEAST — Battery Estimation Architecture and Simulation Toolkit** from a source checkout or from locally built distribution artifacts.

BEAST is currently used as a Python library, so installation is verified through Python imports and the public model/estimator selectors.

## Requirements

BEAST requires:

- Python 3.10 or newer;
- `pip`;
- the runtime dependencies declared in `pyproject.toml`.

A virtual environment is strongly recommended.

Check your Python version:

```bash
python --version
```

## Create a virtual environment

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
```

## Install from a source checkout

From the repository root:

```bash
python -m pip install .
```

Verify the installation:

```bash
python -c "import beast; print(beast.__version__)"
```

## Editable installation for development

If you plan to modify BEAST:

```bash
python -m pip install -e .
```

To include the declared test and documentation dependencies:

```bash
python -m pip install -e ".[test,docs]"
```

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for the contributor workflow.

## Optional dependencies

Install testing support only:

```bash
python -m pip install -e ".[test]"
```

Install documentation support only:

```bash
python -m pip install -e ".[docs]"
```

The current extras provide `pytest` and `pdoc`, respectively.

Ruff and the Python build frontend are useful development tools but are not currently part of these extras:

```bash
python -m pip install ruff build
```

## Verify the package

Check the package version:

```bash
python -c "import beast; print(beast.__version__)"
```

Check a battery-model selector:

```bash
python -c "from beast import selectCellModel; print(selectCellModel('R0R1C1').__name__)"
```

Check an estimator selector:

```bash
python -c "from beast import selectEstimator; print(selectEstimator('EKFDUAL').__name__)"
```

Check the installed package metadata:

```bash
python -m pip show beast-battery-estimation-architecture-simulation-toolkit
```

These checks do not require model datasets or covariance configuration.

## Run the tests

If you installed the test extra from a repository checkout:

```bash
python -m pytest
```

Run the command from the project root, where `pyproject.toml` and `tests/` are located.

## Build distribution artifacts

Install the build frontend:

```bash
python -m pip install build
```

Then build BEAST:

```bash
python -m build
```

The generated wheel and source distribution are written to:

```text
dist/
```

## Install from a wheel

Install a locally built wheel with:

```bash
python -m pip install dist/*.whl
```

On Windows PowerShell, you can specify the wheel filename explicitly:

```powershell
python -m pip install .\dist\<wheel-file>.whl
```

Testing the wheel in a clean virtual environment is recommended before a release.

## Install from a source distribution

Install a locally built source distribution with:

```bash
python -m pip install dist/*.tar.gz
```

If your shell does not expand wildcards, provide the exact filename.

## Upgrade

From an updated source checkout:

```bash
python -m pip install --upgrade .
```

For an editable development installation, reinstall when project metadata or dependencies change:

```bash
python -m pip install -e ".[test,docs]"
```

## Uninstall

```bash
python -m pip uninstall beast-battery-estimation-architecture-simulation-toolkit
```

The distribution name used by `pip` is different from the Python import name:

```python
import beast
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'beast'`

Check whether BEAST is installed in the active interpreter:

```bash
python -m pip show beast-battery-estimation-architecture-simulation-toolkit
python -m pip --version
```

If it is not installed, activate the intended virtual environment and run:

```bash
python -m pip install .
```

### `pip` uses a different Python installation

Prefer:

```bash
python -m pip ...
```

over calling `pip` directly.

Compare:

```bash
python --version
python -m pip --version
```

### Python is older than 3.10

Create a new environment with Python 3.10 or newer and reinstall BEAST.

### Dependency installation fails

Upgrade packaging tools first:

```bash
python -m pip install --upgrade pip setuptools wheel
```

Then retry:

```bash
python -m pip install .
```

### Editable installation does not reflect metadata changes

Editable installs reflect normal source changes, but dependency, version, entry-point, or package-data changes can require reinstalling:

```bash
python -m pip install -e ".[test,docs]"
```

### Source-tree tests pass but the installed package fails

Build and test the wheel in a fresh environment:

```bash
python -m build
python -m venv .venv-wheel
# activate .venv-wheel
python -m pip install --upgrade pip
python -m pip install dist/*.whl
python -c "import beast; print(beast.__version__)"
```

This verifies the packaged artifact rather than relying on the repository's source-tree test path.

## Recommended setups

For normal library use:

```bash
python -m venv .venv
# activate the environment
python -m pip install .
```

For development:

```bash
python -m venv .venv
# activate the environment
python -m pip install --upgrade pip
python -m pip install -e ".[test,docs]"
python -m pip install ruff build
python -m pytest
```

Keep this guide synchronized with `pyproject.toml` whenever supported Python versions, dependencies, extras, or installation methods change.
