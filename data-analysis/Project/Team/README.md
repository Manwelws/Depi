# Ford GoBike — Team Project

EDA + interactive dashboard for the Ford GoBike bike-sharing dataset
(February 2019 trips, preprocessed).

## Structure

```text
.
├── app.py                        # Streamlit dashboard (single entry point)
├── data/processed/               # Cleaned dataset used by app + notebook
│   └── preprocessed_fordgobike.csv
├── notebooks/                    # Phase 2 EDA & question analysis
│   └── ford_gobike_phase2_eda.ipynb
├── docs/                         # Project brief / requirements
│   └── project_requirements.md
└── src/team/                     # Shared Python package (imports, helpers)
```

## Run the dashboard

```bash
streamlit run app.py
```

Override the dataset path without moving files:

```bash
GOBIKE_DATA_CSV=/path/to/file.csv streamlit run app.py
```

## Run the notebook

```bash
jupyter notebook notebooks/ford_gobike_phase2_eda.ipynb
```

Paths inside the notebook are relative to `notebooks/`
(`../data/processed/preprocessed_fordgobike.csv`).

## Install dependencies

```bash
pip install -e .
```

Dashboard: `numpy`, `pandas`, `plotly`, `streamlit`.
Notebook extras: `matplotlib`, `seaborn`, `jupyter`.
