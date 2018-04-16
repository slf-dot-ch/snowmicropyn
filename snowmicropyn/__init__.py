from os.path import dirname, abspath, join

__version__ = '0.1.0a1'

from .profile import Profile


def git_hash():
    here = dirname(abspath(__file__))
    with open(join(here, 'githash'), encoding='utf-8') as f:
        githash = f.read().strip()
    if githash == '':
        return None
    return githash
