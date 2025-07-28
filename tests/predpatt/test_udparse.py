"""
Tests for UDParse and DepTriple classes to document and verify current behavior.

UDParse Class Documentation
===========================

UDParse represents a dependency parse of a sentence with tokens, tags, and dependency relations.

Data Structures
--------------
1. DepTriple: Named tuple with fields (rel, gov, dep)
   - rel: dependency relation (e.g., "nsubj", "dobj")
   - gov: governor token index or Token object
   - dep: dependent token index or Token object
   - __repr__ format: "rel(dep,gov)" (note: dep comes first!)

2. UDParse: Container for parsed sentence
   - tokens: list of tokens (strings or Token objects)
   - tags: list of POS tags
   - triples: list of DepTriple objects
   - governor: dict mapping dependent index to DepTriple
   - dependents: defaultdict mapping governor index to list of DepTriples
   - ud: Universal Dependencies module (always set to dep_v1 regardless of param)

Token Storage and Access
-----------------------
- Tokens stored as a list in self.tokens
- Can be strings (from parser) or Token objects (from PredPatt)
- Indices used in triples correspond to token positions
- Special index -1 or len(tokens) refers to ROOT
- governor dict provides O(1) lookup of governing edge for any token
- dependents dict provides O(1) lookup of all dependents for any token

Relationship with util.ud
------------------------
- Takes ud parameter but always sets self.ud = dep_v1 (bug/quirk)
- Used for pretty printing but not for parsing logic
- UD version determines relation names and constants

Methods
-------
- pprint(): Pretty print dependencies in columnar format
- latex(): Generate LaTeX code for dependency diagram
- view(): Create and open PDF visualization
- toimage(): Convert to PNG image
"""

import pytest
from collections import defaultdict
from decomp.semantics.predpatt.UDParse import UDParse, DepTriple
from decomp.semantics.predpatt.util.ud import dep_v1, dep_v2


class TestDepTriple:
    """Test DepTriple named tuple behavior."""
    
    def test_creation(self):
        """Test creating DepTriple instances."""
        # with indices
        dt1 = DepTriple(rel="nsubj", gov=2, dep=0)
        assert dt1.rel == "nsubj"
        assert dt1.gov == 2
        assert dt1.dep == 0
        
        # with mixed types
        dt2 = DepTriple(rel=dep_v1.dobj, gov="eat", dep="apple")
        assert dt2.rel == dep_v1.dobj
        assert dt2.gov == "eat"
        assert dt2.dep == "apple"
    
    def test_repr(self):
        """Test __repr__ format: rel(dep,gov)."""
        dt = DepTriple(rel="nsubj", gov=2, dep=0)
        assert repr(dt) == "nsubj(0,2)"
        
        # note: dep comes first in repr!
        dt2 = DepTriple(rel="dobj", gov="eat", dep="apple")
        assert repr(dt2) == "dobj(apple,eat)"
    
    def test_named_tuple_behavior(self):
        """Test that DepTriple behaves as a named tuple."""
        dt = DepTriple(rel="nsubj", gov=2, dep=0)
        
        # tuple unpacking
        rel, gov, dep = dt
        assert rel == "nsubj"
        assert gov == 2
        assert dep == 0
        
        # field access
        assert dt[0] == "nsubj"
        assert dt[1] == 2
        assert dt[2] == 0
        
        # immutable
        with pytest.raises(AttributeError):
            dt.rel = "dobj"
    
    def test_equality(self):
        """Test DepTriple equality."""
        dt1 = DepTriple(rel="nsubj", gov=2, dep=0)
        dt2 = DepTriple(rel="nsubj", gov=2, dep=0)
        dt3 = DepTriple(rel="dobj", gov=2, dep=3)
        
        assert dt1 == dt2
        assert dt1 != dt3
        
        # can be used in sets
        s = {dt1, dt2, dt3}
        assert len(s) == 2


