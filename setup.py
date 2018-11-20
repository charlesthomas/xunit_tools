#!/usr/bin/env python
from setuptools import setup

NAME = 'xunit_tools'
DESCRIPTION = '{}: generate HTML reports and diffs from XUnit XML files'.format(NAME)

VERSION = open('{}/VERSION'.format(NAME)).read().strip()
LONG_DESC = open('README.rst').read()
LICENSE = open('LICENSE').read()
REQUIREMENTS = [open('requirements.txt').readlines()]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
]

PACKAGES = [NAME, '{}/templates'.format(NAME)]
PACKAGE_DATA = {NAME: ['VERSION', 'templates/*.html']}

ENTRY_POINTS = {'console_scripts': ['{n} = {n}.__init__:main'.format(n=NAME)]}

setup(
    name=NAME,
    version=VERSION,
    author='Charles Thomas',
    author_email='ch@rlesthom.as',
    url='https://github.com/charlesthomas/%s' % NAME,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    entry_points=ENTRY_POINTS,
)
