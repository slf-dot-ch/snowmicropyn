import os
import re
import io

from setuptools import setup

# Load the package's __version__.py to get version string
here = os.path.abspath(os.path.dirname(__file__))
init_py = os.path.join(here, 'snowmicropyn', '__init__.py')
with io.open(init_py, encoding='utf-8') as f:
    VERSION = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

DESCRIPTION = """A python package to read, export and post process data (*.pnt files) recorded by 
SnowMicroPen, a snow penetration probe for scientific applications developed at SLF.
"""

readme_rst = os.path.join(here, 'README.rst')
with io.open(readme_rst, encoding='utf-8') as f:
    LONG_DESRIPTION = f.read()

setup(
    name='snowmicropyn',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESRIPTION,
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
            'examiner = snowmicropyn.examiner.app:main'
        ]
    },

    python_requires='>=3.4',
    install_requires=[
        'scipy >= 1',
        'pandas >= 0.22',
        'matplotlib >= 2',
        'pytz',
        'PyQt5 >= 5',
    ],
)
