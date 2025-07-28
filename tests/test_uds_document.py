import pytest


test_document_name = 'answers-20111105112131AA6gIX6_ans'
test_document_genre = 'answers'
test_document_timestamp = '20111105112131'


test_document_text = 'My dad just does n\'t understand ? Ugh my dad is so stupid ... he just does n\'t understand anything ! I have 5 sisters and so including my mom ... he is the only guy in a house of six females . Now I \'m the youngest and I just got my period so now we all have ours and he thinks it \'s a good thing ? He \'s always like " ohh you must be so happy to finally have yours , I wish I had mine ! " and he is n\'t even joking . I think just living in a house with so many girls is making him go crazy ? Yep , the females are just getting to him ... dads .. Do n\'t blame him please , he feels lonely and wants to show his attention to all of you to look after you , please forgive and sympathy if he miss something . I am sorry for him , he is a good dad'

test_document_sentence_ids = {'ewt-train-7189': 'answers-20111105112131AA6gIX6_ans-0001',
 'ewt-train-7190': 'answers-20111105112131AA6gIX6_ans-0002',
 'ewt-train-7191': 'answers-20111105112131AA6gIX6_ans-0003',
 'ewt-train-7192': 'answers-20111105112131AA6gIX6_ans-0004',
 'ewt-train-7193': 'answers-20111105112131AA6gIX6_ans-0005',
 'ewt-train-7194': 'answers-20111105112131AA6gIX6_ans-0006',
 'ewt-train-7195': 'answers-20111105112131AA6gIX6_ans-0007',
 'ewt-train-7196': 'answers-20111105112131AA6gIX6_ans-0008',
 'ewt-train-7197': 'answers-20111105112131AA6gIX6_ans-0009'}

test_document_node = 'ewt-train-7195-document-pred-7'

test_document_semantics_node_normalized = {'ewt-train-7195-semantics-pred-7': {'domain': 'semantics',
  'frompredpatt': True,
  'type': 'predicate',
  'factuality': {'factual': {'confidence': 1.0, 'value': 1.2225}},
  'time': {'dur-weeks': {'confidence': 0.3991, 'value': 0.7263},
   'dur-decades': {'confidence': 0.3991, 'value': -1.378},
   'dur-days': {'confidence': 0.3991, 'value': 0.7498},
   'dur-hours': {'confidence': 0.3991, 'value': -1.1733},
   'dur-seconds': {'confidence': 0.3991, 'value': -1.4243},
   'dur-forever': {'confidence': 0.3991, 'value': -1.2803},
   'dur-centuries': {'confidence': 0.3991, 'value': -1.1213},
   'dur-instant': {'confidence': 0.3991, 'value': -1.3219},
   'dur-years': {'confidence': 0.3991, 'value': -1.1953},
   'dur-minutes': {'confidence': 0.3991, 'value': 0.8558},
   'dur-months': {'confidence': 0.3991, 'value': 0.6852}},
  'genericity': {'pred-dynamic': {'confidence': 1.0, 'value': 1.1508},
   'pred-hypothetical': {'confidence': 1.0, 'value': -1.1583},
   'pred-particular': {'confidence': 1.0, 'value': 1.1508}}}}

test_document_semantics_node_raw = {'ewt-train-7195-semantics-pred-7': {'domain': 'semantics', 'frompredpatt': True, 'type': 'predicate', 'factuality': {'factual': {'value': {'factuality-annotator-26': 1, 'factuality-annotator-34': 1}, 'confidence': {'factuality-annotator-26': 4, 'factuality-annotator-34': 4}}}, 'time': {'duration': {'value': {'time-annotator-508': 4, 'time-annotator-619': 6, 'time-annotator-310': 5, 'time-annotator-172': 4, 'time-annotator-448': 5, 'time-annotator-548': 6}, 'confidence': {'time-annotator-508': 2, 'time-annotator-619': 4, 'time-annotator-310': 4, 'time-annotator-172': 4, 'time-annotator-448': 1, 'time-annotator-548': 2}}}, 'genericity': {'pred-dynamic': {'value': {'genericity-pred-annotator-277': 0}, 'confidence': {'genericity-pred-annotator-277': 2}}, 'pred-hypothetical': {'value': {'genericity-pred-annotator-277': 0}, 'confidence': {'genericity-pred-annotator-277': 2}}, 'pred-particular': {'value': {'genericity-pred-annotator-277': 0}, 'confidence': {'genericity-pred-annotator-277': 2}}}}}

@pytest.fixture
def normalized_node_document_annotation(test_data_dir):
    fpath = os.path.join(test_data_dir,
                         'normalized_node_document_annotation.json')
    with open(fpath) as f:
        return f.read()


@pytest.fixture
def normalized_edge_document_annotation(test_data_dir):
    fpath = os.path.join(test_data_dir,
                         'normalized_edge_document_annotation.json')
    with open(fpath) as f:
        return f.read()


@pytest.fixture
def normalized_document_annotations(normalized_node_document_annotation,
                                    normalized_edge_document_annotation):
    norm_node_ann = NormalizedUDSAnnotation.from_json(normalized_node_document_annotation)
    norm_edge_ann = NormalizedUDSAnnotation.from_json(normalized_edge_document_annotation)

    return norm_node_ann, norm_edge_ann


@pytest.fixture
def raw_node_document_annotation():
    return '{"answers-20111105112131AA6gIX6_ans": {"ewt-train-7192-document-pred-25": {"subspace": {"property": {"confidence": {"annotator1": 0.12}, "value": {"annotator1": 0.0}}}}, "ewt-train-7192-document-pred-20": {"subspace": {"property": {"confidence": {"annotator2": 0.55, "annotator3": 0.07}, "value": {"annotator2": 0.0, "annotator3": 0.0}}}}, "ewt-train-7192-document-pred-20": {"subspace": {"property": {"confidence": {"annotator2": 0.55}, "value": {"annotator2": 0.0}}}}}}'


@pytest.fixture
def raw_edge_document_annotation():
    return '{"answers-20111105112131AA6gIX6_ans": {"ewt-train-7192-document-pred-20%%ewt-train-7192-document-arg-2": {"subspace": {"property": {"confidence": {"annotator1": 0.12}, "value": {"annotator1": 0.0}}}}, "ewt-train-7192-document-pred-20%%ewt-train-7189-document-arg-2": {"subspace": {"property": {"confidence": {"annotator2": 0.55, "annotator3": 0.07}, "value": {"annotator2": 0.0, "annotator3": 0.0}}}}, "ewt-train-7192-document-pred-25%%ewt-train-7191-document-arg-18": {"subspace": {"property": {"confidence": {"annotator2": 0.55}, "value": {"annotator2": 0.0}}}}}}'

@pytest.fixture
def raw_document_annotations(raw_node_document_annotation,
                             raw_edge_document_annotation):
    raw_node_ann = RawUDSAnnotation.from_json(raw_node_document_annotation)
    raw_edge_ann = RawUDSAnnotation.from_json(raw_edge_document_annotation)

    return raw_node_ann, raw_edge_ann
