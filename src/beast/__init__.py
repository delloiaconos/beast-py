"""BEAST: Battery Estimation Architecture and Simulation Toolkit.

BEAST is a Python framework for battery modeling, state estimation, and
simulation. It provides reusable models, estimators, and supporting tools for
developing, testing, and evaluating battery management system algorithms.

The framework uses Python-native data structures, NumPy arrays, and modular
components to support research, simulation, and algorithm development.
"""

from beast.core.arrays import (
    FloatArray, 
    IntArray
)

from beast.core.data import (
    ConfigData,
    InputData,
    PlainData,
    ResultData,
    normalize_covariance,
)


from beast.cell_models import (
    CellModel,
    CellModel_H0F0A,
    CellModel_R0A1B1,
    CellModel_R0R1A1R2A2,
    CellModel_R0R1C1,
    CellModel_R0R1C1R2C2,
    CellModel_R0R1T1,
    initCellModel,
    selectCellModel,
    createCellModel,
)

from beast.estimators import (
    Estimator,
    ExposrtableVars,
    EKFdual,
    EnhancedMixAlgorithm,
    MixAlgorithm,
    OpenLoop,
    selectEstimator,
    createEstimator,
)

__version__ = "0.2.0"

__all__ = [
    "__version__",
    
    "FloatArray", "IntArray",
    "ConfigData", "InputData", "PlainData", "ResultData",
    "normalize_covariance",

    "CellModel",
    "CellModel_H0F0A",
    "CellModel_R0A1B1",
    "CellModel_R0R1A1R2A2",
    "CellModel_R0R1C1",
    "CellModel_R0R1C1R2C2",
    "CellModel_R0R1T1",
    "initCellModel", "selectCellModel", "createCellModel",

    "Estimator",
    "ExposrtableVars",
    "EKFdual",
    "EnhancedMixAlgorithm",
    "MixAlgorithm",
    "OpenLoop",
    "selectEstimator", "createEstimator",
]

