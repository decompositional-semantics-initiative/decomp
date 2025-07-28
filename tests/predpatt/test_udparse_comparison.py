"""
Comparison tests between original and modernized UDParse implementations.

These tests ensure that the modernized version behaves identically to the original.
"""

import pytest
from collections import defaultdict

# Import both versions
from decomp.semantics.predpatt.UDParse import UDParse as OriginalUDParse
from decomp.semantics.predpatt.UDParse import DepTriple as OriginalDepTriple
from decomp.semantics.predpatt.parsing.udparse import UDParse as ModernUDParse
from decomp.semantics.predpatt.parsing.udparse import DepTriple as ModernDepTriple
from decomp.semantics.predpatt.util.ud import dep_v1, dep_v2


class TestDepTripleComparison:
    """Test that modern DepTriple behaves identically to original."""
    
    def test_creation_identical(self):
        """Test that both versions create identical DepTriples."""
        # Create with same args
        orig = OriginalDepTriple(rel="nsubj", gov=2, dep=0)
        modern = ModernDepTriple(rel="nsubj", gov=2, dep=0)
        
        assert orig.rel == modern.rel
        assert orig.gov == modern.gov
        assert orig.dep == modern.dep
    
    def test_repr_identical(self):
        """Test that __repr__ output is identical."""
        orig = OriginalDepTriple(rel="dobj", gov=1, dep=3)
        modern = ModernDepTriple(rel="dobj", gov=1, dep=3)
        
        assert repr(orig) == repr(modern)
        assert repr(orig) == "dobj(3,1)"
    
    def test_tuple_behavior_identical(self):
        """Test that tuple behavior is identical."""
        orig = OriginalDepTriple(rel="amod", gov="big", dep="dog")
        modern = ModernDepTriple(rel="amod", gov="big", dep="dog")
        
        # Unpacking
        o_rel, o_gov, o_dep = orig
        m_rel, m_gov, m_dep = modern
        assert (o_rel, o_gov, o_dep) == (m_rel, m_gov, m_dep)
        
        # Indexing
        assert orig[0] == modern[0]
        assert orig[1] == modern[1]
        assert orig[2] == modern[2]
    
    def test_equality_identical(self):
        """Test that equality works identically."""
        orig1 = OriginalDepTriple(rel="nsubj", gov=2, dep=0)
        orig2 = OriginalDepTriple(rel="nsubj", gov=2, dep=0)
        modern1 = ModernDepTriple(rel="nsubj", gov=2, dep=0)
        modern2 = ModernDepTriple(rel="nsubj", gov=2, dep=0)
        
        assert orig1 == orig2
        assert modern1 == modern2
        assert orig1 == modern1  # Cross-version equality


