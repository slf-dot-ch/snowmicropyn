from os.path import dirname, abspath, join

from .profile import Profile
from .pnt import Pnt

import logging

__version__ = '0.1.dev7'


def githash():
    """
    Get the git hash of this release of snowmicropyn.
    :return: Hash as a string, None in case its a non official release.
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
