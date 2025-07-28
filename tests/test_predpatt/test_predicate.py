"""
Tests for Predicate class to document and verify current behavior.

Predicate Class Documentation
============================

The Predicate class represents a predicate extracted from a dependency parse.

Predicate Types
--------------
NORMAL = "normal" : Regular predicates (verbs, etc.)
POSS = "poss"     : Possessive predicates (X's Y)
APPOS = "appos"   : Appositive predicates (X is/are Y)
AMOD = "amod"     : Adjectival modifier predicates (X is/are ADJ)

Attributes
----------
root : Token
    The root token of the predicate.
rules : list
    List of rules that led to this predicate's extraction.
position : int
    Position of the root token (copied from root.position).
ud : module
    The Universal Dependencies module (dep_v1 or dep_v2).
arguments : list[Argument]
    List of arguments associated with this predicate.
type : str
    Type of predicate (NORMAL, POSS, APPOS, or AMOD).
tokens : list[Token]
    List of tokens that form the predicate phrase.

Methods
-------
__init__(root, ud=dep_v1, rules=[], type_=NORMAL)
    Initialize a Predicate.
__repr__()
    Return string representation as 'Predicate(root)'.
copy()
    Create a copy of the predicate with shared arguments.
identifier()
    Return unique identifier in format 'pred.{type}.{position}.{arg_positions}'.
has_token(token)
    Check if predicate contains a token at given position.
has_subj() / subj()
    Check for / return subject argument.
has_obj() / obj()
    Check for / return object argument.
share_subj(other)
    Check if two predicates share the same subject.
has_borrowed_arg()
    Check if any argument is borrowed (shared).
phrase()
    Return the predicate phrase with argument placeholders.
is_broken()
    Check if predicate is malformed.
_format_predicate(name, C=no_color)
    Format predicate with argument names and coloring.
format(track_rule, C=no_color, indent='\t')
    Format complete predicate with arguments for display.

String Formatting Patterns
-------------------------
NORMAL: Tokens and arguments mixed by position order
POSS: "?a 's ?b" (always exactly 2 arguments)
APPOS/AMOD: "?a is/are [tokens]" (subject first, then "is/are", then rest)

Special Cases:
- xcomp with non-VERB/ADJ adds "is/are" after first argument
- Clausal arguments show as "SOMETHING := [phrase]"
- Arguments named ?a, ?b, ?c... ?z, ?a1, ?b1, etc.
"""

import pytest
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.core.predicate import (
    Predicate, NORMAL, POSS, APPOS, AMOD,
    argument_names, no_color
)
from decomp.semantics.predpatt.core.argument import Argument
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, dep_v2, postag
from decomp.semantics.predpatt import rules
from decomp.semantics.predpatt.rules import *
R = rules  # Compatibility alias
from decomp.semantics.predpatt.parsing.udparse import DepTriple


class TestPredicateInitialization:
    """Test Predicate initialization behavior."""
    
    def test_basic_initialization(self):
        """Test basic Predicate creation with defaults."""
        root_token = Token(position=5, text="eat", tag="VB")
        pred = Predicate(root_token)
        
        assert pred.root == root_token
        assert pred.rules == []
        assert pred.position == 5
        assert pred.ud == dep_v1
        assert pred.arguments == []
        assert pred.type == NORMAL
        assert pred.tokens == []
    
    def test_initialization_with_params(self):
        """Test Predicate creation with all parameters."""
        root_token = Token(position=3, text="have", tag="VB")
        rules = [R.a1(), R.b()]
        
        pred = Predicate(root_token, ud=dep_v2, rules=rules, type_=POSS)
        
        assert pred.root == root_token
        assert pred.rules == rules
        assert pred.position == 3
        assert pred.ud == dep_v2
        assert pred.type == POSS
        assert pred.arguments == []
        assert pred.tokens == []
    
    def test_all_predicate_types(self):
        """Test initialization with each predicate type."""
        root = Token(position=0, text="test", tag="NN")
        
        normal_pred = Predicate(root, type_=NORMAL)
        assert normal_pred.type == "normal"
        
        poss_pred = Predicate(root, type_=POSS)
        assert poss_pred.type == "poss"
        
        appos_pred = Predicate(root, type_=APPOS)
        assert appos_pred.type == "appos"
        
        amod_pred = Predicate(root, type_=AMOD)
        assert amod_pred.type == "amod"