class TestUDParseComparison:
    """Test that modern UDParse behaves identically to original."""
    
    def test_basic_initialization_identical(self):
        """Test that basic initialization produces identical results."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            OriginalDepTriple(rel="nsubj", gov=1, dep=0),
            OriginalDepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        assert orig.tokens == modern.tokens
        assert orig.tags == modern.tags
        assert len(orig.triples) == len(modern.triples)
        assert orig.ud == modern.ud == dep_v1
    
    def test_ud_parameter_ignored_identically(self):
        """Test that both versions ignore the ud parameter."""
        tokens = ["test"]
        tags = ["NN"]
        triples = []
        
        orig = OriginalUDParse(tokens, tags, triples, ud=dep_v2)
        modern = ModernUDParse(tokens, tags, triples, ud=dep_v2)
        
        assert orig.ud == modern.ud == dep_v1
    
    def test_governor_dict_identical(self):
        """Test that governor dictionaries are identical."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            OriginalDepTriple(rel="nsubj", gov=1, dep=0),
            OriginalDepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        assert set(orig.governor.keys()) == set(modern.governor.keys())
        for key in orig.governor:
            assert repr(orig.governor[key]) == repr(modern.governor[key])
    
    def test_dependents_dict_identical(self):
        """Test that dependents dictionaries are identical."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            OriginalDepTriple(rel="nsubj", gov=1, dep=0),
            OriginalDepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        # Both should be defaultdicts
        assert isinstance(orig.dependents, defaultdict)
        assert isinstance(modern.dependents, defaultdict)
        
        # Check contents
        assert set(orig.dependents.keys()) == set(modern.dependents.keys())
        for key in orig.dependents:
            assert len(orig.dependents[key]) == len(modern.dependents[key])
            for i in range(len(orig.dependents[key])):
                assert repr(orig.dependents[key][i]) == repr(modern.dependents[key][i])
    
    def test_pprint_output_identical(self):
        """Test that pprint output is identical."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            OriginalDepTriple(rel="nsubj", gov=1, dep=0),
            OriginalDepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        # Test without color
        assert orig.pprint(color=False) == modern.pprint(color=False)
        
        # Test with multiple columns
        assert orig.pprint(color=False, K=2) == modern.pprint(color=False, K=2)
    
    def test_pprint_with_root_identical(self):
        """Test pprint with ROOT edges."""
        tokens = ["test"]
        tags = ["NN"]
        triples = [OriginalDepTriple(rel="root", gov=-1, dep=0)]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        assert orig.pprint(color=False) == modern.pprint(color=False)
    
    def test_latex_output_identical(self):
        """Test that latex output is identical."""
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            OriginalDepTriple(rel="nsubj", gov=1, dep=0),
            OriginalDepTriple(rel="dobj", gov=1, dep=2)
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        assert orig.latex() == modern.latex()
    
    def test_latex_special_chars_identical(self):
        """Test latex with special characters."""
        tokens = ["A&B", "test_case", "$100"]
        tags = ["NN", "NN", "CD"]
        triples = []
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        assert orig.latex() == modern.latex()
    
    def test_empty_parse_identical(self):
        """Test empty parse behavior."""
        orig = OriginalUDParse([], [], [])
        modern = ModernUDParse([], [], [])
        
        assert orig.tokens == modern.tokens
        assert orig.tags == modern.tags
        assert orig.triples == modern.triples
        assert orig.governor == modern.governor
        assert list(orig.dependents.keys()) == list(modern.dependents.keys())
    
    def test_multiple_edges_identical(self):
        """Test handling of multiple edges between same tokens."""
        tokens = ["A", "B"]
        tags = ["DT", "NN"]
        triples = [
            OriginalDepTriple(rel="det", gov=1, dep=0),
            OriginalDepTriple(rel="amod", gov=1, dep=0)
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        # Governor should only have last edge
        assert repr(orig.governor[0]) == repr(modern.governor[0])
        assert repr(orig.governor[0]) == "amod(0,1)"
        
        # Dependents should have both
        assert len(orig.dependents[1]) == len(modern.dependents[1]) == 2


class TestUDParseWithTokenObjects:
    """Test with Token objects from predpatt."""
    
    def test_token_object_handling_identical(self):
        """Test that both versions handle Token objects identically."""
        from decomp.semantics.predpatt.patt import Token
        
        # Create Token objects
        tokens = [
            Token(position=0, text="I", tag="PRP"),
            Token(position=1, text="eat", tag="VBP"),
            Token(position=2, text="apples", tag="NNS")
        ]
        tags = ["PRP", "VBP", "NNS"]
        
        # Use Token objects in triples
        triples = [
            OriginalDepTriple(rel="nsubj", gov=tokens[1], dep=tokens[0]),
            OriginalDepTriple(rel="dobj", gov=tokens[1], dep=tokens[2])
        ]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        # Check that tokens are stored identically
        assert orig.tokens == modern.tokens
        
        # Check governor mapping works
        assert orig.governor[tokens[0]].rel == modern.governor[tokens[0]].rel
        assert orig.governor[tokens[2]].rel == modern.governor[tokens[2]].rel
        
        # Check dependents mapping works
        assert len(orig.dependents[tokens[1]]) == len(modern.dependents[tokens[1]])


class TestEdgeCasesIdentical:
    """Test edge cases behave identically."""
    
    def test_self_loops_identical(self):
        """Test self-loop handling."""
        tokens = ["test"]
        tags = ["NN"]
        triples = [OriginalDepTriple(rel="dep", gov=0, dep=0)]
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        assert repr(orig.governor[0]) == repr(modern.governor[0])
        assert len(orig.dependents[0]) == len(modern.dependents[0])
    
    def test_defaultdict_behavior_identical(self):
        """Test defaultdict behavior is identical."""
        tokens = ["A", "B", "C"]
        tags = ["DT", "NN", "VB"]
        triples = []
        
        orig = OriginalUDParse(tokens, tags, triples)
        modern = ModernUDParse(tokens, tags, triples)
        
        # Both should return empty lists for non-existent keys
        assert orig.dependents[0] == modern.dependents[0] == []
        assert orig.dependents[99] == modern.dependents[99] == []
        
        # After access, keys should exist
        assert 0 in orig.dependents
        assert 0 in modern.dependents


def test_cross_version_compatibility():
    """Test that DepTriples from different versions can be mixed."""
    tokens = ["test"]
    tags = ["NN"]
    
    # Create DepTriple with original version
    orig_triple = OriginalDepTriple(rel="nsubj", gov=1, dep=0)
    
    # Use it in modern UDParse
    modern_parse = ModernUDParse(tokens, tags, [orig_triple])
    
    assert len(modern_parse.triples) == 1
    assert modern_parse.governor[0].rel == "nsubj"
    
    # And vice versa
    modern_triple = ModernDepTriple(rel="dobj", gov=1, dep=0)
    orig_parse = OriginalUDParse(tokens, tags, [modern_triple])
    
    assert len(orig_parse.triples) == 1
    assert orig_parse.governor[0].rel == "dobj"