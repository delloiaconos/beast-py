"""Dummy Cell Model for testing purposes."""

from __future__ import annotations

from typing import Any
from beast.cell_models.base import CellModel

class CellModel_Dummy(CellModel):

    def __init__(self):
        self.Nx = 2
        self.Np = 2
        self.Nu = 1
        self.Ny = 1

    def f0(self, *args, **kwargs):
        raise NotImplementedError

    def g0(self, *args, **kwargs):
        raise NotImplementedError

    def f1x(self, *args, **kwargs):
        raise NotImplementedError

    def f1p(self, *args, **kwargs):
        raise NotImplementedError

    def g1x(self, *args, **kwargs):
        raise NotImplementedError

    def g1p(self, *args, **kwargs):
        raise NotImplementedError

    def coerce_parameters(cls, parameters: Any) -> FloatArray:
        raise NotImplementedError