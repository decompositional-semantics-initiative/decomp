"""
Tests and documentation for PredPatt rules system.

Rules Documentation
==================

The PredPatt rule system consists of several categories of rules that are applied
during predicate-argument extraction. Rules are used to track the logic behind
why certain tokens are identified as predicates or arguments.

Rule Categories
--------------
1. PredicateRootRule - Rules for identifying predicate root tokens
2. ArgumentRootRule - Rules for identifying argument root tokens  
3. PredConjRule - Rules for handling predicate conjunctions
4. ArgumentResolution - Rules for resolving missing/borrowed arguments
5. ConjunctionResolution - Rules for handling argument conjunctions
6. SimplifyRule - Rules for simplifying patterns
7. PredPhraseRule - Rules for building predicate phrases
8. ArgPhraseRule - Rules for building argument phrases

Predicate Root Identification Rules (Applied in predicate_extract)
-----------------------------------------------------------------
- a1: Extract predicate from dependent of {ccomp, csubj, csubjpass}
      Applied when: e.rel in {ccomp, csubj, csubjpass}
      
- a2: Extract predicate from dependent of xcomp
      Applied when: e.rel == xcomp
      
- b:  Extract predicate from dependent of clausal modifier  
      Applied when: e.rel in {advcl, acl, acl:relcl} (if resolve_relcl)
      
- c:  Extract predicate from governor of {nsubj, nsubjpass, dobj, iobj, ccomp, xcomp, advcl}
      Applied when: gov_looks_like_predicate(e) and various conditions
      
- d:  Extract predicate from dependent of apposition
      Applied when: e.rel == appos (if resolve_appos)
      
- e:  Extract predicate from dependent of adjectival modifier
      Applied when: e.rel == amod and dep.tag == ADJ and gov.tag != ADJ (if resolve_amod)
      
- v:  Extract predicate from dependent of nmod:poss (English specific)
      Applied when: e.rel == nmod:poss (if resolve_poss)
      
- f:  Extract conjunct token of a predicate token
      Applied when: e.rel == conj and qualified_conjoined_predicate()

Argument Root Identification Rules (Applied in argument_extract)
---------------------------------------------------------------
- g1: Extract argument from dependent of {nsubj, nsubjpass, dobj, iobj}
      Applied when: e.rel in {nsubj, nsubjpass, dobj, iobj}
      
- h1: Extract argument which directly depends on predicate from {nmod, nmod:npmod, nmod:tmod, obl}
      Applied when: e.rel.startswith(nmod) or e.rel.startswith(obl) and predicate.type != AMOD
      
- h2: Extract argument which indirectly depends on predicate from {nmod, nmod:npmod, nmod:tmod, obl}
      Applied when: Predicate has advmod dependent which has nmod/obl dependent
      
- i:  Extract argument from governor of adjectival modifier
      Applied when: predicate.type == AMOD
      
- j:  Extract argument from governor of apposition  
      Applied when: predicate.type == APPOS
      
- w1: Extract argument from governor of nmod:poss (English specific)
      Applied when: predicate.type == POSS
      
- w2: Extract argument from dependent of nmod:poss (English specific)
      Applied when: predicate.type == POSS
      
- k:  Extract argument from dependent of ccomp
      Applied when: e.rel in {ccomp, csubj, csubjpass} or (e.rel == xcomp and options.cut)

Other Rules
-----------
- l:  Merge xcomp's arguments to real predicate
- m:  Extract conjunct token of argument root
- Predicate phrase rules (n1-n6): Build predicate phrases
- Argument phrase rules: Build argument phrases
- Simplification rules (p1, p2, q, r): Simplify patterns
- u:  Strip punctuation from phrases

Order of Application
-------------------
1. Predicate extraction (predicate_extract):
   - First pass: a1, a2, b, c, d, e, v applied based on dependency relations
   - Second pass: f applied to find conjoined predicates
   
2. Argument extraction (argument_extract):
   - For each predicate: g1, h1, h2, i, j, w1, w2, k applied based on relations
   
3. Argument resolution (_argument_resolution):
   - Various borrowing and sharing rules applied
   
4. Phrase building:
   - Predicate phrases built with n1-n6 rules
   - Argument phrases built with corresponding rules
   
5. Simplification (if options.simple):
   - p1, p2, q, r applied to simplify patterns
"""

