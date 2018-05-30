from os.path import dirname, abspath, join

import logging

__version__ = '1.0.0a2'


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
log = logging.getLogger(__name__)
log.info('snowmicropyn Version {}, Git Hash {}'.format(__version__, githash()))

from .profile import Profile
from .pnt import Pnt
