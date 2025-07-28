#!/usr/bin/env python
"""Tests for visualization and output formatting functions."""

from decomp.semantics.predpatt.core.argument import Argument
from decomp.semantics.predpatt.core.predicate import AMOD, NORMAL, POSS, Predicate
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.utils.ud_schema import dep_v1
from decomp.semantics.predpatt.utils.visualization import (
    argument_names,
    format_predicate,
    format_predicate_instance,
    no_color,
)


class TestArgumentNames:
    """Test argument naming function."""

    def test_basic_naming(self):
        """Test basic argument naming up to 26 arguments."""
        args = list(range(26))
        names = argument_names(args)

        assert names[0] == '?a'
        assert names[1] == '?b'
        assert names[25] == '?z'

    def test_extended_naming(self):
        """Test argument naming beyond 26 arguments."""
        args = list(range(100))
        names = argument_names(args)

        # First 26
        assert names[0] == '?a'
        assert names[25] == '?z'

        # Next 26
        assert names[26] == '?a1'
        assert names[51] == '?z1'

        # Third set
        assert names[52] == '?a2'
        assert names[77] == '?z2'

        # Test specific cases from docstring
        assert [names[i] for i in range(0, 100, 26)] == ['?a', '?a1', '?a2', '?a3']
        assert [names[i] for i in range(1, 100, 26)] == ['?b', '?b1', '?b2', '?b3']


class TestFormatPredicate:
    """Test predicate formatting function."""

    def setup_method(self):
        """Set up test data."""
        # Create tokens
        self.token1 = Token(1, "likes", "VERB", ud=dep_v1)
        self.token2 = Token(0, "John", "NOUN", ud=dep_v1)  # Subject comes first
        self.token3 = Token(2, "Mary", "NOUN", ud=dep_v1)

        # Create arguments
        self.arg1 = Argument(self.token2, ud=dep_v1)
        self.arg1.tokens = [self.token2]
        self.arg1.position = 0  # Subject position
        self.arg2 = Argument(self.token3, ud=dep_v1)
        self.arg2.tokens = [self.token3]
        self.arg2.position = 2  # Object position

    def test_normal_predicate(self):
        """Test formatting of normal predicate."""
        pred = Predicate(self.token1, ud=dep_v1)
        pred.type = NORMAL
        pred.tokens = [self.token1]
        pred.arguments = [self.arg1, self.arg2]

        names = {self.arg1: '?a', self.arg2: '?b'}
        result = format_predicate(pred, names, no_color)

        assert result == '?a likes ?b'

    def test_poss_predicate(self):
        """Test formatting of possessive predicate."""
        pred = Predicate(self.token1, ud=dep_v1)
        pred.type = POSS
        pred.arguments = [self.arg1, self.arg2]

        names = {self.arg1: '?a', self.arg2: '?b'}
        result = format_predicate(pred, names, no_color)

        assert result == '?a poss ?b'

    def test_amod_predicate(self):
        """Test formatting of adjectival modifier predicate."""
        pred = Predicate(self.token1, ud=dep_v1)
        pred.type = AMOD
        pred.tokens = [self.token1]
        pred.arguments = [self.arg1]
        pred.root.gov = None  # No governor for this test

        names = {self.arg1: '?a'}
        result = format_predicate(pred, names, no_color)

        assert result == '?a is/are likes'


class TestFormatPredicateInstance:
    """Test predicate instance formatting."""

    def setup_method(self):
        """Set up test data."""
        # Create tokens and predicate
        self.token = Token(1, "likes", "VERB", ud=dep_v1)  # Predicate in middle
        self.token.gov_rel = "root"
        self.arg_token1 = Token(0, "John", "NOUN", ud=dep_v1)  # Subject first
        self.arg_token2 = Token(2, "Mary", "NOUN", ud=dep_v1)  # Object last

        self.arg1 = Argument(self.arg_token1, ud=dep_v1)
        self.arg1.tokens = [self.arg_token1]
        self.arg1.position = 0
        self.arg1.rules = []

        self.arg2 = Argument(self.arg_token2, ud=dep_v1)
        self.arg2.tokens = [self.arg_token2]
        self.arg2.position = 2
        self.arg2.rules = []

        self.pred = Predicate(self.token, ud=dep_v1)
        self.pred.type = NORMAL
        self.pred.tokens = [self.token]
        self.pred.arguments = [self.arg1, self.arg2]
        self.pred.rules = []

    def test_basic_format(self):
        """Test basic formatting without rule tracking."""
        result = format_predicate_instance(self.pred, track_rule=False)
        expected = "\t?a likes ?b\n\t\t?a: John\n\t\t?b: Mary"
        assert result == expected

    def test_with_rule_tracking(self):
        """Test formatting with rule tracking."""
        self.pred.rules = ['rule1', 'rule2']
        self.arg1.rules = ['arg_rule1']

        result = format_predicate_instance(self.pred, track_rule=True)

        # Check that the output contains rule information
        assert '[likes-root,rule1,rule2]' in result
        assert '[John-None,arg_rule1]' in result
