# -*- coding: utf-8 -*-
import os, sys, shutil

__dir__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(__dir__)
os.system(f"{sys.executable} ./setup.py clean --all")
shutil.rmtree(os.path.join(__dir__, "dist"), ignore_errors = True)
os.system(f"{sys.executable} ./setup.py bdist_wheel")
os.system(f"{sys.executable} ./setup.py sdist")
