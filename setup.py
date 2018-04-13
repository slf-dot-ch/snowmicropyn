from setuptools import setup
import re

with open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

with open('snowmicropyn/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='snowmicropyn',
    description='A python package to read process data recorded by SnowMicroPen© by SLF.',
    long_description=readme,
    version=version,
    author='WSL Institute for Snow and Avalanche Research SLF',
    author_email='snowmicropen@slf.ch',
    url='https://www.slf.ch/en/about-the-slf/instrumented-field-sites-and-laboratories/cold-chambers/snowmicropenr.html',
    download_url='https://github.com/slf-dot-ch/snowmicropyn/tarball/' + version,
    keywords=['SLF', 'SnowMicroPen', 'Snow Micro Pen', 'SMP', 'Snow', 'Science', 'Research', 'Probe'],
    packages=['snowmicropyn', 'snowmicropyn.examiner'],
    package_data={'snowmicropyn': ['examiner/about.html']},
    python_requires='>=3.0',
    install_requires=[
        'scipy >= 1',
        'pandas >= 0.22',
        'matplotlib >= 2',
        'pytz',
        'PyQt5 >= 5'
    ],
    entry_points={
        'gui_scripts': [
            'smpexaminer = snowmicropyn.examiner.app'
        ]
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Planning',
        'Environment :: Other Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Atmospheric Science'
    ]
)
