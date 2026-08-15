# BEAST: Battery Estimation Architecture and Simulation Toolkit

A Python framework for battery modelling, state estimation, and parameter estimation, evolved from academic research on Battery Management Systems at the Università degli Studi di Salerno.

![BEAST Logo](assets/beast-logo.png)

## What is BEAST?

BEAST is a structured Python implementation of a battery-estimation framework originally developed in MATLAB for the study of lithium-ion battery models and real-time state estimators. 
The current codebase preserves the model/estimator architecture of the original work while using standard Python and NumPy data structures for numerical computation.

It provides a modular architecture in which battery models and estimation
algorithms can be developed independently and combined for simulation,
research, and experimental validation.

The framework is a Python evolution of an earlier MATLAB implementation and
uses standard Python and NumPy data structures for numerical computation.

## Project Origins

The project originates from my Bachelor's Degree Thesis in Electronic Engineering at the Università degli Studi di Salerno:
*Hardware/Software Co-Design di uno stimatore dello stato di batterie agli ioni di litio* (academic year 2012–2013). 

The work continued during the following years through undergraduate research
activities on battery modelling and Battery Management Systems at the same
university.

The original research investigated battery modelling, State of Charge (SoC) and parameter estimation, MATLAB simulation, C++ implementation, and real-time execution on an FPGA-based Nios II embedded platform. 

BEAST brings that work into a modern Python framework intended for research,
teaching, simulation, and further development.

## Features

- Modular battery-model architecture
- Interchangeable state-estimation algorithms
- Parameter-estimation support
- Equivalent-circuit battery models
- State of Charge (SoC) estimation
- NumPy-based numerical implementation
- Architecture derived from the original MATLAB research framework
- Extensible interfaces for implementing new models and estimators

## Contributing

Contributions are welcome, particularly in areas that continue the original research direction, such as:

- additional equivalent-circuit models;
- temperature-dependent models;
- hysteresis modelling;
- improved parameter-identification techniques;
- additional state estimators such as UKF or particle filters;
- SoH-oriented estimators;
- ageing models;
- experiment-data importers;
- benchmarking against public battery datasets;
- embedded-oriented numerical implementations;
- improved documentation and examples.

When adding a new model, keep the existing model interface where possible so that estimators remain interchangeable.

## Citation and attribution

If you use BEAST in academic work, please cite the repository and, when relevant to the algorithms or historical implementation, the original thesis and the scientific literature on which the implemented estimators are based.

### License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

Copyright © Salvatore Dello Iacono.

You are free to use, study, modify, and redistribute this software under the terms of the GNU General Public License, Version 3, dated 29 June 2007.

The full license terms are provided in the LICENSE file included with this repository.

This software is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

For more information about the GNU GPL v3.0, see the [`LICENSE`](LICENSE) file or visit GNU Project website.

### Academic Use

If you use this software, its battery models, estimation algorithms, or results obtained with this framework in a scientific publication, thesis, report, or other academic work, please cite this repository.

If you modify or extend the framework for scientific work, please clearly describe the modifications and cite the original project.

See [`CITATION.cff`](CITATION.cff) for the preferred citation.


## Acknowledgements

The original research was conducted at the Università degli Studi di Salerno.

The foundational thesis is:
```
    Salvatore Dello Iacono, Hardware/Software Co-Design di uno stimatore dello stato di batterie agli ioni di litio, Bachelor's Degree Thesis in Electronic Engineering, Università degli Studi di Salerno, academic year 2012–2013.
```
Bachelor's thesis supervision:

- Prof. Walter Zamboni (Università degli Studi di Salerno)— Supervisor
- Prof. Nicola Femia (Università degli Studi di Salerno) — Co-supervisor
- Prof. Federico Baronti (Università di Pisa) — Co-supervisor