class TestPredicateRepr:
    """Test Predicate string representation."""
    
    def test_repr_format(self):
        """Test __repr__ returns Predicate(root)."""
        root = Token(position=2, text="run", tag="VB")
        pred = Predicate(root)
        
        assert repr(pred) == "Predicate(run/2)"
    
    def test_repr_with_different_roots(self):
        """Test repr with various root tokens."""
        root1 = Token(position=0, text="", tag="VB")
        pred1 = Predicate(root1)
        assert repr(pred1) == "Predicate(/0)"
        
        root2 = Token(position=-1, text="ROOT", tag="ROOT")
        pred2 = Predicate(root2)
        assert repr(pred2) == "Predicate(ROOT/-1)"


class TestPredicateCopy:
    """Test Predicate copy method."""
    
    def test_copy_basic(self):
        """Test copying a basic predicate."""
        root = Token(position=1, text="eat", tag="VB")
        pred = Predicate(root, rules=[R.a1()], type_=NORMAL)
        pred.tokens = [root]
        
        copy = pred.copy()
        
        # verify attributes are copied
        assert copy.root == pred.root  # same token reference
        assert copy.rules == pred.rules
        assert copy.position == pred.position
        assert copy.ud == pred.ud
        assert copy.type == pred.type
        assert copy.tokens == pred.tokens
        assert copy.tokens is not pred.tokens  # different list
    
    def test_copy_with_arguments(self):
        """Test copying preserves argument references."""
        root = Token(position=1, text="eat", tag="VB")
        pred = Predicate(root)
        
        # add arguments
        arg1_root = Token(position=0, text="I", tag="PRP")
        arg1 = Argument(arg1_root)
        pred.arguments = [arg1]
        
        copy = pred.copy()
        
        # arguments should be references (share=True)
        assert len(copy.arguments) == 1
        assert copy.arguments[0].share is True
        assert copy.arguments[0].root == arg1.root


class TestPredicateIdentifier:
    """Test Predicate identifier method."""
    
    def test_identifier_format(self):
        """Test identifier format: pred.{type}.{position}.{arg_positions}."""
        root = Token(position=5, text="eat", tag="VB")
        pred = Predicate(root, type_=NORMAL)
        
        # no arguments
        assert pred.identifier() == "pred.normal.5."
        
        # with arguments
        arg1_root = Token(position=2, text="cat", tag="NN")
        arg2_root = Token(position=7, text="fish", tag="NN")
        pred.arguments = [Argument(arg1_root), Argument(arg2_root)]
        
        assert pred.identifier() == "pred.normal.5.2.7"
    
    def test_identifier_different_types(self):
        """Test identifier with different predicate types."""
        root = Token(position=3, text="'s", tag="POS")
        
        poss_pred = Predicate(root, type_=POSS)
        assert poss_pred.identifier() == "pred.poss.3."
        
        appos_pred = Predicate(root, type_=APPOS)
        assert appos_pred.identifier() == "pred.appos.3."


class TestPredicateTokenMethods:
    """Test token-related methods."""
    
    def test_has_token(self):
        """Test has_token method."""
        root = Token(position=2, text="eat", tag="VB")
        token1 = Token(position=1, text="will", tag="MD")
        token2 = Token(position=3, text="quickly", tag="RB")
        
        pred = Predicate(root)
        pred.tokens = [token1, root]
        
        # token at position 1 is in tokens
        test_token = Token(position=1, text="anything", tag="XX")
        assert pred.has_token(test_token) is True
        
        # token at position 3 is not in tokens
        assert pred.has_token(token2) is False
        
        # position is what matters, not the token object
        assert pred.has_token(Token(position=2, text="different", tag="YY")) is True


