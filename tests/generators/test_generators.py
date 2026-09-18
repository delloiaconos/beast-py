"""Tests for the generic profile-generator interface."""

import pytest

from beast.generators.base import Generator


def test_generator_is_abstract():
    with pytest.raises(TypeError):
        Generator()
