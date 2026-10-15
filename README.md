# Electricity theft detection

Group assignment for T5022 Fundamentals of Machine Learning. We use the SGCC (State Grid Corporation of China) electricity consumption dataset to detect customers who steal electricity, and compare two classical supervised learning algorithms on the same task.

Dataset: https://github.com/henryRDlab/ElectricityTheftDetection

## Project layout

```
data/        data files (not in git, see below)
figures/     plots saved by the notebooks
notebooks/   the analysis, one notebook per step
```

## Notebooks and the order they run in

| Order | Notebook | Reads from data/ | Saves to data/ |
|---|---|---|---|
| 1 | `data_cleaning_split.ipynb` | `data.csv` | `data_cleaned.csv`, `data_train.csv`, `data_test.csv`, `split_info.csv` |
| 2 | `features_pca.ipynb` | `data_cleaned.csv`, `split_info.csv` | `features.csv`, `feature_info.json` |

The model notebooks come after these and read `features.csv`.

## How to run

1. Download the SGCC data from the link above and save it as `data/data.csv`. The data folder is in `.gitignore` because the files are too large for git.
2. Open any notebook and run all cells.

You do not have to run the earlier notebooks first. Each notebook calls `get_inputs_ready` from `notebooks/pipeline.py` before it loads anything. If a file it needs is missing, the notebook that makes it is run first, and that notebook's own inputs are checked the same way, all the way back to `data.csv`. Notebooks whose files are already there are not run again.

## Why pipeline.py exists

Each notebook reads files that the one before it saves. Since the data folder is not in git, none of those files exist after a fresh clone. Without `pipeline.py` you had to remember the order and run each notebook by hand, or the next one stopped with a `FileNotFoundError`.

With it:

- any notebook can be run on its own after a fresh clone, as long as `data/data.csv` is in place
- nobody has to remember which notebook makes which file
- the order of the steps and the files each one reads and saves are written down in one place (`STEPS` in `pipeline.py`)
- the earlier notebook runs as a temporary copy, so its saved outputs in git are not changed
- if something goes wrong, the error says which notebook failed or which file is missing

It only checks that the files exist, not that they are up to date. If you change an earlier notebook, run it again yourself, or delete its output files and the next notebook will run it for you.

## Adding a new notebook

Add an entry for it to `STEPS` in `notebooks/pipeline.py` with the files it reads and saves. Then put this at the top of its loading cell:

```python
get_inputs_ready('<notebook file name>.ipynb')
```