class TestPredicateArgumentMethods:
    """Test argument-related methods."""
    
    def test_has_subj_and_subj(self):
        """Test has_subj() and subj() methods."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root)
        
        # no arguments
        assert pred.has_subj() is False
        assert pred.subj() is None
        
        # add non-subject argument
        obj_root = Token(position=3, text="apple", tag="NN")
        obj_root.gov_rel = dep_v1.dobj
        obj_arg = Argument(obj_root)
        pred.arguments = [obj_arg]
        
        assert pred.has_subj() is False
        assert pred.subj() is None
        
        # add subject argument
        subj_root = Token(position=1, text="I", tag="PRP")
        subj_root.gov_rel = dep_v1.nsubj
        subj_arg = Argument(subj_root)
        pred.arguments = [obj_arg, subj_arg]
        
        assert pred.has_subj() is True
        assert pred.subj() == subj_arg
    
    def test_has_obj_and_obj(self):
        """Test has_obj() and obj() methods."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root)
        
        # no arguments
        assert pred.has_obj() is False
        assert pred.obj() is None
        
        # add direct object
        dobj_root = Token(position=3, text="apple", tag="NN")
        dobj_root.gov_rel = dep_v1.dobj
        dobj_arg = Argument(dobj_root)
        pred.arguments = [dobj_arg]
        
        assert pred.has_obj() is True
        assert pred.obj() == dobj_arg
        
        # indirect object also counts
        iobj_root = Token(position=4, text="me", tag="PRP")
        iobj_root.gov_rel = dep_v1.iobj
        iobj_arg = Argument(iobj_root)
        pred.arguments = [dobj_arg, iobj_arg]
        
        assert pred.has_obj() is True
        assert pred.obj() == dobj_arg  # returns first object
    
    def test_share_subj(self):
        """Test share_subj method."""
        # create two predicates
        root1 = Token(position=2, text="eat", tag="VB")
        pred1 = Predicate(root1)
        
        root2 = Token(position=5, text="sleep", tag="VB")
        pred2 = Predicate(root2)
        
        # same subject token
        subj_root = Token(position=1, text="I", tag="PRP")
        subj_root.gov_rel = dep_v1.nsubj
        
        pred1.arguments = [Argument(subj_root)]
        pred2.arguments = [Argument(subj_root)]
        
        assert pred1.share_subj(pred2) is True
        
        # different subject positions
        subj_root2 = Token(position=10, text="he", tag="PRP")
        subj_root2.gov_rel = dep_v1.nsubj
        pred2.arguments = [Argument(subj_root2)]
        
        assert pred1.share_subj(pred2) is False
        
        # no subject in pred2
        pred2.arguments = []
        assert pred1.share_subj(pred2) is None  # returns None, not False
    
    def test_has_borrowed_arg(self):
        """Test has_borrowed_arg method."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root)
        
        # regular argument with no rules
        arg_root = Token(position=1, text="I", tag="PRP")
        arg = Argument(arg_root)
        pred.arguments = [arg]
        
        assert pred.has_borrowed_arg() is False
        
        # borrowed argument needs both share=True AND rules
        arg.share = True
        # Due to mutable default, arg.rules might not be empty after other tests
        # Force clear the rules to test the behavior we want
        arg.rules = []
        assert pred.has_borrowed_arg() is False  # still False without rules
        
        # add a rule to make it truly borrowed
        arg.rules = [R.g1(DepTriple(rel=dep_v1.nsubj, gov=root, dep=arg_root))]
        assert pred.has_borrowed_arg() is True


class TestPredicatePhrase:
    """Test phrase generation."""
    
    def test_phrase_calls_format_predicate(self):
        """Test that phrase() calls _format_predicate with argument names."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root)
        pred.tokens = [root]
        
        # add arguments
        arg1_root = Token(position=1, text="I", tag="PRP")
        arg2_root = Token(position=3, text="apple", tag="NN")
        pred.arguments = [Argument(arg1_root), Argument(arg2_root)]
        
        phrase = pred.phrase()
        
        # should have argument placeholders
        assert "?a" in phrase
        assert "?b" in phrase
        assert "eat" in phrase


class TestPredicateIsBroken:
    """Test is_broken method."""
    
    def test_empty_tokens(self):
        """Test predicate with no tokens is broken."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root)
        pred.tokens = []  # empty
        
        assert pred.is_broken() is True
        
        # with tokens
        pred.tokens = [root]
        assert pred.is_broken() is None  # returns None, not False
    
    def test_empty_argument_tokens(self):
        """Test predicate with empty argument is broken."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root)
        pred.tokens = [root]
        
        # add argument with no tokens
        arg_root = Token(position=1, text="I", tag="PRP")
        arg = Argument(arg_root)
        arg.tokens = []  # empty
        pred.arguments = [arg]
        
        assert pred.is_broken() is True
    
    def test_poss_wrong_arg_count(self):
        """Test POSS predicate must have exactly 2 arguments."""
        root = Token(position=2, text="'s", tag="POS")
        pred = Predicate(root, type_=POSS)
        pred.tokens = [root]
        
        # 0 arguments
        assert pred.is_broken() is True
        
        # 1 argument
        arg1 = Argument(Token(position=1, text="John", tag="NNP"))
        arg1.tokens = [arg1.root]
        pred.arguments = [arg1]
        assert pred.is_broken() is True
        
        # 2 arguments - correct
        arg2 = Argument(Token(position=3, text="book", tag="NN"))
        arg2.tokens = [arg2.root]
        pred.arguments = [arg1, arg2]
        assert pred.is_broken() is None  # returns None when not broken
        
        # 3 arguments
        arg3 = Argument(Token(position=4, text="cover", tag="NN"))
        arg3.tokens = [arg3.root]
        pred.arguments = [arg1, arg2, arg3]
        assert pred.is_broken() is True


