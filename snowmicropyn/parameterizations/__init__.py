# We want the effort to add new parameterizations to be minimal and contained
# in a single file. However, at some place these files need to be imported.
# This is done in profile.py by importing * from here thus calling this code.
# We look for .py files and collect them in __all__ to load them.

from os.path import dirname, basename, isfile, join
import glob

# collect all .py files of this directory except this file:
params = glob.glob(join(dirname(__file__), "*.py"))
params = [pp for pp in params if isfile(pp)]
params = [pp for pp in params if not pp.endswith('__init__.py')]
params = [basename(pp)[:-3] for pp in params] # remove extension

__all__ = params # load all py files of this directory as modules
