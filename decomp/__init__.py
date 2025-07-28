import importlib.resources
import os
from logging import DEBUG, basicConfig


# get the data directory using importlib.resources
DATA_DIR = str(importlib.resources.files('decomp') / 'data')
basicConfig(filename=os.path.join(DATA_DIR, 'build.log'),
            filemode='w',
            level=DEBUG)

from .semantics.uds import NormalizedUDSAnnotation, RawUDSAnnotation, UDSCorpus
