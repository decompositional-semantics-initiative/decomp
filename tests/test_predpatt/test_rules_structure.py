"""Test the modernized rule structure to ensure it works correctly."""

from decomp.semantics.predpatt.parsing.udparse import DepTriple
from decomp.semantics.predpatt.rules import (
    ArgumentRootRule,
    PredicateRootRule,
    Rule,
    a1,
    a2,
    c,
    f,
    g1,
    w2,
)


class TestRuleStructure:
    """Test that the modernized rule structure works correctly."""

    def test_rule_inheritance(self):
        """Test that rules inherit from correct base classes."""
        # predicate root rules
        assert issubclass(a1, PredicateRootRule)
        assert issubclass(a1, Rule)
        assert issubclass(f, PredicateRootRule)

        # argument root rules
        assert issubclass(g1, ArgumentRootRule)
        assert issubclass(g1, Rule)
        assert issubclass(w2, ArgumentRootRule)

    def test_rule_instantiation(self):
        """Test that rules can be instantiated."""
        # simple rules
        rule_a1 = a1()
        assert isinstance(rule_a1, a1)
        assert isinstance(rule_a1, PredicateRootRule)
        assert isinstance(rule_a1, Rule)

        # rules with parameters
        edge = DepTriple(rel="nsubj", gov=1, dep=0)
        rule_c = c(edge)
        assert isinstance(rule_c, c)
        assert rule_c.e == edge

        rule_g1 = g1(edge)
        assert isinstance(rule_g1, g1)
        assert rule_g1.edge == edge

    def test_rule_name(self):
        """Test rule name method."""
        assert a1.name() == 'a1'
        assert g1.name() == 'g1'
        assert ArgumentRootRule.name() == 'ArgumentRootRule'

    def test_rule_repr(self):
        """Test rule string representation."""
        rule = a1()
        assert repr(rule) == 'a1'

        edge = DepTriple(rel="nsubj", gov=1, dep=0)
        rule_c = c(edge)
        assert 'add_root(1)_for_nsubj_from_(0)' in repr(rule_c)

        rule_g1 = g1(edge)
        assert 'g1(nsubj)' in repr(rule_g1)

    def test_rule_explain(self):
        """Test rule explanation."""
        explanation = a1.explain()
        assert 'clausal relation' in explanation
        assert 'ccomp' in explanation

        explanation = g1.explain()
        assert 'argument' in explanation
        assert 'nsubj' in explanation

    def test_rule_equality(self):
        """Test rule equality comparison."""
        rule1 = a1()
        rule2 = a1()
        rule3 = a2()

        assert rule1 == rule2
        assert rule1 != rule3
        assert rule1 != "not a rule"

    def test_rule_hash(self):
        """Test rules can be used in sets and dicts."""
        rule1 = a1()
        rule2 = a1()
        rule3 = a2()

        rule_set = {rule1, rule2, rule3}
        assert len(rule_set) == 2  # a1 and a2

        rule_dict = {rule1: "first", rule3: "third"}
        assert rule_dict[rule2] == "first"  # rule2 is same as rule1
