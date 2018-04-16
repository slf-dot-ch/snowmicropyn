#!/usr/bin/env python

import os
import re

from setuptools import setup

# Load the package's __version__.py to get version string
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'snowmicropyn', '__init__.py')) as f:
    VERSION = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='snowmicropyn',
    version=VERSION,
    description='A python package to read and process data recorded by SnowMicroPen© by SLF',
    author='WSL Institute for Snow and Avalanche Research SLF',
    author_email='snowmicropen@slf.ch',
    keywords=['SLF', 'SnowMicroPen', 'Snow Micro Pen', 'SMP', 'Snow', 'Science', 'Research'],
    url='https://github.com/slf-dot-ch/snowmicropyn',
    license='GPL',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Planning',
        'Environment :: Other Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Atmospheric Science'
    ],

    packages=['snowmicropyn', 'snowmicropyn.examiner'],
    package_data={
        'snowmicropyn': ['githash'],
        'snowmicropyn.examiner': ['about.html'],
    },
    include_package_data=True,
    entry_points={
        'gui_scripts': [
            'smpexaminer = snowmicropyn.examiner.app:main'
        ]
    },

    python_requires='>=3.0',
    install_requires=[
        'scipy >= 1',
        'pandas >= 0.22',
        'matplotlib >= 2',
        'pytz',
        'PyQt5 >= 5',
    ],
)
