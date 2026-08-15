# Installation Guide

This document describes how to install and verify **BEAST** for normal use,
research workflows, testing, documentation, and source development.

> **Python package name:** `beast`  
> **Distribution name:** `beast-battery-estimation-architecture-simulation-toolkit`  
> **Required Python version:** Python 3.10 or newer

For information about modifying the source code and contributing to the project,
see [`DEVELOPMENT.md`](DEVELOPMENT.md).

---

## 1. Requirements

BEAST requires:

- Python **3.10 or newer**
- `pip`
- a Python virtual environment is strongly recommended

The runtime Python dependencies are:

```text
numpy>=1.23
scipy>=1.9
matplotlib>=3.6
```

Optional dependencies are:

```text
pytest>=7    # testing
pdoc>=14     # API documentation
```

---

## 2. Create a virtual environment

Using a virtual environment keeps BEAST and its dependencies isolated from the
system Python installation.

### Linux / macOS

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows — PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows — Command Prompt

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
```

After activation, verify the Python version:

```bash
python --version
```

It must report Python 3.10 or newer.

Upgrade the packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

## 3. Recommended installation from the source repository

Clone the repository and enter its root directory:

```bash
git clone https://github.com/delloiaconos/beast-py.git
cd REPOSITORY
```

Replace the URL above with the actual BEAST repository URL.

Install the package:

```bash
python -m pip install .
```

This installs BEAST together with its required runtime dependencies.

The Python package can then be imported as:

```python
import beast
```

---

## 4. Install from a wheel

A wheel is the recommended format for installing a released version without
working directly from the source tree.

For release `0.2.0`:

```bash
python -m pip install dist/beast_battery_estimation_toolkit-0.2.0-py3-none-any.whl
```

If the wheel is located elsewhere, provide its complete or relative path:

```bash
python -m pip install /path/to/beast_battery_estimation_toolkit-0.2.0-py3-none-any.whl
```

`pip` will automatically install the required NumPy, SciPy, and Matplotlib
dependencies if they are not already available.

---

## 5. Install from the source distribution

A source distribution can also be installed directly:

```bash
python -m pip install dist/beast_battery_estimation_toolkit-0.2.0.tar.gz
```

This builds and installs the package locally.

---

## 6. Editable installation for development

If you intend to modify BEAST while keeping it installed in the virtual
environment, use an editable installation:

```bash
python -m pip install -e .
```

Changes made under:

```text
src/beast/
```

are then immediately visible to Python without reinstalling the package.

For a development workflow that does **not install BEAST itself**, see
[`DEVELOPMENT.md`](DEVELOPMENT.md). That workflow runs directly from the
`src/` tree.

---

## 7. Install optional testing support

To install BEAST together with the testing dependencies:

```bash
python -m pip install ".[test]"
```

For an editable development installation with testing support:

```bash
python -m pip install -e ".[test]"
```

Run the complete test suite with:

```bash
python -m pytest
```

---

## 8. Install optional documentation support

To install the documentation tool:

```bash
python -m pip install ".[docs]"
```

For an editable installation:

```bash
python -m pip install -e ".[docs]"
```

Generate the pdoc API documentation with:

```bash
pdoc beast -o docs/api
```

The generated documentation will be written under:

```text
docs/api/
```

---

## 9. Install testing and documentation support together

Both optional dependency groups can be installed at the same time:

```bash
python -m pip install ".[test,docs]"
```

For development:

```bash
python -m pip install -e ".[test,docs]"
```

---

## 10. Minimal runtime-only environment

If you only want the packages required to execute the source code, without
installing BEAST itself, install:

```bash
python -m pip install \
    "numpy>=1.23" \
    "scipy>=1.9" \
    "matplotlib>=3.6"
