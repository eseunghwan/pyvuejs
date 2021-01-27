# -*- coding: utf-8 -*-
import os, sys, shutil
from glob import glob

__dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(__dir__)
os.system(f"{sys.executable} -m pip uninstall pyvuejs -y")
os.system(f"{sys.executable} ./dev_scripts/make_dist.py")
try:
    whl = glob(os.path.join(__dir__, "dist", "pyvuejs*.whl"))[0]
    os.system(f"{sys.executable} -m pip install {whl}")
except IndexError:
    pass
