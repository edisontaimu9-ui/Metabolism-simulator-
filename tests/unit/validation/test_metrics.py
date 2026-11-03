"""Unit tests for metabosim.validation.metrics."""

import math

import pytest

from metabosim.validation.metrics import max_abs_error, mean_bias, rmse


@pytest.mark.unit
class TestMetrics:
    def test_perfect_match(self) -> None:
        values = [1.0, 2.0, 3.0]
        assert rmse(values, values) == 0.0
        assert mean_bias(values, values) == 0.0
        assert max_abs_error(values, values) == 0.0

    def test_known_values(self) -> None:
        sim, ref = [2.0, 4.0], [1.0, 1.0]
        assert mean_bias(sim, ref) == pytest.approx(2.0)
        assert rmse(sim, ref) == pytest.approx(math.sqrt((1 + 9) / 2))
        assert max_abs_error(sim, ref) == pytest.approx(3.0)

    def test_bias_sign(self) -> None:
        assert mean_bias([1.0], [3.0]) < 0

    def test_length_mismatch_rejected(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            rmse([1.0], [1.0, 2.0])

    def test_empty_rejected(self) -> None:
        with pytest.raises(ValueError, match="At least one"):
            max_abs_error([], [])
