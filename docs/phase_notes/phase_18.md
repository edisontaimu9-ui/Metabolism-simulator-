# Phase 18: Command Line and Packaging

**Status:** Complete

## What was built

- **`metabosim.cli.main`**: a standard-library (`argparse`) command line,
  so no new dependency. Commands:
  - `metabosim models`: list registered model IDs per component.
  - `metabosim simulate ...`: run a constant-plan simulation, print a
    summary, optionally write Markdown and/or HTML reports.
  - `metabosim validate`: run the built-in validation checks; exit
    status 1 if any fail.
  - `app(argv)` returns the exit status (0 ok, 1 validation failure, 2
    invalid input), so it works as the console entry point and in tests.
- **`python -m metabosim`** via `metabosim/__main__.py`.
- **Packaging**: `py.typed` marker, package-data entry for dataset JSON
  files, version bumped to 0.2.0 (kept in sync between
  `pyproject.toml` and `metabosim/__init__.py`, with a test enforcing
  it), development status classifier moved from Pre-Alpha to Alpha.
- Removed the `*/cli/*` coverage exclusion from `pyproject.toml`.

## Example

```bash
metabosim simulate --sex male --age 30 --height 180 --weight 80 \
  --protein 150 --carbs 300 --fat 70 --activity 6:1 --days 90 \
  --body-fat 20 --glycogen 400 --out reports_out/demo
```

## Design decisions

1. **`argparse`, not a CLI framework.** The original entry point named
   `app`, which suggests Typer, but that would add a dependency for a
   small command set. `app` is kept as the entry point name.
2. **Constant plan only.** The CLI takes one daily plan. Day-by-day
   varying plans remain available through the Python API.
3. **Errors are messages, not tracebacks.** Invalid model IDs or values
   print `error: ...` and exit with status 2.

## Verified

- A wheel builds (`metabosim-0.2.0`), contains `py.typed` and the
  validation modules, and declares the `metabosim` console script.
- Tests cover every command, argument errors, and the entry point.
  `__main__.py` is exercised through a subprocess test, so coverage
  tools do not count it (4 lines).

## Not done

- `author` in `pyproject.toml` is still the placeholder "Your Name".
- No release or publishing workflow (PyPI, CI). The package has not been
  uploaded anywhere.
- The `gui` optional dependency (PyQt6) has no code behind it.
- Several roadmap items remain thin by design, notably validation data
  (see Phase 17).

## Verification commands

```bash
pip install -e ".[dev]"
pytest
pytest --doctest-modules src/metabosim
mypy --strict src/metabosim
black --check src tests
ruff check src tests
pip wheel . --no-deps -w dist
```
