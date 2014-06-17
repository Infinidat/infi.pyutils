import os
import sys
import itertools
import platform
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "infi", "pyutils", "__version__.py")) as version_file:
    exec(version_file.read())

install_requires = ["mock", "six", "emport"]
if sys.version_info < (2, 7):
    install_requires.append('unittest2')
    install_requires.append('ordereddict')

setup(name="infi.pyutils",
      classifiers = [
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          ],
      description="Misc. pure-python utilities",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      version=__version__,
      packages=['infi.pyutils'],
      namespace_packages=["infi"],
      install_requires=install_requires,
      zip_safe=False,
      scripts=[],
      )
