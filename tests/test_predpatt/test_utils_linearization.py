"""Tests for linearization utilities."""

import pytest

from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.core.predicate import Predicate, NORMAL, POSS
from decomp.semantics.predpatt.core.argument import Argument
from decomp.semantics.predpatt.utils.linearization import (
    LinearizedPPOpts,
    sort_by_position,
    is_dep_of_pred,
    important_pred_tokens,
    likely_to_be_pred,
    argument_names,
    linear_to_string,
    phrase_and_enclose_arg,
    construct_arg_from_flat,
    construct_pred_from_flat,
    check_recoverability,
    pprint,
    ARG_ENC,
    PRED_ENC,
    ARGPRED_ENC,
    ARG_SUF,
    PRED_SUF,
    ARG_HEADER,
    PRED_HEADER,
    SOMETHING,
)
from decomp.semantics.predpatt.utils.ud_schema import dep_v1, postag


class TestLinearizedPPOpts:
    """Test LinearizedPPOpts class."""
    
    def test_default_options(self):
        """Test default option values."""
        opts = LinearizedPPOpts()
        assert opts.recursive is True
        assert opts.distinguish_header is True
        assert opts.only_head is False
    
    def test_custom_options(self):
        """Test custom option values."""
        opts = LinearizedPPOpts(
            recursive=False,
            distinguish_header=False,
            only_head=True
        )
        assert opts.recursive is False
        assert opts.distinguish_header is False
        assert opts.only_head is True


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_sort_by_position(self):
        """Test sorting by position."""
        # Create tokens with different positions
        t1 = Token(2, "world", None)
        t2 = Token(0, "hello", None)
        t3 = Token(1, "beautiful", None)
        
        sorted_tokens = sort_by_position([t1, t2, t3])
        assert [t.text for t in sorted_tokens] == ["hello", "beautiful", "world"]
        assert [t.position for t in sorted_tokens] == [0, 1, 2]
    
    def test_is_dep_of_pred(self):
        """Test predicate dependency checking."""
        # Test various dependency relations
        token = Token(0, "test", None)
        
        # Test subject relations
        token.gov_rel = dep_v1.nsubj
        assert is_dep_of_pred(token) is True
        
        token.gov_rel = dep_v1.nsubjpass
        assert is_dep_of_pred(token) is True
        
        # Test object relations
        token.gov_rel = dep_v1.dobj
        assert is_dep_of_pred(token) is True
        
        token.gov_rel = dep_v1.iobj
        assert is_dep_of_pred(token) is True
        
        # Test clausal relations
        token.gov_rel = dep_v1.ccomp
        assert is_dep_of_pred(token) is True
        
        token.gov_rel = dep_v1.xcomp
        assert is_dep_of_pred(token) is True
        
        # Test modifier relations
        token.gov_rel = dep_v1.nmod
        assert is_dep_of_pred(token) is True
        
        token.gov_rel = dep_v1.advmod
        assert is_dep_of_pred(token) is True
        
        # Test negation
        token.gov_rel = dep_v1.neg
        assert is_dep_of_pred(token) is True
        
        # Test non-predicate dependency - use punct which exists and should not be predicate dep
        token.gov_rel = dep_v1.punct
        assert is_dep_of_pred(token) is None
    
    def test_important_pred_tokens(self):
        """Test extraction of important predicate tokens."""
        # Create predicate with root
        root = Token(1, "eat", None)
        root.tag = postag.VERB
        root.position = 1
        pred = Predicate(root, dep_v1)
        
        # Add negation as direct dependent of the predicate root
        neg = Token(0, "not", None)
        neg.position = 0
        neg.gov = root  # Set governor to be the predicate root
        neg.gov_rel = dep_v1.neg
        pred.tokens = [root, neg]
        
        # Add other token (not important) - use punct which is not important
        punct = Token(2, ".", None)
        punct.position = 2
        punct.gov = root
        punct.gov_rel = dep_v1.punct
        pred.tokens.append(punct)
        
        important = important_pred_tokens(pred)
        assert len(important) == 2
        # tokens should be sorted by position
        assert important[0].text == "not"
        assert important[1].text == "eat"
    
    def test_likely_to_be_pred(self):
        """Test predicate likelihood checking."""
        # Create predicate
        root = Token(0, "run", None)
        pred = Predicate(root, dep_v1)
        
        # No arguments - not likely
        assert likely_to_be_pred(pred) is False
        
        # Add argument
        arg_root = Token(1, "John", None)
        arg = Argument(arg_root, ud=dep_v1)  # Pass ud parameter
        pred.arguments = [arg]
        
        # Verb tag - likely
        root.tag = postag.VERB
        assert likely_to_be_pred(pred) is True
        
        # Adjective tag - likely
        root.tag = postag.ADJ
        assert likely_to_be_pred(pred) is True
        
        # Apposition relation - likely
        root.tag = postag.NOUN
        root.gov_rel = dep_v1.appos
        assert likely_to_be_pred(pred) is True
        
        # Copula in tokens - likely
        root.gov_rel = None
        cop = Token(2, "is", None)
        cop.gov_rel = dep_v1.cop
        pred.tokens = [cop]
        assert likely_to_be_pred(pred) is True


class TestArgumentNames:
    """Test argument naming function."""
    
    def test_basic_naming(self):
        """Test basic argument naming."""
        args = list(range(5))
        names = argument_names(args)
        
        assert names[0] == '?a'
        assert names[1] == '?b'
        assert names[2] == '?c'
        assert names[3] == '?d'
        assert names[4] == '?e'
    
    def test_extended_naming(self):
        """Test naming with more than 26 arguments."""
        args = list(range(30))
        names = argument_names(args)
        
        assert names[0] == '?a'
        assert names[25] == '?z'
        assert names[26] == '?a1'
        assert names[27] == '?b1'
        assert names[28] == '?c1'
        assert names[29] == '?d1'
    
    def test_large_numbers(self):
        """Test naming with large numbers of arguments."""
        args = list(range(100))
        names = argument_names(args)
        
        assert names[0] == '?a'
        assert names[26] == '?a1'
        assert names[52] == '?a2'
        assert names[78] == '?a3'