class TestPredicateFormatPredicate:
    """Test _format_predicate method for each type."""
    
    def test_format_normal_predicate(self):
        """Test formatting NORMAL predicates."""
        root = Token(position=2, text="eat", tag="VB")
        aux = Token(position=1, text="will", tag="MD")
        pred = Predicate(root, type_=NORMAL)
        pred.tokens = [aux, root]  # "will eat"
        
        # add arguments
        arg1_root = Token(position=0, text="I", tag="PRP")
        arg2_root = Token(position=3, text="apple", tag="NN")
        arg1 = Argument(arg1_root)
        arg2 = Argument(arg2_root)
        pred.arguments = [arg1, arg2]
        
        names = argument_names(pred.arguments)
        result = pred._format_predicate(names, C=no_color)
        
        # should be ordered by position: arg1 aux root arg2
        assert result == "?a will eat ?b"
    
    def test_format_poss_predicate(self):
        """Test formatting POSS predicates."""
        root = Token(position=2, text="'s", tag="POS")
        pred = Predicate(root, type_=POSS)
        pred.tokens = [root]
        
        # POSS needs exactly 2 arguments
        arg1_root = Token(position=1, text="John", tag="NNP")
        arg2_root = Token(position=3, text="book", tag="NN")
        arg1 = Argument(arg1_root)
        arg2 = Argument(arg2_root)
        pred.arguments = [arg1, arg2]
        
        names = argument_names(pred.arguments)
        result = pred._format_predicate(names, C=no_color)
        
        # POSS format: arg1 's arg2
        assert result == "?a poss ?b"
    
    def test_format_appos_predicate(self):
        """Test formatting APPOS predicates."""
        gov_token = Token(position=1, text="CEO", tag="NN")
        root = Token(position=3, text="leader", tag="NN")
        root.gov = gov_token
        
        pred = Predicate(root, type_=APPOS)
        pred.tokens = [root]
        
        # for APPOS, one arg should be the governor
        arg1 = Argument(gov_token)  # the governor
        arg2 = Argument(Token(position=2, text="the", tag="DT"))
        pred.arguments = [arg1, arg2]
        
        names = argument_names(pred.arguments)
        result = pred._format_predicate(names, C=no_color)
        
        # APPOS format: gov_arg is/are other_tokens_and_args
        assert "?a is/are" in result
        assert "leader" in result
    
    def test_format_amod_predicate(self):
        """Test formatting AMOD predicates."""
        gov_token = Token(position=1, text="man", tag="NN")
        root = Token(position=2, text="tall", tag="JJ")
        root.gov = gov_token
        
        pred = Predicate(root, type_=AMOD)
        pred.tokens = [root]
        
        # for AMOD, typically the modified noun is an argument
        arg1 = Argument(gov_token)
        pred.arguments = [arg1]
        
        names = argument_names(pred.arguments)
        result = pred._format_predicate(names, C=no_color)
        
        # AMOD format: arg is/are adj
        assert result == "?a is/are tall"
    
    def test_format_xcomp_special_case(self):
        """Test xcomp with non-VERB/ADJ adds is/are."""
        root = Token(position=2, text="president", tag="NN")
        root.gov_rel = dep_v1.xcomp
        
        pred = Predicate(root, type_=NORMAL)
        pred.tokens = [root]
        
        # first argument should get is/are after it
        arg1_root = Token(position=1, text="him", tag="PRP")
        arg1 = Argument(arg1_root)
        pred.arguments = [arg1]
        
        names = argument_names(pred.arguments)
        result = pred._format_predicate(names, C=no_color)
        
        # xcomp + non-VERB/ADJ: arg is/are tokens
        assert result == "?a is/are president"


