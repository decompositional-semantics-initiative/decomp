import os
import importlib.resources

from logging import basicConfig, DEBUG

# get the data directory using importlib.resources
DATA_DIR = str(importlib.resources.files('decomp') / 'data')
basicConfig(filename=os.path.join(DATA_DIR, 'build.log'),
            filemode='w',
            level=DEBUG)

from .semantics.uds import UDSCorpus
from .semantics.uds import NormalizedUDSAnnotation
from .semantics.uds import RawUDSAnnotation
