import pytest

from copy import deepcopy
from typing import List

from decomp.semantics.uds.metadata import _dtype
from decomp.semantics.uds.metadata import UDSDataType
from decomp.semantics.uds.metadata import UDSPropertyMetadata
from decomp.semantics.uds.metadata import UDSAnnotationMetadata

def test_dtype():
    assert _dtype('int') is int
    assert _dtype('str') is str
    assert _dtype('float') is float
    assert _dtype('bool') is bool
    # assert _dtype('List[str]') is List[str]
    # assert _dtype('List[int]') is List[int]
    # assert _dtype('List[bool]') is List[bool]
    # assert _dtype('List[float]') is List[float]

class TestUDSDataType:

    catdict = {'int': [1, 2, 3, 4, 5],
               'str': ['yes', 'maybe', 'no']}

    def test_init_simple(self):
        UDSDataType(datatype=str)
        UDSDataType(datatype=int)
        UDSDataType(datatype=bool)
        UDSDataType(datatype=float)

    def test_init_categorical(self):
        for t, c in self.catdict.items():
            for o in [True, False]:
                t = int if t == 'int' else str
                UDSDataType(datatype=t,
                            categories=c,
                            ordered=o)

    def test_from_dict_simple(self):
        UDSDataType.from_dict({'datatype': 'str'})        
        UDSDataType.from_dict({'datatype': 'int'})
        UDSDataType.from_dict({'datatype': 'bool'})
        UDSDataType.from_dict({'datatype': 'float'})

    def test_from_dict_categorical(self):
        # the name for the categories key is "categories"
        with pytest.raises(KeyError):
            UDSDataType.from_dict({'datatype': 'int',
                                   'category': [1, 2, 3, 4, 5],
                                   'ordered': True})

        # floats cannot be categorical
        with pytest.raises(ValueError):
            UDSDataType.from_dict({'datatype': 'float',
                                   'categories': [1, 2, 3, 4, 5],
                                   'ordered': True})

        # these are good
        for t, c in self.catdict.items():
            for o in [True, False]:
                dt = UDSDataType.from_dict({'datatype': t,
                                            'categories': c,
                                            'ordered': o})

                assert dt.is_categorical
                assert dt.is_ordered_categorical == o

                if o:
                    assert dt.categories == c
                else:
                    assert dt.categories == set(c)


metadata_example = {'protoroles': {'awareness': {'annotators': ['protoroles-annotator-8',
                                                                'protoroles-annotator-9'],
                                                 'confidence': {'categories': [0, 1],
                                                                'datatype': 'int',
                                                                'ordered': False},
                                                 'value': {'categories': [1, 2, 3, 4, 5],
                                                           'datatype': 'int',
                                                           'ordered': True}},
                                   'change_of_location': {'annotators': ['protoroles-annotator-0',
                                                                         'protoroles-annotator-1'],
                                                          'confidence': {'categories': [0, 1],
                                                                         'datatype': 'int',
                                                                         'ordered': False},
                                                          'value': {'categories': [1, 2, 3, 4, 5],
                                                                    'datatype': 'int',
                                                                    'ordered': True}}}}

metadata_example_noann = deepcopy(metadata_example)

for subspace, propdict in metadata_example_noann.items():
    for prop, md in propdict.items():
        del md['annotators']


class TestUDSPropertyMetadata:

    def test_init(self):
        pass

    def test_from_dict(self):
        metadatadict = metadata_example['protoroles']['awareness']
        metadata = UDSPropertyMetadata.from_dict(metadatadict)

        assert isinstance(metadata.value, UDSDataType)
        assert isinstance(metadata.confidence, UDSDataType)

        assert metadata.value.datatype is int
        assert metadata.confidence.datatype is int

        assert metadata.value.categories == [1, 2, 3, 4, 5]
        assert metadata.confidence.categories == {0, 1}

        assert metadata.annotators == {'protoroles-annotator-8',
                                       'protoroles-annotator-9'}

class TestUDSAnnotationMetadata:

    metadata = UDSAnnotationMetadata.from_dict(metadata_example)
    metadata_noann = UDSAnnotationMetadata.from_dict(metadata_example_noann)

    def test_getitem(self):
        self.metadata['protoroles']
        self.metadata['protoroles', 'awareness']
        self.metadata['protoroles']['awareness']
        self.metadata['protoroles', 'awareness'].value

        with pytest.raises(TypeError):
            self.metadata['protoroles', 'awareness', 'value']

    def test_add(self):
        with pytest.raises(ValueError):
            self.metadata + self.metadata

        metadatadict1 = {'protoroles': {'awareness': metadata_example['protoroles']['awareness']}}
        metadatadict2 = {'protoroles': {'change_of_location': metadata_example['protoroles']['change_of_location']}}

        metadata1 = UDSAnnotationMetadata.from_dict(metadatadict1)
        metadata2 = UDSAnnotationMetadata.from_dict(metadatadict2)

        metadata1 + metadata2

    def test_subspaces(self):
        assert self.metadata.subspaces == {'protoroles'}

    def test_properties(self):
        assert self.metadata.properties() == {'awareness',
                                              'change_of_location'}

        assert self.metadata.properties('protoroles') == {'awareness',
                                                          'change_of_location'}

    def test_annotators(self):
        assert self.metadata.annotators() == {'protoroles-annotator-0',
                                              'protoroles-annotator-1',
                                              'protoroles-annotator-8',
                                              'protoroles-annotator-9'}

        assert self.metadata.annotators('protoroles') == {'protoroles-annotator-0',
                                                          'protoroles-annotator-1',
                                                          'protoroles-annotator-8',
                                                          'protoroles-annotator-9'}

        assert self.metadata.annotators('protoroles', 'awareness') == {'protoroles-annotator-8',
                                                                       'protoroles-annotator-9'}


        with pytest.raises(ValueError):
            self.metadata.annotators(prop='awareness')

        assert self.metadata_noann.annotators() is None

    def test_has_annotators(self):
        assert self.metadata.has_annotators()
        assert self.metadata.has_annotators('protoroles')
        assert self.metadata.has_annotators('protoroles', 'awareness')
        assert not self.metadata_noann.has_annotators()

def test_something(raw_node_sentence_annotation):
    print(raw_node_sentence_annotation)
