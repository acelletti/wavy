from .exceptions import *
from .info import *
from .read import *
from .tags import *
from .wave_file import *

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