class TestUDParseInitialization:
    """Test UDParse initialization."""
    
    def test_basic_initialization(self):
        """Test basic UDParse creation."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple(rel="nsubj", gov=1, dep=0),
            DepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        parse = UDParse(tokens, tags, triples)
        
        assert parse.tokens == tokens
        assert parse.tags == tags
        assert parse.triples == triples
        assert parse.ud == dep_v1  # always dep_v1!
    
    def test_ud_parameter_ignored(self):
        """Test that ud parameter is ignored (always sets dep_v1)."""
        tokens = ["test"]
        tags = ["NN"]
        triples = []
        
        # even with dep_v2, it sets dep_v1
        parse = UDParse(tokens, tags, triples, ud=dep_v2)
        assert parse.ud == dep_v1  # quirk: always dep_v1
    
    def test_governor_dict(self):
        """Test governor dictionary construction."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple(rel="nsubj", gov=1, dep=0),
            DepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        parse = UDParse(tokens, tags, triples)
        
        # governor maps dependent index to edge
        assert parse.governor[0] == triples[0]
        assert parse.governor[2] == triples[1]
        assert 1 not in parse.governor  # 1 has no governor
    
    def test_dependents_dict(self):
        """Test dependents dictionary construction."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple(rel="nsubj", gov=1, dep=0),
            DepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        parse = UDParse(tokens, tags, triples)
        
        # dependents maps governor index to list of edges
        assert len(parse.dependents[1]) == 2
        assert parse.dependents[1][0] == triples[0]
        assert parse.dependents[1][1] == triples[1]
        assert len(parse.dependents[0]) == 0  # defaultdict
        assert len(parse.dependents[2]) == 0
    
    def test_empty_parse(self):
        """Test empty parse."""
        parse = UDParse([], [], [])
        
        assert parse.tokens == []
        assert parse.tags == []
        assert parse.triples == []
        assert parse.governor == {}
        assert isinstance(parse.dependents, defaultdict)
        assert len(parse.dependents) == 0


class TestUDParsePprint:
    """Test pretty printing functionality."""
    
    def test_pprint_basic(self):
        """Test basic pretty printing."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple(rel="nsubj", gov=1, dep=0),
            DepTriple(rel="dobj", gov=1, dep=2),
            DepTriple(rel="root", gov=-1, dep=1)  # ROOT edge
        ]
        
        parse = UDParse(tokens, tags, triples)
        output = parse.pprint(color=False)
        
        # should contain dependency representations
        assert "nsubj(I/0, eat/1)" in output
        assert "dobj(apples/2, eat/1)" in output
        assert "root(eat/1, ROOT/-1)" in output
    
    def test_pprint_multicolumn(self):
        """Test multi-column pretty printing."""
        tokens = ["A", "B", "C", "D"]
        tags = ["DT", "NN", "VB", "NN"]
        triples = [
            DepTriple(rel="det", gov=1, dep=0),
            DepTriple(rel="nsubj", gov=2, dep=1),
            DepTriple(rel="dobj", gov=2, dep=3)
        ]
        
        parse = UDParse(tokens, tags, triples)
        
        # single column
        output1 = parse.pprint(color=False, K=1)
        lines1 = output1.strip().split('\n')
        assert len(lines1) == 3
        
        # two columns
        output2 = parse.pprint(color=False, K=2)
        lines2 = output2.strip().split('\n')
        assert len(lines2) == 2  # 3 items in 2 columns = 2 rows
    
    def test_pprint_with_root_token(self):
        """Test that ROOT token is added to tokens list."""
        tokens = ["test"]
        tags = ["NN"]
        triples = [DepTriple(rel="root", gov=-1, dep=0)]
        
        parse = UDParse(tokens, tags, triples)
        output = parse.pprint(color=False)
        
        # ROOT should be referenced
        assert "ROOT" in output
        assert "root(test/0, ROOT/-1)" in output


