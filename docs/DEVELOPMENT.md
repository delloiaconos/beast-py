# BEAST Development Guide

This document describes how to develop, test, document, and package the Python implementation of **BEAST: Battery Estimation Architecture and Simulation Toolkit**.

The development workflow is intentionally **source-tree based**: the BEAST package itself does **not** need to be installed into the virtual environment for normal development and testing. Only the external Python dependencies are installed. The source code is imported directly from `src/`.

---

## 1. Requirements

The project currently requires:

- Python **3.10 or newer**
- NumPy `>=1.23`
- SciPy `>=1.9`
- Matplotlib `>=3.6`

Development tools:

- Pytest `>=7` for automated testing
- pdoc `>=14` for API documentation

Optional release/development tools:

- `build` for creating wheels and source distributions
- `ruff` for static checks and formatting/lint support

Git is recommended for normal development.

---

## 2. Get the source code

Clone the repository and enter the project directory:

```bash
git clone https://github.com/delloiaconos/beast-py.git
cd beast
```


Do not work directly inside `dist/`, `build/`, generated documentation, or Python cache directories.

---

## 3. Create an isolated development environment

Using a virtual environment is strongly recommended so that BEAST development dependencies do not interfere with other Python projects.

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

To leave the environment later:

```bash
deactivate
```

---

## 4. Install only the required dependencies

For normal development, **do not install the BEAST package itself** with `pip install .`.

Install only the external dependencies:

```bash
python -m pip install \
  "numpy>=1.23" \
  "scipy>=1.9" \
  "matplotlib>=3.6" \
  "pytest>=7" \
  "pdoc>=14"
```

On Windows PowerShell, the same command can be written on one line:

```powershell
python -m pip install "numpy>=1.23" "scipy>=1.9" "matplotlib>=3.6" "pytest>=7" "pdoc>=14"
```

This installs the libraries required to execute, test, and document the project, while keeping the BEAST source code directly editable in the repository.

### Optional development tools

Install these only when needed:

```bash
python -m pip install build ruff
```

They are not required to run the numerical framework or its test suite.

---

## 5. Develop directly from `src/`

The project follows the standard Python `src` layout. Therefore, when the package is not installed, Python must be told where the source package is located.

### Linux / macOS

From the repository root:

```bash
export PYTHONPATH="$PWD/src"
```

### Windows PowerShell

```powershell
$env:PYTHONPATH = "$PWD\src"
```

You can verify that the source package is visible with:

```bash
python -c "import beast; print(beast.__file__)"
```

The printed path should point inside your repository, for example:

```text
.../beast-python/src/beast/__init__.py
```

This is the preferred workflow during active development because every code change is immediately visible to Python without reinstalling anything.

---

## 6. Run the test suite

From the repository root:

```bash
MPLBACKEND=Agg python -m pytest
```

The `Agg` Matplotlib backend prevents graphical windows from opening during automated tests.

On Windows PowerShell:

```powershell
$env:MPLBACKEND = "Agg"
python -m pytest
```

The current suite covers the battery models, estimators, Jacobians, binary I/O, processing workflow, pulse generation, plotting, factory functions, and the plain NumPy/dictionary API.

### Run a single test file

```bash
python -m pytest tests/test_binary_io.py
```

### Run one test function

```bash
python -m pytest tests/test_binary_io.py::test_name
```

### Run tests matching a keyword

```bash
python -m pytest -k ekf
```

### More verbose output

```bash
python -m pytest -vv
```

### Stop on the first failure

```bash
python -m pytest -x
```

A change should normally not be committed until the complete test suite passes.

---

## 7. Run the example program

With `PYTHONPATH` pointing to `src/`:

```bash
MPLBACKEND=Agg python examples/synthetic_run.py
```

This is a useful quick check after changes to battery models or estimators.

The example should execute directly from the working tree; no BEAST package installation is required.

---

## 8. Development principles

The current Python architecture deliberately separates the **numerical core** from the **MATLAB compatibility layer**.

For new development:

- use Python scalars for scalar values;
- use one-dimensional NumPy arrays for states, parameters, inputs, and outputs;
- use two-dimensional NumPy arrays for matrices, Jacobians, covariance matrices, and histories;
- use dictionaries for named configuration and result groups;
- avoid introducing new MATLAB-style container classes into numerical code;
- keep legacy dataclasses in `beast.types` only as compatibility adapters;
- normalize compatibility objects before numerical processing begins.