```

Then, from the repository root, make the `src/` directory visible to Python.

### Linux / macOS

```bash
export PYTHONPATH="$PWD/src"
```

### Windows — PowerShell

```powershell
$env:PYTHONPATH="$PWD\src"
```

You can now run:

```bash
python examples/synthetic_run.py
```

This approach is especially useful while developing the numerical core. See
[`DEVELOPMENT.md`](DEVELOPMENT.md) for the complete source-tree workflow.

---

## 11. Verify the installation

### Check the Python import

Run:

```bash
python -c "import beast; print(beast.__file__)"
```

Python should print the location from which the package was imported.

### Check package metadata

```bash
python -m pip show beast_battery_estimation_toolkit
```

The output should include information such as:

```text
Name: beast-battery-estimation-architecture-simulation-toolkit
Version: 0.2.0
Requires: matplotlib, numpy, scipy
```

### Check the command-line interface

The package defines the `beast` command.

Run:

```bash
beast --help
```

or:

```bash
python -m beast --help
```

A help message should be displayed.

### Run the synthetic example

From the repository root:

```bash
python examples/synthetic_run.py
```

This is a useful first check of the model and estimator stack.

---

## 12. Verify with the test suite

If the testing dependencies are installed:

```bash
python -m pytest
```

To run a specific test module:

```bash
python -m pytest tests/test_cell_models.py
```

To run estimator tests:

```bash
python -m pytest tests/test_estimators.py
```

To display more detail:

```bash
python -m pytest -v
```

---

## 13. Headless systems and CI environments

Matplotlib may require a non-interactive backend on servers, containers, or CI
systems without a graphical display.

### Linux / macOS

```bash
export MPLBACKEND=Agg
```

### Windows — PowerShell

```powershell
$env:MPLBACKEND="Agg"
```

Then execute tests or scripts normally:

```bash
python -m pytest
```

---

## 14. Upgrade an existing installation

When installing a newer wheel:

```bash
python -m pip install --upgrade path/to/new-wheel.whl
```

When installing from an updated source checkout:

```bash
git pull
python -m pip install --upgrade .
```

For an editable installation, source-code changes are already visible. Run:

```bash
python -m pip install -e .
```

again if package metadata or dependencies in `pyproject.toml` have changed.

---

## 15. Uninstall

Remove the installed BEAST package with:

```bash
python -m pip uninstall beast_battery_estimation_toolkit
```

This removes the BEAST package but does not automatically remove NumPy, SciPy,
Matplotlib, or other dependencies that may be shared by other Python packages.

To remove the complete isolated environment, deactivate it first:

```bash
deactivate
```

and delete `.venv`.

### Linux / macOS

```bash
rm -rf .venv
```

### Windows — PowerShell

```powershell
Remove-Item -Recurse -Force .venv
```

---

## 16. Troubleshooting

### `ModuleNotFoundError: No module named 'beast'`

If BEAST is supposed to be installed, verify:

```bash
python -m pip show beast_battery_estimation_toolkit
```

If it is not installed:

```bash
python -m pip install .
```

If you are deliberately using the source-tree workflow instead, ensure that
`src/` is on `PYTHONPATH`.

Linux / macOS:

```bash
export PYTHONPATH="$PWD/src"
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="$PWD\src"
```

---

### `pip` installs into a different Python interpreter

Use:

```bash
python -m pip ...
```

instead of calling `pip` directly.

Check:

```bash
python --version
python -m pip --version
```

---

### Python is older than 3.10

BEAST declares:

```text
requires-python = ">=3.10"
```

Create the environment with a supported interpreter, for example:

```bash
python3.11 -m venv .venv
```

or:

```bash
python3.12 -m venv .venv
```

depending on the Python versions installed on your system.

---

### Problems importing NumPy, SciPy, or Matplotlib

Upgrade the dependencies in the active virtual environment:

```bash
python -m pip install --upgrade numpy scipy matplotlib
```

Then verify:

```bash
python -c "import numpy, scipy, matplotlib; print('Dependencies OK')"
```

---

### Matplotlib display errors

For automated tests or machines without a display:

```bash
export MPLBACKEND=Agg
```

On Windows PowerShell:

```powershell
$env:MPLBACKEND="Agg"
```

---

### Editable installation does not reflect metadata changes

Editable installation reflects Python source changes immediately, but changes
to dependencies, console scripts, version numbers, or other package metadata
may require reinstalling:

```bash
python -m pip install -e .
```

---

## 17. Installation choices at a glance

| Goal | Recommended command |
|---|---|
| Use a released wheel | `python -m pip install dist/<wheel>.whl` |
| Install from repository source | `python -m pip install .` |
| Develop with package installed | `python -m pip install -e .` |
| Install with tests | `python -m pip install -e ".[test]"` |
| Install with docs | `python -m pip install -e ".[docs]"` |
| Install with tests + docs | `python -m pip install -e ".[test,docs]"` |
| Develop without installing BEAST | Install dependencies and use `PYTHONPATH=src` |

---

## 18. Recommended setup for researchers

For most users who want to run experiments and inspect the framework:

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install .
```

Verify:

```bash
python -c "import beast; print('BEAST installation OK')"
python examples/synthetic_run.py
```

For researchers who also intend to modify and validate the algorithms:

```bash
python -m pip install -e ".[test,docs]"
python -m pytest
```

Continue with [`DEVELOPMENT.md`](DEVELOPMENT.md).

---

## License

BEAST is distributed under the **GNU General Public License v3.0
(GPL-3.0)**.

See [`LICENSE`](LICENSE) for the complete license terms.
