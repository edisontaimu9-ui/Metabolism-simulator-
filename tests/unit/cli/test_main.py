"""Unit tests for metabosim.cli.main."""

import tomllib
from pathlib import Path

import pytest

import metabosim
from metabosim.cli.main import _parse_activity, app

_SIM_ARGS = [
    "simulate",
    "--sex", "male", "--age", "30", "--height", "180", "--weight", "80",
    "--protein", "150", "--carbs", "300", "--fat", "70", "--days", "10",
]  # fmt: skip


@pytest.mark.unit
class TestModels:
    def test_lists_every_category(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert app(["models"]) == 0
        out = capsys.readouterr().out
        for label in ("bmr:", "tef:", "energy-balance:", "body-composition:"):
            assert label in out
        assert "mifflin_st_jeor" in out


@pytest.mark.unit
class TestSimulate:
    def test_prints_summary(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert app(_SIM_ARGS) == 0
        assert "10 days:" in capsys.readouterr().out

    def test_writes_both_reports(self, tmp_path: Path) -> None:
        out = tmp_path / "run"
        assert app([*_SIM_ARGS, "--out", str(out)]) == 0
        assert (tmp_path / "run.md").exists()
        assert (tmp_path / "run.html").exists()

    def test_markdown_only(self, tmp_path: Path) -> None:
        out = tmp_path / "run"
        assert app([*_SIM_ARGS, "--out", str(out), "--format", "md"]) == 0
        assert (tmp_path / "run.md").exists()
        assert not (tmp_path / "run.html").exists()

    def test_html_only(self, tmp_path: Path) -> None:
        out = tmp_path / "run"
        assert app([*_SIM_ARGS, "--out", str(out), "--format", "html"]) == 0
        assert (tmp_path / "run.html").exists()
        assert not (tmp_path / "run.md").exists()

    def test_model_overrides_activity_and_tracking(self, tmp_path: Path) -> None:
        args = [
            *_SIM_ARGS, "--bmr", "harris_benedict", "--tef", "fixed_percentage",
            "--energy-balance", "static_rule", "--adaptive", "threshold",
            "--activity", "6:1", "--body-fat", "20", "--glycogen", "400",
            "--name", "Demo", "--fiber", "20", "--alcohol", "0",
        ]  # fmt: skip
        assert app(args) == 0

    def test_invalid_days_reports_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        args = [*_SIM_ARGS[:-1], "0"]
        assert app(args) == 2
        assert "error:" in capsys.readouterr().err

    def test_unknown_model_reports_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert app([*_SIM_ARGS, "--bmr", "nope"]) == 2
        assert "error:" in capsys.readouterr().err


@pytest.mark.unit
class TestParseActivity:
    def test_valid(self) -> None:
        entry = _parse_activity("6:1.5")
        assert entry.met == 6.0 and entry.duration_hours == 1.5

    @pytest.mark.parametrize("bad", ["6", "a:b", "0:1", "6:1:2"])
    def test_invalid(self, bad: str) -> None:
        import argparse

        with pytest.raises(argparse.ArgumentTypeError):
            _parse_activity(bad)


@pytest.mark.unit
class TestArgumentErrors:
    def test_missing_required_returns_2(self) -> None:
        assert app(["simulate"]) == 2

    def test_no_command_returns_2(self) -> None:
        assert app([]) == 2

    def test_version_flag_returns_0(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert app(["--version"]) == 0
        assert metabosim.__version__ in capsys.readouterr().out


@pytest.mark.unit
class TestPackaging:
    def test_version_matches_pyproject(self) -> None:
        root = Path(__file__).resolve().parents[3]
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        assert data["project"]["version"] == metabosim.__version__

    def test_entry_point_target_exists(self) -> None:
        root = Path(__file__).resolve().parents[3]
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        target = data["project"]["scripts"]["metabosim"]
        assert target == "metabosim.cli.main:app"
        assert callable(app)


@pytest.mark.unit
class TestValidate:
    def test_passing_checks_exit_0(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert app(["validate"]) == 0
        out = capsys.readouterr().out
        assert "[PASS] yoo_2018_steady_state_weight" in out
        assert "plausibility check" in out

    def test_failing_check_exit_1(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from metabosim.cli import main as cli_main
        from metabosim.validation import check_value

        monkeypatch.setattr(
            cli_main,
            "run_yoo_2018_check",
            lambda: [check_value("x", 50.0, 75.0, 5.0, "kg", "d")],
        )
        assert app(["validate"]) == 1
        assert "[FAIL] x" in capsys.readouterr().out


@pytest.mark.unit
def test_python_dash_m_entry_point() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "metabosim", "models"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "mifflin_st_jeor" in result.stdout
