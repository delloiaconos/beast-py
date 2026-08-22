# BEAST Python

**Python implementation of BEAST — Battery Estimation Algorithms and Simulation Toolkit**

`beast-py` is the Python implementation of the BEAST battery modelling and estimation framework. It provides a NumPy-based environment for simulation, algorithm development, numerical analysis, and research.

For the general project introduction, history, battery-model documentation, and links to the other implementations, see the main [BEAST repository](https://github.com/delloiaconos/beast.git).

## About this implementation

The Python implementation preserves the common BEAST model/estimator architecture while using standard Python and NumPy data structures for numerical computation.
It is intended for:

- rapid development of battery models and estimators;
- simulation and numerical experimentation;
- analysis of estimator behaviour and results;
- validation against experimental datasets;
- prototyping before or alongside a C++ implementation;
- comparison with the MATLAB reference implementation.

Battery models and estimators are kept modular so that compatible components can be combined without tying an estimator to a single cell-model implementation.

## Main capabilities

The project focuses on:

- equivalent-circuit battery models;
- State of Charge estimation;
- state-estimation algorithms;
- parameter-estimation algorithms;
- NumPy-based numerical computation;
- extensible interfaces for adding models and estimators;
- reproducible comparison with the other BEAST implementations.

The exact set of currently implemented models and estimators is defined by this repository and may differ from the C++ and MATLAB versions.

## Development

When adding a new model or estimator, keep the common interfaces stable where possible so that models and estimators remain interchangeable.

Tests should accompany changes to numerical behaviour, model equations, estimator logic, factories, and registry-related code.

## License

`beast-py` is distributed under the **GNU General Public License version 3.0
(GPL-3.0)**.

See [`LICENSE`](LICENSE) for the complete license text.
