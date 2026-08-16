# BEAST Development Guide

This guide describes the recommended workflow for developing **BEAST — Battery Estimation Architecture and Simulation Toolkit**.

For installation-only instructions, see [`INSTALLATION.md`](INSTALLATION.md).

## Requirements

BEAST requires Python 3.10 or newer. Use a virtual environment for development.

Create and activate one, then install BEAST in editable mode with its declared test and documentation extras:

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test,docs]"
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test,docs]"
```

Ruff and the Python build frontend are useful development tools but are not currently included in the optional dependency groups:

```bash
python -m pip install ruff build
```

## Project structure

```text
src/beast/
├── cell_models/     # Battery-model base class, implementations, and registry
├── core/            # Shared array types and small data/numerical helpers
├── estimators/      # Estimator base class, implementations, and registry
├── io/              # Binary data I/O
└── __init__.py      # Public package API

tests/               # Unit and numerical tests
docs/                # Project documentation
```

Keep subsystem responsibilities clear:

- `core` should remain small and broadly reusable;
- model-specific helpers belong in `cell_models`;
- estimator-specific helpers belong in `estimators`;
- file-format concerns belong in `io`;
- fixtures, stubs, and dummy implementations used only by tests belong in `tests`.

## Running tests

Run the complete suite from the repository root:

```bash
python -m pytest
```

Useful variants:

```bash
python -m pytest -v
python -m pytest -v --exitfirst
python -m pytest -x
python -m pytest tests/test_cellmodels.py
python -m pytest -k estimator
```

Do not document a fixed number of passing tests. The expected baseline is that the complete suite passes for supported Python versions.

## Code checks

If Ruff is installed:

```bash
ruff check src tests
```

The current Ruff configuration targets Python 3.10 and uses a maximum line length of 100 characters.

Before committing, run both tests and lint checks:

```bash
python -m pytest
ruff check src tests
```

## Development principles

BEAST is scientific software. Numerical behavior, API clarity, and testability are all part of correctness.

Prefer code that:

- makes units, array shapes, and sampling assumptions explicit;
- rejects invalid numerical input instead of propagating it silently;
- keeps battery-model physics separate from estimator behavior;
- minimizes coupling between models and estimators;
- can be tested with small, deterministic fixtures;
- uses clear Python APIs without requiring knowledge of the original MATLAB implementation.

Compatibility with existing behavior matters, but new APIs should favor clear and documented Python semantics.

## Numerical conventions

Use NumPy arrays for numerical vectors and matrices, and reuse the aliases in `beast.core.arrays` when they improve type clarity.

Document non-obvious shapes and units. Typical symbols are:

```text
x   state vector
p   parameter vector
u   input vector
y   measurement vector
P   covariance matrix
```

### Finite values

Physical and numerical inputs should normally be finite. When adding validation, consider explicit checks such as:

```python
np.isfinite(value)
np.all(np.isfinite(array))
```

A comparison such as `value <= 0` does not reject `NaN` on its own.

### Covariance matrices

Validate the assumptions required by the algorithm. Depending on the use case, this can include:

- correct shape;
- finite values;
- symmetry;
- positive semidefiniteness or positive definiteness.

Estimator tests should also detect numerical loss of covariance symmetry when relevant.

### Floating-point tests

Use tolerant comparisons for floating-point results:

```python
np.testing.assert_allclose(actual, expected, rtol=..., atol=...)
```

Choose tolerances based on the operation being tested.

## Working on battery models

Built-in models derive from `beast.cell_models.CellModel`.

The current registry supports:

- `H0F0A`;
- `R0A1B1`;
- `R0R1C1`;
- `R0R1C1R2C2`;
- `R0R1T1`.

When adding a model:

1. create a module under `src/beast/cell_models/`;
2. implement the required `CellModel` operations;
3. define required data and dimensions clearly;
4. add the class to `CELL_MODEL_REGISTRY`;
5. export it from `beast.cell_models` and, if public, from `beast`;
6. add tests.

Model tests should cover dimensions, state/output equations, invalid inputs, state and parameter coercion, boundary behavior, and analytical Jacobians against finite-difference approximations where applicable.

## Working on estimators

Built-in estimators derive from `beast.estimators.Estimator`.

The current registry supports:

- `EKFDUAL`;
- `MIXALGORITHM`;
- `ENHANCEDMIXALGORITHM`;
- `OPENLOOP`.

When adding an estimator:

1. create a module under `src/beast/estimators/`;
2. implement the base estimator interface;
3. make assumptions about model dimensions and sampling time explicit;
4. add the class to `ESTIMATOR_REGISTRY`;
5. export it from `beast.estimators` and, if public, from `beast`;
6. add numerical tests.

Estimator tests should cover initialization, prediction, measurement updates, covariance behavior, state/parameter coercion, multi-step trajectories, and failure cases.

Keep fake models and other estimator test scaffolding under `tests/`, not in production modules.

## Model/estimator boundaries

A battery model should describe the system being estimated. Estimator-specific tuning such as process noise, measurement noise, and estimator covariance belongs conceptually to the estimator side of the architecture.

Estimators should depend only on the model behavior they require. If this boundary is formalized further, prefer an estimator-facing `Protocol` while retaining the abstract `CellModel` base class for built-in BEAST models.

## Sampling time

Sampling time must have one unambiguous meaning throughout a simulation.

When changing `delta_t` handling:

- require a finite, strictly positive value;
- document which object owns it;
- avoid independent model and estimator values that can silently disagree;
- add tests for any override behavior.

Changes in this area require particular care because the current code passes timing information to both models and estimators.

## Binary I/O

Legacy binary loading is implemented in `beast.io.binary` and is used by `initCellModel()`.

When changing binary I/O:

- preserve the expected element order;
- validate file sizes and requested shapes;
- keep file-format logic out of numerical model equations;
- use temporary files/directories in tests;
- keep the matrix-order regression tests passing.

## Factories and registries

Model and estimator selection is registry-based:

```python
from beast import selectCellModel, selectEstimator

