import sys
import os
import multiprocessing

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.main import start_app

if __name__ == "__main__":
    multiprocessing.freeze_support()
    start_app()