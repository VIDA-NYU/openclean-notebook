# This file is part of the Data Cleaning Library (openclean).
#
# Copyright (c) 2018-2021 New York University.
#
# openclean is released under the Revised BSD License. See file LICENSE for
# full license details.

"""Required packages for install, test, docs, and tests."""

import os
import re

from setuptools import setup, find_packages


install_requires = [
    'future',
    'jsonschema==3.2.0',
    'openclean-core>=0.2.0',
    'datamart-profiler==0.8.1'
]


tests_require = [
    'coverage>=4.0',
    'pytest',
    'pytest-cov',
    'tox'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
    'jupyter': ['jupyter']
}


# Get the version string from the version.py file in the openclean_notebook
# package. Based on: https://stackoverflow.com/questions/458550
with open(os.path.join('openclean_notebook', 'version.py'), 'rt') as f:
    filecontent = f.read()
match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", filecontent, re.M)
if match is not None:
    version = match.group(1)
else:
    raise RuntimeError('unable to find version string in %s.' % (filecontent,))


# Get long project description text from the README.rst file
with open('README.rst', 'rt') as f:
    readme = f.read()


setup(
    name='openclean-notebook',
    version=version,
    description='openclean Notebook UI Package',
    long_description=readme,
    long_description_content_type='text/x-rst',
    keywords='data cleaning, data profiling, user interface',
    url='https://github.com/VIDA-NYU/openclean_notebook',
    author='New York University',
    author_email='heiko.muller@gmail.com',
    license_file='LICENSE',
    packages=find_packages(exclude=['tests', 'js', 'node_modules']),
    include_package_data=True,
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python'
    ]
)
