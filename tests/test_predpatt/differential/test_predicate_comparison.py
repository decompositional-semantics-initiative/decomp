"""
Compare the original Predicate class with the modernized Predicate class.

This test ensures that both implementations have identical behavior.
"""

import pytest

# Skip these tests if external predpatt is not installed
predpatt = pytest.importorskip("predpatt")
from predpatt.patt import (
    Token as OriginalToken,
    Predicate as OriginalPredicate, 
    Argument as OriginalArgument,
    NORMAL as ORIG_NORMAL,
    POSS as ORIG_POSS,
    APPOS as ORIG_APPOS,
    AMOD as ORIG_AMOD,
    argument_names as orig_argument_names,
    no_color as orig_no_color
)
from decomp.semantics.predpatt.core.token import Token as ModernToken
from decomp.semantics.predpatt.core.predicate import (
    Predicate as ModernPredicate,
    NORMAL as MOD_NORMAL,
    POSS as MOD_POSS,
    APPOS as MOD_APPOS,
    AMOD as MOD_AMOD,
    argument_names as mod_argument_names,
    no_color as mod_no_color
)
from decomp.semantics.predpatt.core.argument import Argument as ModernArgument
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, dep_v2
from decomp.semantics.predpatt.parsing.udparse import DepTriple
from decomp.semantics.predpatt import rules
from decomp.semantics.predpatt.rules import *
R = rules  # Compatibility alias