class TestUDParseLatex:
    """Test LaTeX generation."""
    
    def test_latex_generation(self):
        """Test LaTeX code generation."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple(rel="nsubj", gov=1, dep=0),
            DepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        parse = UDParse(tokens, tags, triples)
        latex = parse.latex()
        
        # check it's bytes
        assert isinstance(latex, bytes)
        
        # decode and check content
        latex_str = latex.decode('utf-8')
        assert r"\documentclass{standalone}" in latex_str
        assert r"\usepackage{tikz-dependency}" in latex_str
        assert r"\begin{dependency}" in latex_str
        
        # tokens in LaTeX
        assert "I" in latex_str
        assert "eat" in latex_str
        assert "apples" in latex_str
        
        # dependency edges (1-indexed for LaTeX)
        assert r"\depedge{2}{1}{nsubj}" in latex_str
        assert r"\depedge{2}{3}{dobj}" in latex_str
    
    def test_latex_special_characters(self):
        """Test LaTeX escaping of special characters."""
        tokens = ["A&B", "test_case", "$100"]
        tags = ["NN", "NN", "CD"]
        triples = []
        
        parse = UDParse(tokens, tags, triples)
        latex = parse.latex().decode('utf-8')
        
        # & replaced with 'and' (no spaces)
        assert "A \\& B" not in latex  # would break LaTeX
        assert "AandB" in latex  # replaced without spaces
        
        # _ replaced with space
        assert "test case" in latex
        
        # $ escaped
        assert "\\$100" in latex
    
    def test_latex_excludes_root_edges(self):
        """Test that edges to ROOT (gov=-1) are excluded."""
        tokens = ["test"]
        tags = ["NN"]
        triples = [
            DepTriple(rel="root", gov=-1, dep=0),
            DepTriple(rel="dep", gov=0, dep=0)  # self-loop
        ]
        
        parse = UDParse(tokens, tags, triples)
        latex = parse.latex().decode('utf-8')
        
        # root edge excluded (gov < 0)
        assert "depedge" in latex  # has some edge
        assert "{0}" not in latex  # no 0-indexed governor
        assert "{1}{1}" in latex  # self-loop (1-indexed)


class TestUDParseWithTokenObjects:
    """Test UDParse with Token objects instead of strings."""
    
    def test_token_objects(self):
        """Test that UDParse can handle Token objects."""
        from decomp.semantics.predpatt.patt import Token
        
        tokens = [
            Token(position=0, text="I", tag="PRP"),
            Token(position=1, text="eat", tag="VBP"),
            Token(position=2, text="apples", tag="NNS")
        ]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple(rel="nsubj", gov=tokens[1], dep=tokens[0]),
            DepTriple(rel="dobj", gov=tokens[1], dep=tokens[2])
        ]
        
        parse = UDParse(tokens, tags, triples)
        
        assert parse.tokens == tokens
        assert parse.triples == triples
        
        # governor/dependents should work with token objects
        assert parse.governor[tokens[0]] == triples[0]
        assert parse.governor[tokens[2]] == triples[1]
        assert len(parse.dependents[tokens[1]]) == 2


class TestUDParseEdgeCases:
    """Test edge cases and special behaviors."""
    
    def test_multiple_edges_same_pair(self):
        """Test multiple edges between same token pair."""
        tokens = ["A", "B"]
        tags = ["DT", "NN"]
        triples = [
            DepTriple(rel="det", gov=1, dep=0),
            DepTriple(rel="amod", gov=1, dep=0)  # second edge
        ]
        
        parse = UDParse(tokens, tags, triples)
        
        # governor only keeps last edge
        assert parse.governor[0] == triples[1]
        
        # dependents keeps both
        assert len(parse.dependents[1]) == 2
        assert triples[0] in parse.dependents[1]
        assert triples[1] in parse.dependents[1]
    
    def test_self_loops(self):
        """Test self-loop edges."""
        tokens = ["test"]
        tags = ["NN"]
        triples = [DepTriple(rel="dep", gov=0, dep=0)]
        
        parse = UDParse(tokens, tags, triples)
        
        assert parse.governor[0] == triples[0]
        assert parse.dependents[0] == [triples[0]]
    
    def test_defaultdict_behavior(self):
        """Test that dependents is a defaultdict."""
        tokens = ["A", "B", "C"]
        tags = ["DT", "NN", "VB"]
        triples = []
        
        parse = UDParse(tokens, tags, triples)
        
        # accessing non-existent key returns empty list
        assert parse.dependents[0] == []
        assert parse.dependents[99] == []
        assert isinstance(parse.dependents[0], list)
    
    def test_root_indexing(self):
        """Test various ROOT index representations."""
        tokens = ["test"]
        tags = ["NN"]
        
        # ROOT as -1
        triples1 = [DepTriple(rel="root", gov=-1, dep=0)]
        parse1 = UDParse(tokens, tags, triples1)
        assert parse1.dependents[-1] == [triples1[0]]
        
        # ROOT as len(tokens)
        triples2 = [DepTriple(rel="root", gov=1, dep=0)]
        parse2 = UDParse(tokens, tags, triples2)
        assert parse2.dependents[1] == [triples2[0]]