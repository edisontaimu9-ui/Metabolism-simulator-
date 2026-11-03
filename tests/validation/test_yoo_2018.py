"""Literature plausibility check: Yoo S. J Obes Metab Syndr. 2018.

Plausibility only. See metabosim.validation.yoo2018 for why the
tolerance is wide (several inputs are assumed, not published).
"""

import pytest

from metabosim.validation import run_yoo_2018_check


@pytest.mark.validation
def test_yoo_2018_steady_state_is_plausible() -> None:
    results = run_yoo_2018_check()
    failed = [r for r in results if not r.passed]
    assert not failed, [(r.name, r.observed, r.expected) for r in failed]
