#!/usr/bin/python3

from distutils.core import setup

d = generate_distutils_setup(
    # #  don't do this unless you want a globally visible script
    #packages=[],
    #package_dir={}
  )
maps = d
setup(**maps)
