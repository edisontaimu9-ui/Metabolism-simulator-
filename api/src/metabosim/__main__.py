"""Enables ``python -m metabosim``."""

import sys

from metabosim.cli.main import app

if __name__ == "__main__":
    sys.exit(app())
