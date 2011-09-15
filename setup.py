import os
import itertools
import platform
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "infi", "pyutils", "__version__.py")) as version_file:
    exec(version_file.read())

install_requires = []
if platform.python_version() < '2.7':
    install_requires.append('unittest2')

setup(name="infi.pyutils",
      classifiers = [
          "Programming Language :: Python :: 2.6",
          ],
      description="Misc. pure-python utilities",
      license="BSD",
      author="Rotem Yaari",
      author_email="vmalloc@gmail.com",
      #url="your.url.here",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      namespace_packages=["infi"],
      install_requires=install_requires,
      scripts=[],
      )