The numerical modules should not depend on the legacy dataclasses.

The most important supporting modules are:

```text
beast.arrays
    NumPy conversion, shape validation, scalar extraction, and field access.

beast.data
    Construction and validation of plain dictionaries used by the framework.

beast.types
    Legacy MATLAB-shaped compatibility adapters.
```

---

## 9. Numerical conventions

When modifying algorithms, preserve the conventions used by the framework.

### States and parameters

States and parameter vectors should normally be one-dimensional:

```python
x = np.array([0.85, 0.0], dtype=float)
p = np.array([0.01, 0.02, 900.0], dtype=float)
```

Avoid unnecessary `(n, 1)` MATLAB-style column arrays unless a matrix operation specifically requires them.

### Covariances and Jacobians

Matrices remain two-dimensional:

```python
sx_w = np.diag([1e-8, 1e-8])
```

### Dataset structures

Prefer dictionaries containing NumPy arrays:

```python
dataset = {
    "delta_t": delta_t,
    "t_all": time,
    "u_all": current,
    "y_exp_all": voltage,
    "x0": initial_state,
    "p0": initial_parameters,
}
```

### Binary compatibility

Legacy MATLAB binary files use MATLAB-compatible column-major ordering. 
Do not change serialization ordering without also changing compatibility tests and documenting the incompatibility.

### Floating-point comparisons

Do not compare computed floating-point arrays with `==` unless exact equality is explicitly required. In tests, use NumPy tolerance-based comparison functions such as:

```python
np.testing.assert_allclose(actual, expected, rtol=..., atol=...)
```

Choose tolerances based on the numerical meaning of the quantity being tested.

---

## 10. Adding or modifying a battery model

Battery models live in:

```text
src/beast/cell_models/
```

A model should follow the interface defined by the base model and provide the model functions required by the estimators, including the relevant state/output functions and Jacobians.

When adding a model:

1. Add the implementation module under `cell_models/`.
2. Follow the existing state and parameter ordering conventions.
3. Add pdoc-compatible docstrings.
4. Add type hints to public functions and methods.
5. Expose the model from `cell_models/__init__.py` if it is part of the public API.
6. Update `cell_models/factory.py` if selector-based construction is supported.
7. Add dimensional tests.
8. Add analytical Jacobian tests against finite differences.
9. Add at least one representative numerical evolution test.
10. Update architecture/API documentation if the public interface changes.

A model change should not be accepted solely because a simulation appears reasonable; its analytical Jacobians should remain independently testable.

---

## 11. Adding or modifying an estimator

Estimator implementations live in:

```text
src/beast/estimators/
```

When adding an estimator:

1. Derive from or follow the estimator base interface.
2. Keep estimator state internal only where it is genuinely algorithmic state.
3. Accept NumPy arrays and plain dictionary data at public numerical boundaries.
4. Avoid depending on `beast.types` compatibility dataclasses.
5. Add the estimator to `estimators/__init__.py` when public.
6. Update `estimators/factory.py` when selector-based construction is required.
7. Add initialization tests.
8. Add single-step tests where practical.
9. Add complete-run tests.
10. Test failure cases and incompatible dimensions.
11. Document covariance assumptions and any estimator-specific tuning parameters.

For Kalman-family estimators, changes to covariance propagation or Jacobian use should receive particularly careful numerical regression testing.

---

## 12. Documentation rules

Public modules, classes, methods, and functions should contain pdoc-compatible docstrings.

A useful docstring should explain:

- purpose;
- parameters and expected shapes;
- return values and shapes;
- units where important;
- algorithm-specific assumptions;
- exceptions or invalid conditions;
- compatibility behavior where relevant.

Do not merely restate the function name.

### Build API documentation

Ensure `PYTHONPATH` includes `src/`, then run:

```bash
pdoc beast -o docs/api
```

To start a local documentation server:

```bash
pdoc beast
```

The generated `docs/api/` directory is ignored by Git in the current project configuration, so it can be regenerated locally as needed.

---

## 13. Code checks

The project currently targets a maximum line length of 100 characters and Python 3.10 semantics.

If Ruff is installed:

```bash
ruff check src tests examples
```

If a future formatter is introduced, its configuration should be recorded in `pyproject.toml` and used consistently by all contributors.

Before committing, Python source files can also be syntax-checked with:

```bash
python -m compileall -q src tests examples
```

