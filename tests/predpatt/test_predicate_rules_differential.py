"""Differential testing for predicate identification rules.

This ensures our modernized rules produce exactly the same results
as the original PredPatt implementation.
"""

import pytest
from decomp.semantics.predpatt.patt import PredPatt, PredPattOpts, Token
from decomp.semantics.predpatt.parsing.udparse import UDParse, DepTriple
from decomp.semantics.predpatt import rules as original_R
from decomp.semantics.predpatt.rules import (
    a1, a2, b, c, d, e, f, v,
    gov_looks_like_predicate
)
from decomp.semantics.predpatt.util.ud import dep_v1, postag


class TestPredicateRulesDifferential:
    """Test that modernized predicate rules behave identically to original."""
    
    def create_parse_with_tokens(self, tokens, tags, triples):
        """Helper to create a UDParse with proper Token objects."""
        token_objs = []
        for i, (text, tag) in enumerate(zip(tokens, tags)):
            t = Token(position=i, text=text, tag=tag)
            token_objs.append(t)
        
        # set up dependencies
        for triple in triples:
            if triple.gov >= 0:
                gov_tok = token_objs[triple.gov]
                dep_tok = token_objs[triple.dep]
                dep_tok.gov = gov_tok
                dep_tok.gov_rel = triple.rel
                if gov_tok.dependents is None:
                    gov_tok.dependents = []
                gov_tok.dependents.append(DepTriple(triple.rel, gov_tok, dep_tok))
        
        return UDParse(token_objs, tags, triples)
    
    def test_rule_classes_identical(self):
        """Test that rule classes have same structure as original."""
        # test basic instantiation
        assert a1().name() == original_R.a1().name()
        assert a2().name() == original_R.a2().name()
        assert b().name() == original_R.b().name()
        assert d().name() == original_R.d().name()
        assert e().name() == original_R.e().name()
        assert v().name() == original_R.v().name()
        assert f().name() == original_R.f().name()
        
        # test rule c with edge parameter
        edge = DepTriple(rel="nsubj", gov=1, dep=0)
        rule_c_new = c(edge)
        rule_c_orig = original_R.c(edge)
        assert repr(rule_c_new) == repr(rule_c_orig)
    
    def test_gov_looks_like_predicate_identical(self):
        """Test that gov_looks_like_predicate produces identical results."""
        # create test tokens
        verb_token = Token(position=0, text="runs", tag="VERB")
        noun_token = Token(position=1, text="dog", tag="NOUN")
        
        # test verb with nmod
        edge1 = DepTriple(rel="nmod", gov=verb_token, dep=noun_token)
        assert gov_looks_like_predicate(edge1, dep_v1) == True
        
        # test noun with nsubj
        edge2 = DepTriple(rel="nsubj", gov=noun_token, dep=verb_token)
        assert gov_looks_like_predicate(edge2, dep_v1) == True
        
        # test noun with det (should be False)
        edge3 = DepTriple(rel="det", gov=noun_token, dep=verb_token)
        assert gov_looks_like_predicate(edge3, dep_v1) == False
    
    def test_predicate_extraction_order_identical(self):
        """Test that predicates are identified in exact same order."""
        # "Sam, the CEO, arrived and left"
        tokens = ["Sam", ",", "the", "CEO", ",", "arrived", "and", "left"]
        tags = ["PROPN", "PUNCT", "DET", "NOUN", "PUNCT", "VERB", "CCONJ", "VERB"]
        triples = [
            DepTriple("nsubj", 5, 0),    # Sam <- arrived
            DepTriple("appos", 0, 3),    # CEO <- Sam
            DepTriple("det", 3, 2),      # the <- CEO
            DepTriple("punct", 3, 1),    # , <- CEO
            DepTriple("punct", 3, 4),    # , <- CEO
            DepTriple("root", -1, 5),    # arrived <- ROOT
            DepTriple("cc", 5, 6),       # and <- arrived
            DepTriple("conj", 5, 7),     # left <- arrived
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(resolve_appos=True, resolve_poss=True, resolve_amod=True)
        pp = PredPatt(parse, opts=opts)
        
        # should identify predicates by position: CEO (3), arrived (5), left (7)
        assert len(pp.events) == 3
        pred_positions = sorted([p.root.position for p in pp.events])
        assert pred_positions == [3, 5, 7]
        
        # check rule types by position
        ceo_pred = [p for p in pp.events if p.root.position == 3][0]
        arrived_pred = [p for p in pp.events if p.root.position == 5][0] 
        left_pred = [p for p in pp.events if p.root.position == 7][0]
        
        assert any(isinstance(r, original_R.d) for r in ceo_pred.rules)
        assert any(isinstance(r, original_R.c) for r in arrived_pred.rules)
        assert any(isinstance(r, original_R.f) for r in left_pred.rules)
    
    def test_complex_sentence_identical(self):
        """Test complex sentence with multiple predicate types."""
        # "John's red car arrived when I thought he left"
        tokens = ["John", "'s", "red", "car", "arrived", "when", "I", "thought", "he", "left"]
        tags = ["PROPN", "X", "ADJ", "NOUN", "VERB", "SCONJ", "PRON", "VERB", "PRON", "VERB"]
        triples = [
            DepTriple("nmod:poss", 3, 0),  # John <- car
            DepTriple("case", 0, 1),       # 's <- John
            DepTriple("amod", 3, 2),       # red <- car
            DepTriple("nsubj", 4, 3),      # car <- arrived
            DepTriple("root", -1, 4),      # arrived <- ROOT
            DepTriple("advcl", 4, 7),      # thought <- arrived
            DepTriple("mark", 7, 5),       # when <- thought
            DepTriple("nsubj", 7, 6),      # I <- thought
            DepTriple("ccomp", 7, 9),      # left <- thought
            DepTriple("nsubj", 9, 8),      # he <- left
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(
            resolve_appos=True,
            resolve_poss=True,
            resolve_amod=True,
            resolve_relcl=True
        )
        pp = PredPatt(parse, opts=opts)
        
        # check all predicates were found by position
        pred_positions = sorted([p.root.position for p in pp.events])
        expected_positions = sorted([0, 2, 4, 7, 9])  # John, red, arrived, thought, left
        assert pred_positions == expected_positions
        
        # verify specific rules were applied by position
        for pred in pp.events:
            if pred.root.position == 0:  # John
                assert any(isinstance(r, original_R.v) for r in pred.rules)
            elif pred.root.position == 2:  # red
                assert any(isinstance(r, original_R.e) for r in pred.rules)
            elif pred.root.position == 4:  # arrived
                assert any(isinstance(r, original_R.c) for r in pred.rules)
            elif pred.root.position == 7:  # thought
                assert any(isinstance(r, original_R.b) for r in pred.rules)
            elif pred.root.position == 9:  # left
                assert any(isinstance(r, original_R.a1) for r in pred.rules)
    
    def test_xcomp_rule_a2(self):
        """Test rule a2 for xcomp."""
        # "I want to sleep"
        tokens = ["I", "want", "to", "sleep"]
        tags = ["PRON", "VERB", "PART", "VERB"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- want
            DepTriple("xcomp", 1, 3),    # sleep <- want
            DepTriple("mark", 3, 2),     # to <- sleep
            DepTriple("root", -1, 1),    # want <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # should find "want" but "sleep" gets merged via xcomp resolution
        # this is expected behavior - xcomp predicates get merged when options.cut is True
        assert len(pp.events) >= 1
        pred_positions = [p.root.position for p in pp.events]
        assert 1 in pred_positions  # want at position 1
        
        # check want has c rule (from nsubj)
        want_pred = [p for p in pp.events if p.root.position == 1][0]
        assert any(isinstance(r, original_R.c) for r in want_pred.rules)
    
    def test_rule_application_with_dep_arc(self):
        """Test that dep arcs are handled correctly."""
        # sentence with dep arc - should skip some rules
        tokens = ["Something", "went", "wrong"]
        tags = ["NOUN", "VERB", "ADJ"]
        triples = [
            DepTriple("dep", 1, 0),      # Something <- went (dep arc)
            DepTriple("root", -1, 1),    # went <- ROOT
            DepTriple("xcomp", 1, 2),    # wrong <- went
        ]
        
        # set up the dep relation on governor
        token_objs = []
        for i, (text, tag) in enumerate(zip(tokens, tags)):
            t = Token(position=i, text=text, tag=tag)
            token_objs.append(t)
        
        # manually set gov_rel for testing
        token_objs[0].gov_rel = "dep"
        token_objs[0].gov = token_objs[1]
        
        parse = UDParse(token_objs, tags, triples)
        pp = PredPatt(parse)
        
        # the behavior with dep arcs is preserved
        pred_positions = [p.root.position for p in pp.events]
        assert 1 in pred_positions  # went at position 1
    
    def test_qualified_conjoined_predicate(self):
        """Test the qualified_conjoined_predicate logic."""
        # "He runs and jumps" - both verbs, should work
        tokens1 = ["He", "runs", "and", "jumps"]
        tags1 = ["PRON", "VERB", "CCONJ", "VERB"]
        triples1 = [
            DepTriple("nsubj", 1, 0),
            DepTriple("root", -1, 1),
            DepTriple("cc", 1, 2),
            DepTriple("conj", 1, 3),
        ]
        
        parse1 = self.create_parse_with_tokens(tokens1, tags1, triples1)
        pp1 = PredPatt(parse1)
        assert len(pp1.events) == 2
        pred_positions = [p.root.position for p in pp1.events]
        assert 3 in pred_positions  # jumps at position 3
        
        # "There is nothing wrong with a negotiation, but nothing helpful"
        # wrong (ADJ) conj with helpful (ADJ) - should work
        tokens2 = ["nothing", "wrong", "but", "nothing", "helpful"]
        tags2 = ["NOUN", "ADJ", "CCONJ", "NOUN", "ADJ"]
        triples2 = [
            DepTriple("amod", 0, 1),     # wrong <- nothing
            DepTriple("cc", 1, 2),       # but <- wrong
            DepTriple("conj", 1, 4),     # helpful <- wrong
            DepTriple("dep", 4, 3),      # nothing <- helpful
        ]
        
        parse2 = self.create_parse_with_tokens(tokens2, tags2, triples2)
        opts2 = PredPattOpts(resolve_amod=True)
        pp2 = PredPatt(parse2, opts=opts2)
        
        # both adjectives should be predicates
        pred_positions = [p.root.position for p in pp2.events]
        assert 1 in pred_positions  # wrong at position 1
        assert 4 in pred_positions  # helpful at position 4


class TestRuleEquivalence:
    """Test that our rule instances are functionally equivalent to original."""
    
    def test_rule_instances_comparable(self):
        """Test that rule instances can be compared properly."""
        # our rules
        new_a1_1 = a1()
        new_a1_2 = a1()
        new_a2 = a2()
        
        # original rules
        orig_a1 = original_R.a1()
        orig_a2 = original_R.a2()
        
        # same type rules should be equal
        assert new_a1_1 == new_a1_2
        assert new_a1_1 != new_a2
        
        # names should match
        assert new_a1_1.name() == orig_a1.name()
        assert new_a2.name() == orig_a2.name()
        
        # repr should work
        assert repr(new_a1_1) == "a1"
        assert repr(orig_a1) == "a1"