import pytest
from decomp.semantics.predpatt import rules
from decomp.semantics.predpatt.rules import *
R = rules  # Compatibility alias for existing tests
from decomp.semantics.predpatt.parsing.udparse import UDParse, DepTriple
from decomp.semantics.predpatt.extraction.engine import PredPattEngine as PredPatt
from decomp.semantics.predpatt.core.options import PredPattOpts
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.core.predicate import Predicate, NORMAL, APPOS, AMOD, POSS
from decomp.semantics.predpatt.core.argument import Argument
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, dep_v2


class TestRuleClasses:
    """Test basic rule class functionality."""
    
    def test_rule_name(self):
        """Test that rules return their class name."""
        assert R.a1.name() == 'a1'
        assert R.g1.name() == 'g1'
        assert R.borrow_subj.name() == 'borrow_subj'
    
    def test_rule_repr(self):
        """Test rule string representation."""
        rule = R.a1()
        assert repr(rule) == 'a1'
        
        # Test rules with parameters
        edge = DepTriple(rel="nsubj", gov=1, dep=0)
        rule_g1 = R.g1(edge)
        assert 'g1(nsubj)' in repr(rule_g1)
    
    def test_rule_explain(self):
        """Test that rules have docstrings."""
        assert 'clausal relation' in R.a1.explain()
        assert 'xcomp' in R.a2.explain()
        assert 'clausal modifier' in R.b.explain()


