import os

from pkg_resources import resource_filename
from logging import basicConfig, DEBUG

DATA_DIR = resource_filename('decomp', 'data/')
basicConfig(filename=os.path.join(DATA_DIR, 'build.log'),
            filemode='w',
            level=DEBUG)

from .semantics.uds import UDSCorpus, UDSDataset
