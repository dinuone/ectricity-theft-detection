"""
Keeps the notebooks in the right order.

Each notebook calls get_inputs_ready('<its own file name>') before it loads
anything. If a file it reads from the data folder is missing, the notebook that
makes that file is run first. That notebook's own inputs are checked the same
way, so the whole chain back to data.csv gets filled in.

It only checks that the files are there, not that they are up to date. If you
change an earlier notebook, run it again yourself (or delete its output files
and the next notebook will run it for you).
"""

import os
import sys
import time
import hashlib
import tempfile
import subprocess
import importlib.util

NOTEBOOK_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(NOTEBOOK_DIR, '..', 'data')

# One entry per notebook, in the order they run.
# 'reads' = files in data/ the notebook loads, 'makes' = files in data/ it saves.
# 'time' is only for the message, measured on a 2-core machine.
STEPS = [
    {
        'notebook': 'data_cleaning_split.ipynb',
        'reads': ['data.csv'],
        'makes': ['data_cleaned.csv', 'data_train.csv', 'data_test.csv', 'split_info.csv'],
        'time': 'about 2 min',
    },
    {
        'notebook': 'features_pca.ipynb',
        'reads': ['data_cleaned.csv', 'split_info.csv'],
        'makes': ['features.csv', 'feature_info.json'],
        'time': 'about 10 min',
    },
    {
        'notebook': 'svm_model.ipynb',
        'reads': ['features.csv', 'feature_info.json', 'split_info.csv'],
        'makes': ['svm_test_predictions.csv', 'svm_info.json'],
        'time': 'about 45 min',
    },
    # When the random forest notebook is added, give it an entry here the same way.
]


def find_step(notebook):
    for step in STEPS:
        if step['notebook'] == notebook:
            return step
    raise ValueError(f"{notebook} is not listed in STEPS in pipeline.py. Add an entry for it first.")


def find_maker(file_name):
    # the step whose notebook saves this file, or None if no notebook makes it (like data.csv)
    for step in STEPS:
        if file_name in step['makes']:
            return step
    return None


def run_notebook(step):
    notebook = step['notebook']

    if importlib.util.find_spec('nbconvert') is None:
        raise ImportError("nbconvert is needed to run the earlier notebooks. "
                          "Install it with: pip install nbconvert")

    print(f"Running {notebook} ({step['time']})...", flush=True)
    start = time.time()

    # The notebook is run with the same Python that is running this one. The run's copy
    # goes to a temporary folder, so the notebook file itself (and its saved outputs)
    # stays as it is. Its data files and figures are still saved as normal.
    with tempfile.TemporaryDirectory() as temp_folder:
        command = [sys.executable, '-m', 'nbconvert', '--to', 'notebook', '--execute', notebook,
                   '--output-dir', temp_folder,
                   '--ExecutePreprocessor.kernel_name=python3',
                   '--ExecutePreprocessor.timeout=-1']
        result = subprocess.run(command, cwd=NOTEBOOK_DIR, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr[-4000:])
        raise RuntimeError(f"{notebook} stopped with an error (the end of its output is above). "
                           f"Open it, fix the error, and run this cell again.")

    minutes = (time.time() - start) / 60
    print(f"Finished {notebook} in {minutes:.1f} min.", flush=True)


def get_inputs_ready(notebook):
    step = find_step(notebook)

    for file_name in step['reads']:
        path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(path):
            maker = find_maker(file_name)
            if maker is None:
                raise FileNotFoundError(f"data/{file_name} is missing and none of the notebooks make it. "
                                        f"Put it in the data folder by hand (data.csv is the raw SGCC file).")

            print(f"data/{file_name} is missing, so {maker['notebook']} has to run first.")
            # the earlier notebook might be missing some of its own inputs too
            get_inputs_ready(maker['notebook'])
            run_notebook(maker)

            if not os.path.exists(path):
                raise RuntimeError(f"{maker['notebook']} ran, but data/{file_name} is still missing.")

    print(f"All inputs for {notebook} are in place.")