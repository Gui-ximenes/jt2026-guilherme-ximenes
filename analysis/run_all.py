"""Roda toda a pipeline de análise em sequência."""

import runpy
from pathlib import Path

SCRIPTS = [
    "01_data_prep.py",
    "02_profile_analysis.py",
    "03_location_analysis.py",
    "04_features_analysis.py",
    "05_investment_recommendation.py",
]

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    for script in SCRIPTS:
        print(f"\n\n{'#' * 70}\n# RODANDO {script}\n{'#' * 70}")
        runpy.run_path(str(here / script), run_name="__main__")
