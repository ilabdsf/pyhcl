#!/usr/bin/env python

from __future__ import print_function

from os.path import abspath, dirname, join, exists
from distutils.core import setup

try:
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.command.build_py import build_py as _build_py

import os
import sys
import subprocess

setup_dir = abspath(dirname(__file__))
version_file = join(setup_dir, 'src', 'hcl', 'version.py')

def _pre_install():
    '''Initialize the parse table at install time'''
    
    # Generate the parsetab.dat file at setup time
    dat = join(setup_dir, 'src', 'hcl', 'parsetab.dat')
    if exists(dat):
        os.unlink(dat)

    sys.path.insert(0, join(setup_dir, 'src'))
    
    import hcl
    from hcl.parser import HclParser
    parser = HclParser()
    
    print('exists', dat)


class build_py(_build_py):
    def run(self):
        self.execute(_pre_install, (), msg="Generating parse table...")
        _build_py.run(self)
        

# Automatically generate a version.py based on the git version
if exists(join(setup_dir, '.git')):
    p = subprocess.Popen(["git", "describe", "--tags", "--long", "--dirty=-dirty"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    # Make sure the git version has at least one tag
    if err:
        print("Error: You need to create a tag for this repo to use the builder")
        sys.exit(1)

    # Convert git version to PEP440 compliant version
    # - Older versions of pip choke on local identifiers, so we can't include the git commit
    v, commits, local = out.decode('utf-8').rstrip().split('-', 2)
    if commits != '0' or '-dirty' in local:
        v = '%s.post0.dev%s' % (v, commits)
    
    # Create the version.py file
    with open(version_file, 'w') as fp:
        fp.write("# Autogenerated by setup.py\n__version__ = '{0}'".format(v))

with open(join(setup_dir, 'README.rst'), 'r') as readme_file:
    long_description = readme_file.read()

with open(version_file) as fp:
    exec(compile(fp.read(), 'version.py', 'exec'), {}, locals())

install_requires=open(join(setup_dir, 'requirements.txt')).readlines()

setup(name='pyhcl',
      version=__version__,
      description='HCL configuration parser for python',
      long_description=long_description,
      author='Dustin Spicuzza',
      author_email='dustin@virtualroadside.com',
      url='https://github.com/virtuald/pyhcl',
      package_dir={'': 'src'},
      package_data={'hcl': ['src/hcl/parsetab.dat']},
      packages=['hcl'],
      scripts=["scripts/hcltool"],
      include_package_data=True,
      setup_requires=install_requires,
      install_requires=install_requires,
      cmdclass={'build_py': build_py},
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Text Processing"
      ])


