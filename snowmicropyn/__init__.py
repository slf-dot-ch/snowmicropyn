from os.path import dirname, abspath, join

import logging

__version__ = '1.1.0'

def githash():
    """
    Get the git hash of this release of *snowmicropyn*.

    The Hash is a string. It can be ``None``, which means you're using a non
    official release of *snowmicropyn*.
    """
    here = dirname(abspath(__file__))
    with open(join(here, 'githash'), encoding='utf-8') as f:
        hash_ = f.read().strip()
    if hash_ == '':
        return None
    return hash_


# Log version and its git hash when module is imported
log = logging.getLogger('pyngui')
log.info('snowmicropyn Version {}, Git Hash {}'.format(__version__, githash()))

from .profile import Profile
from .pnt import Pnt

from .derivatives import parameterizations as params
proksch2015 = params.get('P2015') # backwards compatibility to < v1.1.0
