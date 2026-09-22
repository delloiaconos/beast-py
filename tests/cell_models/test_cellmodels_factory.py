from __future__ import annotations

import pytest

from beast.cell_models import (
    CellModel_R0R1A1R2A2,
    CellModel_R0R1C1,
    selectCellModel,
)

def test_cell_model_selector_accepts_class_name():
    assert selectCellModel(" cellmodel_r0r1c1 ") is CellModel_R0R1C1

def test_cell_model_selector_includes_r0r1a1r2a2():
    assert selectCellModel(" r0r1a1r2a2 ") is CellModel_R0R1A1R2A2

def test_unknown_model_has_actionable_error():
    with pytest.raises(ValueError, match="Unknown cell model"):
        selectCellModel("missing")
