#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
  packages=['rtk_tools'],
  package_dir={'': 'src'},
  scripts=['script/recipe_mixer.py']
)

setup(**d)