---

## 14. Recommended development cycle

A normal development iteration should be:

```text
1. Update local main branch.
2. Create a feature/fix branch.
3. Activate the virtual environment.
4. Set PYTHONPATH to src/.
5. Make a small, focused change.
6. Add or update tests for that change.
7. Run the affected tests.
8. Run the complete test suite.
9. Run the synthetic example when numerical code changed.
10. Update pdoc docstrings and Markdown documentation.
11. Run static/syntax checks.
12. Review the diff.
13. Commit with a descriptive message.
```

Example Git workflow:

```bash
git switch main
git pull --ff-only
git switch -c feature/new-cell-model

# edit source and tests

MPLBACKEND=Agg python -m pytest
ruff check src tests examples
git status
git diff
git add src tests docs
git commit -m "Add new battery cell model"
```

Keep commits focused. Avoid mixing large formatting changes with numerical algorithm changes in the same commit.

---

## 15. Regression testing for scientific code

BEAST is scientific/numerical software, so regression testing should protect both **software behavior** and **scientific behavior**.

For algorithm changes, consider storing or generating deterministic reference cases containing:

- input current;
- measured or simulated voltage;
- initial state;
- initial parameters;
- covariance matrices;
- expected state histories;
- expected parameter histories;
- expected model outputs.

Whenever possible, compare important changes against:

1. the previous Python implementation;
2. the original MATLAB implementation;
3. the C++ implementation, where available;
4. independently calculated analytical or finite-difference results.

For MATLAB/Python parity studies, run both implementations on the same `MD_*.in` data and compare the exported histories with documented absolute and relative tolerances.

Do not silently update reference values simply because a test fails. First determine whether the algorithm changed intentionally or a regression was introduced.

---

## 16. Test data

Small deterministic test data may be stored under the test tree if appropriate, for example:

```text
tests/
└── data/
    ├── model_case_01/
    └── matlab_reference_01/
```

Avoid committing large experimental datasets directly to the Git repository.

For larger datasets, consider separate release assets, archival storage, or a DOI-backed research-data repository, and document how tests can obtain them.

Tests should not depend on network access unless explicitly separated from the normal unit-test suite.

---

## 17. When an editable installation is useful

The normal workflow in this guide intentionally avoids installing BEAST itself.

However, an editable installation can be useful when testing the installed command-line interface or behavior exactly as another Python project would import it:

```bash
python -m pip install -e .
```

With testing dependencies:

```bash
python -m pip install -e ".[test]"
```

With documentation dependencies:

```bash
python -m pip install -e ".[docs]"
```

An editable install does not copy the source tree into the environment; it links the environment to the working source tree. Nevertheless, it should be considered an **optional integration-development mode**, not the default source-tree workflow described above.

To remove it:

```bash
python -m pip uninstall beast_battery_estimation_toolkit
```

---

## 18. Build release artifacts

Packaging is not required for everyday development.

When preparing a release, install the build frontend:

```bash
python -m pip install build
```

Clean previous generated artifacts:

```bash
rm -rf build dist *.egg-info src/*.egg-info
```

On Windows, remove the equivalent directories manually or with PowerShell.

Build the wheel and source distribution:

```bash
python -m build
```

Artifacts will be created under:

```text
dist/
```

Before publishing a release, test the wheel in a **fresh virtual environment** rather than assuming that a successful source-tree test guarantees correct packaging.

---

## 19. Clean-install verification

A simple release verification workflow is:

```bash
python -m venv .venv-release
source .venv-release/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/*.whl
python -c "import beast; print(beast.__file__)"
beast --help
```

Then run at least one representative numerical example against the installed wheel.

After verification:

```bash
deactivate
rm -rf .venv-release
```

---

## 20. Versioning and changelog

When preparing a new release:

1. Decide the next version number.
2. Update the version in `pyproject.toml`.
3. Update `CHANGELOG.md`.
4. Update `CITATION.cff` if it contains a release version/date.
5. Run all tests and validation checks.
6. Build the package.
7. Test the built wheel in a clean environment.
8. Commit the release changes.
9. Create an annotated Git tag.
10. Publish the GitHub release.

Example:

```bash
git tag -a v0.3.0 -m "BEAST 0.3.0"
git push origin v0.3.0
```

If the project is archived through Zenodo or another research repository, create/update the DOI-backed release after the GitHub release and update citation metadata as appropriate.

