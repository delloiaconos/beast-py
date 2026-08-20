from __future__ import annotations

import pytest

from beast.cell_models import selectCellModel, CellModel_R0R1C1, CellModel_ESC

def test_cell_model_selector_accepts_class_name():
    assert selectCellModel(" cellmodel_r0r1c1 ") is CellModel_R0R1C1
    assert selectCellModel(" ESC ") is CellModel_ESC

def test_unknown_model_has_actionable_error():
    with pytest.raises(ValueError, match="Unknown cell model"):
        selectCellModel("missing")