class TestLinearToString:
    """Test linear to string conversion."""
    
    def test_basic_conversion(self):
        """Test basic token extraction."""
        tokens = [
            ARG_ENC[0],
            "hello" + ARG_SUF,
            ARG_ENC[1],
            "world" + PRED_SUF,
        ]
        
        result = linear_to_string(tokens)
        assert result == ["hello", "world"]
    
    def test_with_headers(self):
        """Test extraction with header markers."""
        tokens = [
            "test" + PRED_HEADER,
            "arg" + ARG_HEADER,
        ]
        
        result = linear_to_string(tokens)
        assert result == ["test", "arg"]
    
    def test_skip_special_tokens(self):
        """Test skipping special tokens."""
        tokens = [
            PRED_ENC[0],
            "hello" + PRED_SUF,
            SOMETHING,
            ARG_ENC[0],
            "world" + ARG_SUF,
            ARG_ENC[1],
            PRED_ENC[1],
        ]
        
        result = linear_to_string(tokens)
        assert result == ["hello", "world"]


class TestPhraseAndEncloseArg:
    """Test argument phrase enclosure."""
    
    def test_full_phrase(self):
        """Test full phrase enclosure."""
        # Create argument with tokens
        root = Token(1, "John", None)
        t2 = Token(2, "Smith", None)
        arg = Argument(root, [])
        arg.tokens = [root, t2]
        
        opt = LinearizedPPOpts(only_head=False, distinguish_header=True)
        result = phrase_and_enclose_arg(arg, opt)
        
        expected = f"{ARG_ENC[0]} John{ARG_HEADER} Smith{ARG_SUF} {ARG_ENC[1]}"
        assert result == expected
    
    def test_only_head(self):
        """Test head-only enclosure."""
        root = Token(1, "John", None)
        arg = Argument(root, [])
        
        opt = LinearizedPPOpts(only_head=True, distinguish_header=True)
        result = phrase_and_enclose_arg(arg, opt)
        
        expected = f"{ARG_ENC[0]} John{ARG_HEADER} {ARG_ENC[1]}"
        assert result == expected
    
    def test_no_header_distinction(self):
        """Test without header distinction."""
        root = Token(1, "John", None)
        arg = Argument(root, [])
        
        opt = LinearizedPPOpts(only_head=True, distinguish_header=False)
        result = phrase_and_enclose_arg(arg, opt)
        
        expected = f"{ARG_ENC[0]} John{ARG_SUF} {ARG_ENC[1]}"
        assert result == expected


class TestConstructArgFromFlat:
    """Test argument construction from flat tokens."""
    
    def test_basic_construction(self):
        """Test basic argument construction."""
        tokens = [
            (0, "John" + ARG_HEADER),
            (1, "Smith" + ARG_SUF),
            (2, ARG_ENC[1])
        ]
        
        tokens_iter = iter(tokens)
        arg = construct_arg_from_flat(tokens_iter)
        
        assert arg.root.text == "John"
        assert arg.root.position == 0
        assert len(arg.tokens) == 2
        assert arg.tokens[0].text == "John"
        assert arg.tokens[1].text == "Smith"
    
    def test_no_header(self):
        """Test construction without header."""
        tokens = [
            (0, "test" + ARG_SUF),
            (1, ARG_ENC[1])
        ]
        
        tokens_iter = iter(tokens)
        arg = construct_arg_from_flat(tokens_iter)
        
        # When no header, position is set to last token position
        assert arg.position == 1
        assert len(arg.tokens) == 1
        assert arg.tokens[0].text == "test"


class TestCheckRecoverability:
    """Test recoverability checking."""
    
    def test_valid_structure(self):
        """Test valid linearized structure."""
        tokens = [
            PRED_ENC[0],
            "test" + PRED_SUF,
            ARG_ENC[0],
            "arg" + ARG_SUF,
            ARG_ENC[1],
            PRED_ENC[1]
        ]
        
        is_recoverable, _ = check_recoverability(tokens)
        assert is_recoverable is True
    
    def test_invalid_start(self):
        """Test invalid starting token."""
        tokens = [
            ARG_ENC[0],  # Should start with PRED_ENC
            "test" + ARG_SUF,
            ARG_ENC[1]
        ]
        
        is_recoverable, _ = check_recoverability(tokens)
        assert is_recoverable is False
    
    def test_unmatched_brackets(self):
        """Test unmatched brackets."""
        tokens = [
            PRED_ENC[0],
            "test" + PRED_SUF,
            ARG_ENC[0],
            "arg" + ARG_SUF,
            # Missing ARG_ENC[1]
            PRED_ENC[1]
        ]
        
        is_recoverable, _ = check_recoverability(tokens)
        assert is_recoverable is False


class TestPprint:
    """Test pretty printing."""
    
    def test_basic_pprint(self):
        """Test basic pretty printing."""
        s = "^((( test:p ^(( arg:a ))$ )))$"
        result = pprint(s)
        expected = "[ test:p ( arg:a ) ]"
        assert result == expected
    
    def test_argpred_pprint(self):
        """Test argument predicate pretty printing."""
        s = "^(((:a test:p )))$:a"
        result = pprint(s)
        expected = "[ test:p ]"
        assert result == expected