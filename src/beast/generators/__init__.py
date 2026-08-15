"""Input-profile generators for BEAST simulations."""

from beast.generators.base import Generator
from beast.generators.constant_current import Generator_ConstantCurrent
from beast.generators.pulse import Generator_Pulse

__all__ = [
    "Generator",
    "Generator_ConstantCurrent",
    "Generator_Pulse",
]
