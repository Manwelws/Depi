"""Dashboard entry point (legacy path) — delegates to the single implementation.

`streamlit run dashboard/app.py` and `streamlit run app.py` serve the same
dashboard, so the dashboard code has a single source of truth.
"""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent.parent / "app.py"), run_name="__main__")