class TestPredicateFormat:
    """Test the full format method."""
    
    def test_format_basic(self):
        """Test basic formatting without tracking rules."""
        root = Token(position=2, text="eat", tag="VB")
        pred = Predicate(root, type_=NORMAL)
        pred.tokens = [root]
        
        # add arguments
        arg1_root = Token(position=1, text="I", tag="PRP")
        arg1_root.gov_rel = dep_v1.nsubj
        arg1 = Argument(arg1_root)
        arg1.tokens = [arg1_root]
        
        arg2_root = Token(position=3, text="apple", tag="NN")
        arg2_root.gov_rel = dep_v1.dobj
        arg2 = Argument(arg2_root)
        arg2.tokens = [arg2_root]
        
        pred.arguments = [arg1, arg2]
        
        result = pred.format(track_rule=False)
        lines = result.split('\n')
        
        assert len(lines) == 3
        assert lines[0] == "\t?a eat ?b"
        assert lines[1] == "\t\t?a: I"
        assert lines[2] == "\t\t?b: apple"
    
    def test_format_with_tracking(self):
        """Test formatting with rule tracking."""
        root = Token(position=2, text="eat", tag="VB")
        root.gov_rel = "root"
        pred = Predicate(root, type_=NORMAL, rules=[R.a1()])
        pred.tokens = [root]
        
        arg_root = Token(position=1, text="I", tag="PRP")
        arg_root.gov_rel = dep_v1.nsubj
        # g1 needs an edge object with rel attribute
        edge = DepTriple(rel=dep_v1.nsubj, gov=root, dep=arg_root)
        arg = Argument(arg_root, rules=[R.g1(edge)])
        arg.tokens = [arg_root]
        pred.arguments = [arg]
        
        result = pred.format(track_rule=True)
        
        # should include rule information in magenta
        assert "[eat-root,a1]" in result
        assert "[I-nsubj,g1(nsubj)]" in result
    
    def test_format_clausal_argument(self):
        """Test formatting with clausal argument."""
        root = Token(position=1, text="know", tag="VB")
        pred = Predicate(root, type_=NORMAL)
        pred.tokens = [root]
        
        # clausal argument
        arg_root = Token(position=3, text="coming", tag="VBG")
        arg_root.gov_rel = dep_v1.ccomp
        arg_root.gov = root  # governed by predicate root
        arg = Argument(arg_root)
        arg.tokens = [Token(position=2, text="he's", tag="PRP"), arg_root]
        pred.arguments = [arg]
        
        result = pred.format(track_rule=False)
        
        # clausal args show as SOMETHING := phrase
        assert "SOMETHING := he's coming" in result
    
    def test_format_with_custom_indent(self):
        """Test formatting with custom indentation."""
        root = Token(position=1, text="eat", tag="VB")
        pred = Predicate(root)
        pred.tokens = [root]
        
        result = pred.format(track_rule=False, indent="  ")
        
        assert result.startswith("  ")  # uses custom indent
        assert not result.startswith("\t")  # not default tab


class TestArgumentNames:
    """Test the argument_names helper function."""
    
    def test_argument_names_basic(self):
        """Test basic argument naming."""
        args = list(range(5))
        names = argument_names(args)
        
        assert names[0] == "?a"
        assert names[1] == "?b"
        assert names[2] == "?c"
        assert names[3] == "?d"
        assert names[4] == "?e"
    
    def test_argument_names_wraparound(self):
        """Test argument naming beyond 26."""
        args = list(range(30))
        names = argument_names(args)
        
        # first 26: ?a through ?z
        assert names[0] == "?a"
        assert names[25] == "?z"
        
        # after 26: the formula is c = i // 26 if i >= 26 else ''
        # so for i=26: c = 26 // 26 = 1, letter = chr(97 + 26%26) = chr(97) = 'a'
        assert names[26] == "?a1"
        assert names[27] == "?b1"
        assert names[28] == "?c1"
        assert names[29] == "?d1"
    
    def test_argument_names_large_numbers(self):
        """Test argument naming with large numbers."""
        # argument_names uses enumerate, so it's based on index not the value
        args = [52, 53, 54]  # these are the actual arguments (could be any objects)
        names = argument_names(args)
        
        # the first three args get names based on their index (0, 1, 2)
        assert names[52] == "?a"  # index 0
        assert names[53] == "?b"  # index 1  
        assert names[54] == "?c"  # index 2