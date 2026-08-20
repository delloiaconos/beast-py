"""Battery equivalent-circuit models."""

from beast.cell_models.base import CellModel
from beast.cell_models.factory import (
    CELL_MODEL_REGISTRY,
    initCellModel,
    selectCellModel,
    createCellModel,
)

from beast.cell_models.h0f0a import CellModel_H0F0A
from beast.cell_models.r0a1b1 import CellModel_R0A1B1
from beast.cell_models.r0r1c1 import CellModel_R0R1C1
from beast.cell_models.r0r1c1r2c2 import CellModel_R0R1C1R2C2
from beast.cell_models.r0r1t1 import CellModel_R0R1T1
from beast.cell_models.esc import CellModel_ESC

__all__ = [
    "CELL_MODEL_REGISTRY",
    "initCellModel",
    "selectCellModel",
    "createCellModel",
    "CellModel",
    "CellModel_H0F0A",
    "CellModel_R0A1B1",
    "CellModel_R0R1C1",
    "CellModel_R0R1C1R2C2",
    "CellModel_R0R1T1",
    "CellModel_ESC",
]