class TestPredicateExtractionRules:
    """Test predicate root identification rules."""
    
    def create_parse(self, tokens, tags, triples):
        """Helper to create a UDParse."""
        return UDParse(tokens, tags, triples)
    
    def test_rule_a1_ccomp(self):
        """Test a1: Extract predicate from ccomp dependent."""
        # "I think [he sleeps]"
        tokens = ["I", "think", "he", "sleeps"]
        tags = ["PRP", "VBP", "PRP", "VBZ"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- think
            DepTriple("nsubj", 3, 2),    # he <- sleeps
            DepTriple("ccomp", 1, 3),    # sleeps <- think (ccomp)
            DepTriple("root", -1, 1)     # think <- ROOT
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should extract "think" and "sleeps" as predicates
        assert len(pp.events) == 2
        pred_roots = [p.root.text for p in pp.events]
        assert "think" in pred_roots
        assert "sleeps" in pred_roots
        
        # Check that a1 rule was applied
        sleeps_pred = [p for p in pp.events if p.root.text == "sleeps"][0]
        assert any(isinstance(r, R.a1) for r in sleeps_pred.rules)
    
    def test_rule_a2_xcomp(self):
        """Test a2: Extract predicate from xcomp dependent."""
        # "I want [to sleep]"
        tokens = ["I", "want", "to", "sleep"]
        tags = ["PRP", "VBP", "TO", "VB"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- want
            DepTriple("xcomp", 1, 3),    # sleep <- want (xcomp)
            DepTriple("mark", 3, 2),     # to <- sleep
            DepTriple("root", -1, 1)     # want <- ROOT
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should extract "want" as predicate
        # Note: xcomp dependent is not extracted as a separate predicate in standard mode
        assert len(pp.events) == 1
        pred_roots = [p.root.text for p in pp.events]
        assert "want" in pred_roots
        
        # Check that the predicate has an xcomp argument extracted by rule l
        want_pred = pp.events[0]
        assert any(isinstance(r, R.l) for r in want_pred.rules)
    
    def test_rule_b_advcl(self):
        """Test b: Extract predicate from clausal modifier."""
        # "I run [when he sleeps]"
        tokens = ["I", "run", "when", "he", "sleeps"]
        tags = ["PRP", "VBP", "WRB", "PRP", "VBZ"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- run
            DepTriple("advcl", 1, 4),    # sleeps <- run (advcl)
            DepTriple("mark", 4, 2),     # when <- sleeps
            DepTriple("nsubj", 4, 3),    # he <- sleeps
            DepTriple("root", -1, 1)     # run <- ROOT
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        opts = PredPattOpts(resolve_relcl=True)
        pp = PredPatt(parse, opts=opts)
        
        # Should extract "run" and "sleeps" as predicates
        assert len(pp.events) == 2
        pred_roots = [p.root.text for p in pp.events]
        assert "run" in pred_roots
        assert "sleeps" in pred_roots
        
        # Check that b rule was applied
        sleeps_pred = [p for p in pp.events if p.root.text == "sleeps"][0]
        assert any(isinstance(r, R.b) for r in sleeps_pred.rules)
    
    def test_rule_c_governor(self):
        """Test c: Extract predicate from governor of core arguments."""
        # "The dog barks"
        tokens = ["The", "dog", "barks"]
        tags = ["DT", "NN", "VBZ"]
        triples = [
            DepTriple("det", 1, 0),      # The <- dog
            DepTriple("nsubj", 2, 1),    # dog <- barks
            DepTriple("root", -1, 2)     # barks <- ROOT
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should extract "barks" as predicate
        assert len(pp.events) == 1
        assert pp.events[0].root.text == "barks"
        
        # Check that c rule was applied
        assert any(isinstance(r, R.c) for r in pp.events[0].rules)
    
    def test_rule_d_appos(self):
        """Test d: Extract predicate from apposition dependent."""
        # "Sam, [the CEO], arrived"
        tokens = ["Sam", ",", "the", "CEO", ",", "arrived"]
        tags = ["NNP", ",", "DT", "NN", ",", "VBD"]
        triples = [
            DepTriple("nsubj", 5, 0),    # Sam <- arrived
            DepTriple("appos", 0, 3),    # CEO <- Sam (appos)
            DepTriple("det", 3, 2),      # the <- CEO
            DepTriple("punct", 3, 1),    # , <- CEO
            DepTriple("punct", 3, 4),    # , <- CEO
            DepTriple("root", -1, 5)     # arrived <- ROOT
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        opts = PredPattOpts(resolve_appos=True)
        pp = PredPatt(parse, opts=opts)
        
        # Should extract "arrived" and "CEO" as predicates
        assert len(pp.events) == 2
        pred_roots = [p.root.text for p in pp.events]
        assert "arrived" in pred_roots
        assert "CEO" in pred_roots
        
        # Check that d rule was applied and type is APPOS
        ceo_pred = [p for p in pp.events if p.root.text == "CEO"][0]
        assert any(isinstance(r, R.d) for r in ceo_pred.rules)
        assert ceo_pred.type == APPOS
    
    def test_rule_e_amod(self):
        """Test e: Extract predicate from adjectival modifier."""
        # "The [red] car"
        tokens = ["The", "red", "car"]
        tags = ["DT", "ADJ", "NN"]
        triples = [
            DepTriple("det", 2, 0),      # The <- car
            DepTriple("amod", 2, 1),     # red <- car (amod)
        ]
        
        # Create parse with strings (not Token objects)
        parse = UDParse(tokens, tags, triples)
        opts = PredPattOpts(resolve_amod=True)
        pp = PredPatt(parse, opts=opts)
        
        # Should extract "red" as predicate  
        assert len(pp.events) == 1
        assert pp.events[0].root.text == "red"
        
        # Check that e rule was applied and type is AMOD
        assert any(isinstance(r, R.e) for r in pp.events[0].rules)
        assert pp.events[0].type == AMOD
    
    def test_rule_v_poss(self):
        """Test v: Extract predicate from nmod:poss dependent."""
        # "[John's] car"
        tokens = ["John", "'s", "car"]
        tags = ["NNP", "POS", "NN"]
        triples = [
            DepTriple("nmod:poss", 2, 0),  # John <- car (nmod:poss)
            DepTriple("case", 0, 1),       # 's <- John
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        opts = PredPattOpts(resolve_poss=True)
        pp = PredPatt(parse, opts=opts)
        
        # Should extract "John" as predicate
        assert len(pp.events) == 1
        assert pp.events[0].root.text == "John"
        
        # Check that v rule was applied and type is POSS
        assert any(isinstance(r, R.v) for r in pp.events[0].rules)
        assert pp.events[0].type == POSS
    
    def test_rule_f_conj(self):
        """Test f: Extract conjunct token of predicate."""
        # "I [run] and [jump]"
        tokens = ["I", "run", "and", "jump"]
        tags = ["PRP", "VBP", "CC", "VBP"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- run
            DepTriple("cc", 1, 2),       # and <- run
            DepTriple("conj", 1, 3),     # jump <- run (conj)
            DepTriple("root", -1, 1)     # run <- ROOT
        ]
        
        parse = self.create_parse(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should extract "run" and "jump" as predicates
        assert len(pp.events) == 2
        pred_roots = [p.root.text for p in pp.events]
        assert "run" in pred_roots
        assert "jump" in pred_roots
        
        # Check that f rule was applied to jump
        jump_pred = [p for p in pp.events if p.root.text == "jump"][0]
        assert any(isinstance(r, R.f) for r in jump_pred.rules)


class TestArgumentExtractionRules:
    """Test argument root identification rules."""
    
    def create_parse_with_tokens(self, tokens, tags, triples):
        """Helper to create a UDParse with proper Token objects."""
        # UDParse expects tokens to be strings, not Token objects
        return UDParse(tokens, tags, triples)
    
    def test_rule_g1_core_args(self):
        """Test g1: Extract arguments from core dependencies."""
        # "[I] eat [apples]"
        tokens = ["I", "eat", "apples"]
        tags = ["PRP", "VBP", "NNS"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- eat
            DepTriple("dobj", 1, 2),     # apples <- eat
            DepTriple("root", -1, 1)     # eat <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should have one predicate with two arguments
        assert len(pp.events) == 1
        pred = pp.events[0]
        assert len(pred.arguments) == 2
        
        # Check arguments and g1 rules
        arg_texts = [a.root.text for a in pred.arguments]
        assert "I" in arg_texts
        assert "apples" in arg_texts
        
        for arg in pred.arguments:
            assert any(isinstance(r, R.g1) for r in arg.rules)
    
    def test_rule_h1_nmod(self):
        """Test h1: Extract nmod arguments."""
        # "I eat [in the park]"
        tokens = ["I", "eat", "in", "the", "park"]
        tags = ["PRP", "VBP", "IN", "DT", "NN"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- eat
            DepTriple("nmod", 1, 4),     # park <- eat
            DepTriple("case", 4, 2),     # in <- park
            DepTriple("det", 4, 3),      # the <- park
            DepTriple("root", -1, 1)     # eat <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should have arguments including "park"
        pred = pp.events[0]
        arg_texts = [a.root.text for a in pred.arguments]
        assert "park" in arg_texts
        
        # Check h1 rule
        park_arg = [a for a in pred.arguments if a.root.text == "park"][0]
        assert any(isinstance(r, R.h1) for r in park_arg.rules)
    
    def test_rule_h2_indirect_nmod(self):
        """Test h2: Extract indirect nmod arguments through advmod."""
        # "I turned away [from the market]"
        tokens = ["I", "turned", "away", "from", "the", "market"]
        tags = ["PRP", "VBD", "RB", "IN", "DT", "NN"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- turned
            DepTriple("advmod", 1, 2),   # away <- turned
            DepTriple("nmod", 2, 5),     # market <- away
            DepTriple("case", 5, 3),     # from <- market
            DepTriple("det", 5, 4),      # the <- market
            DepTriple("root", -1, 1)     # turned <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Should extract "market" as argument via h2
        pred = pp.events[0]
        arg_texts = [a.root.text for a in pred.arguments]
        assert "market" in arg_texts
        
        # Check h2 rule
        market_arg = [a for a in pred.arguments if a.root.text == "market"][0]
        assert any(isinstance(r, R.h2) for r in market_arg.rules)
    
    def test_rule_i_amod_governor(self):
        """Test i: Extract argument from governor of amod."""
        # "The [red] [car]"
        tokens = ["The", "red", "car"]
        tags = ["DT", "ADJ", "NN"]
        triples = [
            DepTriple("det", 2, 0),      # The <- car
            DepTriple("amod", 2, 1),     # red <- car
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(resolve_amod=True)
        pp = PredPatt(parse, opts=opts)
        
        # "red" should be predicate with "car" as argument
        assert len(pp.events) == 1
        pred = pp.events[0]
        assert pred.root.text == "red"
        assert len(pred.arguments) == 1
        assert pred.arguments[0].root.text == "car"
        
        # Check i rule
        assert any(isinstance(r, R.i) for r in pred.arguments[0].rules)
    
    def test_rule_j_appos_governor(self):
        """Test j: Extract argument from governor of apposition."""
        # "[Sam], the CEO"
        tokens = ["Sam", ",", "the", "CEO"]
        tags = ["NNP", ",", "DT", "NN"]
        triples = [
            DepTriple("appos", 0, 3),    # CEO <- Sam
            DepTriple("det", 3, 2),      # the <- CEO
            DepTriple("punct", 3, 1),    # , <- CEO
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(resolve_appos=True)
        pp = PredPatt(parse, opts=opts)
        
        # "CEO" should be predicate with "Sam" as argument
        assert len(pp.events) == 1
        pred = pp.events[0]
        assert pred.root.text == "CEO"
        assert len(pred.arguments) == 1
        assert pred.arguments[0].root.text == "Sam"
        
        # Check j rule
        assert any(isinstance(r, R.j) for r in pred.arguments[0].rules)
    
    def test_rule_w1_w2_poss(self):
        """Test w1/w2: Extract arguments from nmod:poss relation."""
        # "[John]'s [car]"
        tokens = ["John", "'s", "car"]
        tags = ["NNP", "POS", "NN"]
        triples = [
            DepTriple("nmod:poss", 2, 0),  # John <- car
            DepTriple("case", 0, 1),       # 's <- John
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(resolve_poss=True)
        pp = PredPatt(parse, opts=opts)
        
        # "John" should be predicate with both "car" (w1) and "John" (w2) as arguments
        assert len(pp.events) == 1
        pred = pp.events[0]
        assert pred.root.text == "John"
        assert len(pred.arguments) == 2
        
        arg_texts = [a.root.text for a in pred.arguments]
        assert "car" in arg_texts
        assert "John" in arg_texts
        
        # Check w1 and w2 rules
        car_arg = [a for a in pred.arguments if a.root.text == "car"][0]
        john_arg = [a for a in pred.arguments if a.root.text == "John"][0]
        assert any(isinstance(r, R.w1) for r in car_arg.rules)
        assert any(isinstance(r, R.w2) for r in john_arg.rules)
    
    def test_rule_k_ccomp_arg(self):
        """Test k: Extract argument from ccomp dependent."""
        # "They said [he left]"
        tokens = ["They", "said", "he", "left"]
        tags = ["PRP", "VBD", "PRP", "VBD"]
        triples = [
            DepTriple("nsubj", 1, 0),    # They <- said
            DepTriple("ccomp", 1, 3),    # left <- said
            DepTriple("nsubj", 3, 2),    # he <- left
            DepTriple("root", -1, 1)     # said <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # "said" should have "They" and "left" as arguments
        said_pred = [p for p in pp.events if p.root.text == "said"][0]
        arg_texts = [a.root.text for a in said_pred.arguments]
        assert "They" in arg_texts
        assert "left" in arg_texts
        
        # Check k rule
        left_arg = [a for a in said_pred.arguments if a.root.text == "left"][0]
        assert any(isinstance(r, R.k) for r in left_arg.rules)


class TestArgumentResolutionRules:
    """Test argument borrowing and resolution rules."""
    
    def create_parse_with_tokens(self, tokens, tags, triples):
        """Helper to create a UDParse with proper Token objects."""
        # UDParse expects tokens to be strings, not Token objects
        return UDParse(tokens, tags, triples)
    
    def test_borrow_subj_from_conj(self):
        """Test borrowing subject from conjoined predicate."""
        # "[I] run and jump"  (jump should borrow "I")
        tokens = ["I", "run", "and", "jump"]
        tags = ["PRP", "VBP", "CC", "VBP"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- run
            DepTriple("cc", 1, 2),       # and <- run
            DepTriple("conj", 1, 3),     # jump <- run
            DepTriple("root", -1, 1)     # run <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Both predicates should have "I" as subject
        run_pred = [p for p in pp.events if p.root.text == "run"][0]
        jump_pred = [p for p in pp.events if p.root.text == "jump"][0]
        
        assert any(a.root.text == "I" for a in run_pred.arguments)
        assert any(a.root.text == "I" for a in jump_pred.arguments)
        
        # Check borrow_subj rule on jump's argument
        jump_subj = [a for a in jump_pred.arguments if a.root.text == "I"][0]
        assert any(isinstance(r, R.borrow_subj) for r in jump_subj.rules)
    
    def test_l_merge_xcomp_args(self):
        """Test l: Merge xcomp arguments to governor."""
        # "I want to eat apples" with options.cut=True
        tokens = ["I", "want", "to", "eat", "apples"]
        tags = ["PRP", "VBP", "TO", "VB", "NNS"]
        triples = [
            DepTriple("nsubj", 1, 0),    # I <- want
            DepTriple("xcomp", 1, 3),    # eat <- want
            DepTriple("mark", 3, 2),     # to <- eat
            DepTriple("dobj", 3, 4),     # apples <- eat
            DepTriple("root", -1, 1)     # want <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(cut=True)
        pp = PredPatt(parse, opts=opts)
        
        # With cut=True, xcomp creates a separate predicate but borrows arguments
        assert len(pp.events) == 2
        
        # Find the predicates
        want_pred = [p for p in pp.events if p.root.text == "want"][0]
        eat_pred = [p for p in pp.events if p.root.text == "eat"][0]
        
        # Check that eat borrowed subject from want
        eat_arg_texts = [a.root.text for a in eat_pred.arguments]
        assert "I" in eat_arg_texts  # borrowed subject
        assert "apples" in eat_arg_texts  # own object
        
        # Check cut borrow rules
        assert any(isinstance(r, R.cut_borrow_subj) for arg in eat_pred.arguments 
                  for r in arg.rules)


class TestPhraseRules:
    """Test predicate and argument phrase building rules."""
    
    def create_parse_with_tokens(self, tokens, tags, triples):
        """Helper to create a UDParse with proper Token objects."""
        # UDParse expects tokens to be strings, not Token objects
        return UDParse(tokens, tags, triples)
    
    def test_predicate_phrase_rules(self):
        """Test n1-n6 predicate phrase building rules."""
        # "I quickly eat"
        tokens = ["I", "quickly", "eat"]
        tags = ["PRP", "RB", "VBP"]
        triples = [
            DepTriple("nsubj", 2, 0),    # I <- eat
            DepTriple("advmod", 2, 1),   # quickly <- eat
            DepTriple("root", -1, 2)     # eat <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Predicate phrase should include both "quickly" and "eat"
        pred = pp.events[0]
        assert "quickly" in pred.phrase()
        assert "eat" in pred.phrase()
    
    def test_argument_phrase_rules(self):
        """Test argument phrase building rules."""
        # "the big dog"
        tokens = ["the", "big", "dog", "barks"]
        tags = ["DT", "JJ", "NN", "VBZ"]
        triples = [
            DepTriple("det", 2, 0),      # the <- dog
            DepTriple("amod", 2, 1),     # big <- dog
            DepTriple("nsubj", 3, 2),    # dog <- barks
            DepTriple("root", -1, 3)     # barks <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        pp = PredPatt(parse)
        
        # Argument phrase should include all modifiers
        pred = pp.events[0]
        arg = pred.arguments[0]
        assert "the big dog" in arg.phrase()


class TestSimplificationRules:
    """Test pattern simplification rules."""
    
    def create_parse_with_tokens(self, tokens, tags, triples):
        """Helper to create a UDParse with proper Token objects."""
        # UDParse expects tokens to be strings, not Token objects
        return UDParse(tokens, tags, triples)
    
    def test_simple_predicate_rules(self):
        """Test q (remove advmod) and r (remove aux) rules."""
        # "I have quickly eaten"
        tokens = ["I", "have", "quickly", "eaten"]
        tags = ["PRP", "VBP", "RB", "VBN"]
        triples = [
            DepTriple("nsubj", 3, 0),    # I <- eaten
            DepTriple("aux", 3, 1),      # have <- eaten
            DepTriple("advmod", 3, 2),   # quickly <- eaten
            DepTriple("root", -1, 3)     # eaten <- ROOT
        ]
        
        parse = self.create_parse_with_tokens(tokens, tags, triples)
        opts = PredPattOpts(simple=True)
        pp = PredPatt(parse, opts=opts)
        
        # With simple=True, predicate phrase is simplified but still includes arguments
        pred = pp.events[0]
        assert pred.phrase() == "?a eaten"  # phrase() includes argument placeholders
        
        # Check q and r rules were applied
        assert any(isinstance(r, R.q) for r in pred.rules)
        assert any(isinstance(r, R.r) for r in pred.rules)