class TestPredicateComparison:
    """Test that original and modern Predicate classes behave identically."""
    
    def test_constants_identical(self):
        """Test predicate type constants are identical."""
        assert ORIG_NORMAL == MOD_NORMAL == "normal"
        assert ORIG_POSS == MOD_POSS == "poss"
        assert ORIG_APPOS == MOD_APPOS == "appos"
        assert ORIG_AMOD == MOD_AMOD == "amod"
    
    def test_argument_names_identical(self):
        """Test argument_names function produces identical output."""
        args = list(range(30))
        orig_names = orig_argument_names(args)
        mod_names = mod_argument_names(args)
        
        for arg in args:
            assert orig_names[arg] == mod_names[arg]
    
    def test_initialization_identical(self):
        """Test both classes initialize with same attributes."""
        root = OriginalToken(position=5, text="eat", tag="VB")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        assert orig.root == modern.root
        assert orig.rules == modern.rules
        assert orig.position == modern.position
        # Both should have a ud attribute, but they may be different classes
        # What matters is they produce the same behavior, not that they're the same class
        assert hasattr(orig, 'ud')
        assert hasattr(modern, 'ud')
        assert len(orig.arguments) == len(modern.arguments) == 0
        assert orig.type == modern.type == ORIG_NORMAL
        assert len(orig.tokens) == len(modern.tokens) == 0
    
    def test_repr_identical(self):
        """Test both classes have same string representation."""
        root = OriginalToken(position=3, text="eat", tag="VB")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        assert repr(orig) == repr(modern) == "Predicate(eat/3)"
    
    def test_identifier_identical(self):
        """Test identifier method produces same results."""
        root = OriginalToken(position=5, text="eat", tag="VB")
        
        orig = OriginalPredicate(root, type_=ORIG_POSS)
        modern = ModernPredicate(root, type_=MOD_POSS)
        
        # add arguments
        arg1 = OriginalArgument(OriginalToken(position=2, text="cat", tag="NN"))
        arg2 = OriginalArgument(OriginalToken(position=7, text="food", tag="NN"))
        orig.arguments = [arg1, arg2]
        modern.arguments = [arg1, arg2]  # can share since we're just testing
        
        assert orig.identifier() == modern.identifier() == "pred.poss.5.2.7"
    
    def test_has_token_identical(self):
        """Test has_token method behaves identically."""
        root = OriginalToken(position=2, text="eat", tag="VB")
        token1 = OriginalToken(position=1, text="will", tag="MD")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        orig.tokens = [token1, root]
        modern.tokens = [token1, root]
        
        # test with token at position 1
        test_token = OriginalToken(position=1, text="anything", tag="XX")
        assert orig.has_token(test_token) == modern.has_token(test_token) == True
        
        # test with token at position 3
        test_token2 = OriginalToken(position=3, text="not", tag="RB")
        assert orig.has_token(test_token2) == modern.has_token(test_token2) == False
    
    def test_subj_obj_methods_identical(self):
        """Test subject/object methods behave identically."""
        root = OriginalToken(position=2, text="eat", tag="VB")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        # no arguments
        assert orig.has_subj() == modern.has_subj() == False
        assert orig.has_obj() == modern.has_obj() == False
        assert orig.subj() == modern.subj() == None
        assert orig.obj() == modern.obj() == None
        
        # add subject
        subj_root = OriginalToken(position=1, text="I", tag="PRP")
        subj_root.gov_rel = dep_v1.nsubj
        subj_arg = OriginalArgument(subj_root)
        
        orig.arguments = [subj_arg]
        modern.arguments = [subj_arg]
        
        assert orig.has_subj() == modern.has_subj() == True
        assert orig.subj() == modern.subj() == subj_arg
    
    def test_share_subj_identical(self):
        """Test share_subj returns same values."""
        root1 = OriginalToken(position=2, text="eat", tag="VB")
        orig1 = OriginalPredicate(root1)
        modern1 = ModernPredicate(root1)
        
        root2 = OriginalToken(position=5, text="sleep", tag="VB")
        orig2 = OriginalPredicate(root2)
        modern2 = ModernPredicate(root2)
        
        # no subject
        result_orig = orig1.share_subj(orig2)
        result_modern = modern1.share_subj(modern2)
        assert result_orig == result_modern == None
    
    def test_has_borrowed_arg_identical(self):
        """Test has_borrowed_arg behaves identically."""
        root = OriginalToken(position=2, text="eat", tag="VB")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        # regular argument
        arg_root = OriginalToken(position=1, text="I", tag="PRP")
        arg = OriginalArgument(arg_root)
        
        orig.arguments = [arg]
        modern.arguments = [arg]
        
        assert orig.has_borrowed_arg() == modern.has_borrowed_arg() == False
        
        # with share and rules
        arg.share = True
        edge = DepTriple(rel=dep_v1.nsubj, gov=root, dep=arg_root)
        arg.rules = [R.g1(edge)]
        
        assert orig.has_borrowed_arg() == modern.has_borrowed_arg() == True
    
    def test_is_broken_identical(self):
        """Test is_broken method returns same values."""
        root = OriginalToken(position=2, text="'s", tag="POS")
        
        orig = OriginalPredicate(root, type_=ORIG_POSS)
        modern = ModernPredicate(root, type_=MOD_POSS)
        
        # empty tokens
        assert orig.is_broken() == modern.is_broken() == True
        
        # add tokens but wrong arg count for POSS
        orig.tokens = [root]
        modern.tokens = [root]
        
        assert orig.is_broken() == modern.is_broken() == True
        
        # add correct number of arguments
        arg1 = OriginalArgument(OriginalToken(position=1, text="John", tag="NNP"))
        arg1.tokens = [arg1.root]
        arg2 = OriginalArgument(OriginalToken(position=3, text="book", tag="NN"))
        arg2.tokens = [arg2.root]
        
        orig.arguments = [arg1, arg2]
        modern.arguments = [arg1, arg2]
        
        assert orig.is_broken() == modern.is_broken() == None
    
    def test_phrase_identical(self):
        """Test phrase method produces identical output."""
        root = OriginalToken(position=2, text="eat", tag="VB")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        orig.tokens = [root]
        modern.tokens = [root]
        
        # add arguments
        arg1_root = OriginalToken(position=1, text="I", tag="PRP")
        arg2_root = OriginalToken(position=3, text="apple", tag="NN")
        arg1 = OriginalArgument(arg1_root)
        arg2 = OriginalArgument(arg2_root)
        
        orig.arguments = [arg1, arg2]
        modern.arguments = [arg1, arg2]
        
        assert orig.phrase() == modern.phrase()
    
    def test_format_identical(self):
        """Test format method produces identical output."""
        root = OriginalToken(position=2, text="eat", tag="VB")
        
        orig = OriginalPredicate(root)
        modern = ModernPredicate(root)
        
        orig.tokens = [root]
        modern.tokens = [root]
        
        # add arguments
        arg_root = OriginalToken(position=1, text="I", tag="PRP")
        arg_root.gov_rel = dep_v1.nsubj
        arg = OriginalArgument(arg_root)
        arg.tokens = [arg_root]
        
        orig.arguments = [arg]
        modern.arguments = [arg]
        
        # compare basic format
        orig_output = orig.format(track_rule=False)
        modern_output = modern.format(track_rule=False)
        
        assert orig_output == modern_output
    
    def test_format_predicate_types_identical(self):
        """Test _format_predicate for different predicate types."""
        # test POSS type
        root = OriginalToken(position=2, text="'s", tag="POS")
        
        orig = OriginalPredicate(root, type_=ORIG_POSS)
        modern = ModernPredicate(root, type_=MOD_POSS)
        
        arg1 = OriginalArgument(OriginalToken(position=1, text="John", tag="NNP"))
        arg2 = OriginalArgument(OriginalToken(position=3, text="book", tag="NN"))
        
        orig.arguments = [arg1, arg2]
        modern.arguments = [arg1, arg2]
        
        names = orig_argument_names([arg1, arg2])
        
        orig_result = orig._format_predicate(names)
        modern_result = modern._format_predicate(names)
        
        assert orig_result == modern_result == "?a poss ?b"