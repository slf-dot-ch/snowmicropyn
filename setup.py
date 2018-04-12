from setuptools import setup
from setuptools import find_packages

setup(
    name='snowmicropyn',
    description='SnowMicroPyn, an Application to view and analyze Snow Profiles recorded by Snow Micro Pen by SLF',
    version='0.1.0a1',
    author='WSL Institute for Snow and Avalanche Research SLF',
    author_email='snowmicropen@slf.ch',
    url='https://www.slf.ch/en/about-the-slf/instrumented-field-sites-and-laboratories/cold-chambers/snowmicropenr.html',
    keywords=['SLF', 'SnowMicroPen', 'Snow Micro Pen', 'SMP', 'Snow', 'Science', 'Research', 'Probe'],
    packages=find_packages(),
    package_data={'snowmicropyn': ['artwork/*']},
    python_requires='>=3',
    install_requires=[
        'scipy>=1',
        'pandas>=0.22',
        'matplotlib>=2',
        'pytz',
        'PyQt5'
    ],
    entry_points={
        'gui_scripts': [
            'smpaxaminer = snowmicropyn.examiner.app'
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
