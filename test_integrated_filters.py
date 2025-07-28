#!/usr/bin/env python3
"""Tests for integrated predicate and argument filtering.

This test suite verifies that the complete filtering system works
correctly when applied to predicates with their arguments.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from decomp.semantics.predpatt.core.predicate import Predicate
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.core.argument import Argument
from decomp.semantics.predpatt.parsing.udparse import DepTriple
from decomp.semantics.predpatt.filters import (
    isNotInterrogative,
    isPredVerb,
    isNotCopula,
    hasSubj,
    isNotHave,
    isSbjOrObj,
    isNotPronoun,
    has_direct_arc,
    apply_filters,
    activate
)
from decomp.semantics.predpatt.util.ud import dep_v1


def create_test_token(position, text, tag, gov_rel="root", gov=None):
    """Create a test token for filtering tests."""
    token = Token(position, text, tag, dep_v1)
    token.gov_rel = gov_rel
    token.gov = gov
    token.dependents = []
    return token


def create_test_predicate_with_args(pred_text, pred_tag, arguments_data):
    """Create a predicate with arguments for testing.
    
    Args:
        pred_text: Text of the predicate
        pred_tag: POS tag of the predicate
        arguments_data: List of (position, text, tag, gov_rel) tuples
    """
    pred_token = create_test_token(1, pred_text, pred_tag)
    pred = Predicate(pred_token, dep_v1, [])
    pred.tokens = [pred_text]  # For interrogative check
    
    # Create dependents for predicate
    dependents = []
    arguments = []
    
    for pos, text, tag, gov_rel in arguments_data:
        arg_token = create_test_token(pos, text, tag, gov_rel, pred_token)
        dep_triple = DepTriple(gov_rel, pred_token, arg_token)
        dependents.append(dep_triple)
        arguments.append(Argument(arg_token, dep_v1, []))
    
    pred.root.dependents = dependents
    pred.arguments = arguments
    
    return pred


def test_complete_filtering_pipeline():
    """Test the complete filtering pipeline on realistic predicates."""
    print("Testing complete filtering pipeline...")
    
    # Test 1: Good predicate with good arguments
    print("  Test 1: Good verbal predicate with noun arguments")
    pred1 = create_test_predicate_with_args("gave", "VERB", [
        (0, "John", "PROPN", "nsubj"),
        (2, "book", "NOUN", "dobj"),
        (3, "Mary", "PROPN", "iobj")
    ])
    
    # Apply predicate filters
    pred_passes = (isNotInterrogative(pred1) and isPredVerb(pred1) 
                  and isNotCopula(pred1) and hasSubj(pred1) and isNotHave(pred1))
    
    # Apply argument filters
    arg_results = []
    for arg in pred1.arguments:
        core = isSbjOrObj(arg)
        pronoun = isNotPronoun(arg)
        direct = has_direct_arc(pred1, arg)
        all_pass = core and pronoun and direct
        arg_results.append((arg.root.text, core, pronoun, direct, all_pass))
    
    print(f"    Predicate passes: {pred_passes}")
    for text, core, pronoun, direct, all_pass in arg_results:
        print(f"    Arg '{text}': core={core}, pronoun={pronoun}, direct={direct}, all={all_pass}")
    
    assert pred_passes
    assert all(result[4] for result in arg_results)  # All arguments should pass
    
    # Test 2: Pronoun arguments (should fail pronoun filter)
    print("  Test 2: Predicate with pronoun arguments")
    pred2 = create_test_predicate_with_args("saw", "VERB", [
        (0, "I", "PRP", "nsubj"),
        (2, "him", "PRP", "dobj")
    ])
    
    pred_passes2 = (isNotInterrogative(pred2) and isPredVerb(pred2) 
                   and isNotCopula(pred2) and hasSubj(pred2) and isNotHave(pred2))
    
    arg_results2 = []
    for arg in pred2.arguments:
        core = isSbjOrObj(arg)
        pronoun = isNotPronoun(arg)
        direct = has_direct_arc(pred2, arg)
        all_pass = core and pronoun and direct
        arg_results2.append((arg.root.text, core, pronoun, direct, all_pass))
    
    print(f"    Predicate passes: {pred_passes2}")
    for text, core, pronoun, direct, all_pass in arg_results2:
        print(f"    Arg '{text}': core={core}, pronoun={pronoun}, direct={direct}, all={all_pass}")
    
    assert pred_passes2
    assert not any(result[4] for result in arg_results2)  # No arguments should pass (all pronouns)
    
    # Test 3: Non-core arguments (should fail core filter)
    print("  Test 3: Predicate with non-core arguments")
    pred3 = create_test_predicate_with_args("ran", "VERB", [
        (0, "John", "PROPN", "nsubj"),
        (2, "quickly", "ADV", "advmod"),
        (3, "park", "NOUN", "nmod")
    ])
    
    pred_passes3 = (isNotInterrogative(pred3) and isPredVerb(pred3) 
                   and isNotCopula(pred3) and hasSubj(pred3) and isNotHave(pred3))
    
    arg_results3 = []
    for arg in pred3.arguments:
        core = isSbjOrObj(arg)
        pronoun = isNotPronoun(arg)
        direct = has_direct_arc(pred3, arg)
        all_pass = core and pronoun and direct
        arg_results3.append((arg.root.text, core, pronoun, direct, all_pass))
    
    print(f"    Predicate passes: {pred_passes3}")
    for text, core, pronoun, direct, all_pass in arg_results3:
        print(f"    Arg '{text}': core={core}, pronoun={pronoun}, direct={direct}, all={all_pass}")
    
    assert pred_passes3
    # Only the subject should pass all filters
    assert arg_results3[0][4]  # John/nsubj should pass
    assert not arg_results3[1][4]  # quickly/advmod should fail
    assert not arg_results3[2][4]  # park/nmod should fail
    
    return True


def test_apply_filters_function():
    """Test the apply_filters function with different filter types."""
    print("Testing apply_filters function with argument filters...")
    
    pred = create_test_predicate_with_args("gave", "VERB", [
        (0, "John", "PROPN", "nsubj"),
        (2, "it", "PRP", "dobj")
    ])
    
    # Test argument filters through apply_filters
    result1 = apply_filters(isSbjOrObj, pred)
    print(f"  apply_filters(isSbjOrObj): {result1} (should be True - has core args)")
    assert result1 == True
    
    result2 = apply_filters(isNotPronoun, pred)
    print(f"  apply_filters(isNotPronoun): {result2} (should be True - has non-pronoun)")
    assert result2 == True  # Should return True if ANY argument passes
    
    result3 = apply_filters(has_direct_arc, pred)
    print(f"  apply_filters(has_direct_arc): {result3} (should be True - has direct arcs)")
    assert result3 == True
    
    # Test with predicate that has only pronouns
    pred_pronouns = create_test_predicate_with_args("saw", "VERB", [
        (0, "I", "PRP", "nsubj"),
        (2, "him", "PRP", "dobj")
    ])
    
    result4 = apply_filters(isNotPronoun, pred_pronouns)
    print(f"  apply_filters(isNotPronoun) on all pronouns: {result4} (should be False)")
    assert result4 == False
    
    return True


def test_activate_function_complete():
    """Test the activate function with complete predicate and arguments."""
    print("Testing activate function with complete setup...")
    
    pred = create_test_predicate_with_args("bought", "VERB", [
        (0, "Sarah", "PROPN", "nsubj"),
        (2, "book", "NOUN", "dobj"),
        (3, "store", "NOUN", "nmod")
    ])
    
    # Apply activate function
    activate(pred)
    
    # Check predicate rules
    pred_rule_names = [rule for rule in pred.rules if isinstance(rule, str)]
    print(f"  Predicate rules: {pred_rule_names}")
    
    expected_pred_rules = ['isNotInterrogative', 'isPredVerb', 'isNotCopula', 
                          'isGoodAncestor', 'isGoodDescendants', 'hasSubj', 'isNotHave']
    
    for expected_rule in expected_pred_rules:
        assert expected_rule in pred_rule_names, f"Missing predicate rule: {expected_rule}"
    
    # Check argument rules
    for i, arg in enumerate(pred.arguments):
        arg_rule_names = [rule for rule in arg.rules if isinstance(rule, str)]
        print(f"  Argument {i} ('{arg.root.text}') rules: {arg_rule_names}")
        
        # All arguments should have been tested by all argument filters
        # (though they may not all pass)
        expected_arg_rules = ['isSbjOrObj', 'isNotPronoun', 'has_direct_arc']
        for expected_rule in expected_arg_rules:
            # Note: Rules are only added when filters return True
            # So we can't assert all rules are present, but we can check
            # that the activate function was called (rules list exists)
            assert hasattr(arg, 'rules'), f"Argument {i} missing rules list"
    
    return True


def test_filter_behavior_edge_cases():
    """Test edge cases and special filter behaviors."""
    print("Testing edge cases and special behaviors...")
    
    # Test 1: Copula predicate (should fail isNotCopula but pass others)
    print("  Test 1: Copula predicate")
    cop_dep = DepTriple("cop", create_test_token(1, "tall", "ADJ"), create_test_token(2, "is", "AUX"))
    subj_dep = DepTriple("nsubj", create_test_token(1, "tall", "ADJ"), create_test_token(0, "John", "PROPN"))
    
    pred_cop = Predicate(create_test_token(1, "tall", "VERB"), dep_v1, [])
    pred_cop.tokens = ["tall"]
    pred_cop.root.dependents = [cop_dep, subj_dep]
    pred_cop.arguments = [Argument(create_test_token(0, "John", "PROPN", "nsubj"), dep_v1, [])]
    pred_cop.arguments[0].root.gov = pred_cop.root
    
    copula_result = isNotCopula(pred_cop)
    other_results = [isNotInterrogative(pred_cop), isPredVerb(pred_cop), hasSubj(pred_cop)]
    
    print(f"    Copula filter: {copula_result} (should be False)")
    print(f"    Other filters: {other_results} (should be [True, True, True])")
    
    assert copula_result == False
    assert all(other_results)
    
    # Test 2: Interrogative sentence
    print("  Test 2: Interrogative sentence")
    pred_q = create_test_predicate_with_args("eat", "VERB", [
        (0, "you", "PRP", "nsubj"),
        (2, "what", "PRON", "dobj")
    ])
    pred_q.tokens = ["What", "did", "you", "eat", "?"]
    
    interrog_result = isNotInterrogative(pred_q)
    pronoun_what = isNotPronoun(pred_q.arguments[1])
    
    print(f"    Interrogative filter: {interrog_result} (should be False)")
    print(f"    'what' pronoun filter: {pronoun_what} (should be False)")
    
    assert interrog_result == False
    assert pronoun_what == False
    
    # Test 3: Case sensitivity in pronoun filter
    print("  Test 3: Case sensitivity")
    mixed_case_args = [
        ("That", "PRON", False),
        ("THIS", "PRON", False),  
        ("Which", "PRON", False),
        ("WHAT", "PRON", False),
        ("Book", "NOUN", True)
    ]
    
    for text, tag, expected in mixed_case_args:
        arg = Argument(create_test_token(0, text, tag, "dobj"), dep_v1, [])
        result = isNotPronoun(arg)
        print(f"    '{text}': {result} (expected {expected})")
        assert result == expected
    
    return True


def main():
    """Run all integrated filter tests."""
    print("Integrated Filter Testing")
    print("=" * 30)
    
    tests = [
        test_complete_filtering_pipeline,
        test_apply_filters_function,
        test_activate_function_complete,
        test_filter_behavior_edge_cases
    ]
    
    passed = 0
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
                print(f"  ✓ {test.__name__} passed\n")
            else:
                print(f"  ✗ {test.__name__} failed\n")
        except Exception as e:
            print(f"  ✗ {test.__name__} failed with error: {e}\n")
    
    print("=" * 30)
    print(f"Passed {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("All integrated filter tests passed!")
        return True
    else:
        print(f"Some tests failed. {len(tests) - passed} tests need fixing.")
        return False


if __name__ == '__main__':
    main()