---

## 21. Changes that require special care

The following areas should be considered compatibility-sensitive:

- state-vector ordering;
- parameter-vector ordering;
- sign convention for battery current;
- OCV interpolation behavior;
- state/parameter compatibility projections;
- Jacobian definitions;
- covariance ordering and dimensions;
- MATLAB binary serialization order;
- estimator update sequence;
- clipping or boundary handling;
- public selector strings;
- returned dictionary field names.

If one of these intentionally changes, document the change in `CHANGELOG.md` and add a migration note when existing users may be affected.

---

## 22. Suggested branch naming

Examples:

```text
feature/new-cell-model
feature/new-estimator
fix/ekf-covariance-update
fix/binary-import
refactor/model-api
docs/development-guide
test/matlab-reference
```

Branch names should communicate the purpose of the work rather than the contributor's name.

---

## 23. Suggested commit style

Examples:

```text
Add R0R1C1 temperature-dependent model
Fix dual EKF covariance update
Add MATLAB parity regression test
Refactor pulse generator to plain NumPy inputs
Document estimator extension interface
```

Describe what changed. For scientific changes, the commit or pull request should also explain **why** the numerical behavior changed.

---

## 24. Before opening a pull request

Check the following:

- [ ] The change has a clear purpose.
- [ ] New numerical behavior is covered by tests.
- [ ] Existing tests still pass.
- [ ] Analytical Jacobians are checked when applicable.
- [ ] The synthetic example still runs when relevant.
- [ ] Public functions have type hints.
- [ ] Public APIs have pdoc-compatible docstrings.
- [ ] NumPy shapes and units are documented.
- [ ] The numerical layer does not introduce new dependencies on legacy dataclasses.
- [ ] Compatibility-sensitive changes are documented.
- [ ] `CHANGELOG.md` is updated when appropriate.
- [ ] Generated files, virtual environments, caches, and build products are not committed.

---

## 25. Minimal daily command sequence

For an existing clone, a typical Linux/macOS development session can be as short as:

```bash
cd REPOSITORY
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
export MPLBACKEND=Agg
python -m pytest
```

Then edit the code and repeatedly run only the relevant tests:

```bash
python -m pytest tests/test_cell_models.py
python -m pytest tests/test_estimators.py
```

Before committing:

```bash
python -m pytest
python -m compileall -q src tests examples
ruff check src tests examples   # if Ruff is installed
```

---

## 26. Re-create the environment from scratch

If the development environment becomes inconsistent, it is often better to delete it and recreate it rather than trying to repair packages individually.

Linux/macOS:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "numpy>=1.23" "scipy>=1.9" "matplotlib>=3.6" "pytest>=7" "pdoc>=14"
export PYTHONPATH="$PWD/src"
MPLBACKEND=Agg python -m pytest
```

This recreates only the external dependencies and continues to execute BEAST directly from the repository source tree.

---

## 27. Current validation baseline

At the time this guide was prepared, the current source tree passes:

```text
28 tests passed
```

The synthetic dual-EKF example also executes successfully from the source tree using `PYTHONPATH=src`.

Treat this as a baseline rather than a permanent test count: the number of tests should grow as new models, algorithms, regression cases, and scientific reference datasets are added.

---

## 28. Further documentation

Developers should also consult:

- `README.md` — project overview and user-facing introduction;
- `docs/ARCHITECTURE.md` — package architecture and extension points;
- `docs/PLAIN_DATA_API.md` — NumPy/dictionary API conventions;
- `docs/MATLAB_TO_PYTHON.md` — mapping from the original MATLAB implementation;
- `docs/CORRECTIONS.md` — documented corrections made during conversion;
- `docs/VALIDATION.md` — current automated validation and remaining parity work;
- `CHANGELOG.md` — release history;
- `CITATION.cff` — preferred scientific citation;
- `LICENSE` — GNU General Public License v3.0 terms.

---

## 29. Philosophy of the development workflow

BEAST originates from scientific work on battery modelling and state estimation. Development should therefore favor:

- reproducible numerical behavior;
- explicit assumptions;
- transparent equations and model structure;
- independent validation of derivatives and estimators;
- readable NumPy-based implementations;
- backwards compatibility where it does not obstruct a cleaner numerical core;
- traceability between scientific changes, tests, and documentation.

The objective is not only to make the code run, but to make numerical results understandable, testable, and reproducible by other researchers and developers.
