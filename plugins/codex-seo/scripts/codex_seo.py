#!/usr/bin/env python3
"""Codex entrypoint for the managed SEO runtime, with no external imports."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().with_name("runtime.py")), run_name="__main__")