model_class = selectCellModel("R0R1C1")
estimator_class = selectEstimator("EKFDUAL")
```

When modifying a registry, add factory tests and update public documentation.

Invalid selectors should raise clear, actionable errors.

## Documentation

Documentation must describe the repository as it exists now.

Before documenting a command, module, script, or file, verify that it exists and works. In particular:

- do not reference example scripts that are not in the repository;
- do not document a CLI unless a working CLI is shipped;
- do not hard-code test counts;
- keep installation commands synchronized with `pyproject.toml`;
- document important units, shapes, assumptions, and exceptions in public APIs.

API documentation can be generated with the declared `docs` extra:

```bash
pdoc beast
```

For a local documentation server:

```bash
pdoc beast --http localhost:8080
```

## Building distributions

Install the build frontend if necessary:

```bash
python -m pip install build
```

Build the wheel and source distribution with:

```bash
python -m build
```

Artifacts are written to `dist/`.

Before a release, test the built wheel in a clean virtual environment rather than relying only on source-tree imports:

```bash
python -m venv .venv-wheel
# activate .venv-wheel
python -m pip install --upgrade pip
python -m pip install dist/*.whl
python -c "import beast; print(beast.__version__)"
python -c "from beast import selectCellModel; print(selectCellModel('R0R1C1').__name__)"
```

This catches packaging problems that can be hidden by the repository's `src` test path.

## Versioning

The package version is currently present in both:

```text
pyproject.toml
src/beast/__init__.py
```

Keep them synchronized when preparing a release.

## Scientific regression tests

Unit tests are necessary but not sufficient for scientific algorithms.

For models and estimators, maintain compact reference datasets when practical. Useful reference data includes inputs, initial conditions, state trajectories, parameter trajectories, model outputs, and covariance trajectories.

Expected results should come from a trusted implementation, analytical result, or independently validated dataset. Avoid generating reference results through the same code path that the test is intended to validate.

## Pull-request checklist

- [ ] The complete test suite passes.
- [ ] New behavior has tests.
- [ ] Numerical changes have appropriate tolerance-based or regression tests.
- [ ] Ruff reports no new issues.
- [ ] Public API changes are documented.
- [ ] Installation instructions still match `pyproject.toml`.
- [ ] Test-only implementations remain under `tests/`.
- [ ] Registry changes include selector tests.
- [ ] Documentation references only files and features that exist.
- [ ] Packaging changes have been verified using a built wheel.

## Recommended daily workflow

```bash
# activate the virtual environment
python -m pip install -e ".[test,docs]"

# edit source and tests
python -m pytest
ruff check src tests
```

For release or packaging changes, also run:

```bash
python -m build
```

and verify the resulting wheel in a clean environment.
