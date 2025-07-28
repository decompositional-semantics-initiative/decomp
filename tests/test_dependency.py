from networkx import DiGraph
from numpy import array

from decomp.syntax.dependency import CoNLLDependencyTreeCorpus, DependencyGraphBuilder


rawtree = '''1       I       I       PRON    PRP     Case=Nom|Number=Sing|Person=1|PronType=Prs      4       nsubj   _       _
2       ca      can     AUX     MD      VerbForm=Fin    4       aux     _       SpaceAfter=No
3       n't     not     PART    RB      _       4       advmod  _       _
4       imagine imagine VERB    VB      VerbForm=Inf    0       root    _       _
5       they    they    PRON    PRP     Case=Nom|Number=Plur|Person=3|PronType=Prs      6       nsubj   _       _
6       wanted  want    VERB    VBD     Mood=Ind|Tense=Past|VerbForm=Fin        4       ccomp   _       _
7       to      to      PART    TO      _       8       mark    _       _
8       do      do      VERB    VB      VerbForm=Inf    6       xcomp   _       _
9       this    this    PRON    DT      Number=Sing|PronType=Dem        8       obj     _       SpaceAfter=No
10      .       .       PUNCT   .       _       4       punct   _       _'''

sentence = "I ca n't imagine they wanted to do this ."

listtree = [l.split() for l in rawtree.split('\n')]


def setup_tree():
    # build and extract tree
    graph = DependencyGraphBuilder().from_conll(listtree, 'tree1')

    return graph


def setup_corpus():
    listtrees = {'tree1': listtree,
                 'tree2': listtree}

    corpus = CoNLLDependencyTreeCorpus(listtrees)

    return corpus


# could use @nose.with_setup
def test_dependency_tree_builder():
    tree = setup_tree()

    assert tree.name == 'tree1'
    assert (tree.graph['conll'] == array(listtree)).all()

    print(tree.nodes['tree1-root-0'])
    # test the root
    # test syntax nodes
    assert tree.nodes['tree1-root-0'] == {'position': 0,
                                          'domain': 'root',
                                          'type': 'root'}

    for idx, node in tree.nodes.items():
        for row in listtree:
            if int(row[0]) == idx:
                assert node['form'] == row[1]
                assert node['lemma'] == row[2]
                assert node['upos'] == row[3]
                assert node['xpos'] == row[4]

    for (idx1, idx2), edge in tree.edges.items():
        for row in listtree:
            if int(row[0]) == idx2:
                assert int(row[6]) == idx1
                assert row[7] == edge['deprel']


def test_dependency_tree_corpus():
    corpus = setup_corpus()

    assert all([isinstance(t, DiGraph) for gid, t in corpus.graphs.items()])
    assert all([isinstance(t, DiGraph) for gid, t in corpus.items()])
    assert all([isinstance(gid, str) for gid in corpus])
