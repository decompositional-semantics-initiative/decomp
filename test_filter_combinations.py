#!/usr/bin/env python3
"""Tests for predicate filter combinations.

This test suite verifies that our filter combination functions work correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from decomp.semantics.predpatt.core.predicate import Predicate
from decomp.semantics.predpatt.core.token import Token
from decomp.semantics.predpatt.core.argument import Argument
from decomp.semantics.predpatt.parsing.udparse import DepTriple, UDParse
from decomp.semantics.predpatt.filters.predicate_filters import (
    filter_events_NUCL,
    filter_events_SPRL,
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


def create_test_predicate(position, text, tag, type_="normal", gov_rel="root", dependents=None):
    """Create a test predicate for filtering tests."""
    root = create_test_token(position, text, tag, gov_rel)
    if dependents:
        root.dependents = dependents
    pred = Predicate(root, dep_v1, [], type_=type_)
    pred.tokens = [text]  # Simple token list for interrogative check
    return pred


def create_test_parse(tokens, interrogative=False):
    """Create a simple test parse for filter combinations."""
    if interrogative:
        tokens = tokens + ["?"]
    parse = UDParse(tokens, ["VERB"] * len(tokens), [], dep_v1)
    return parse


def test_good_predicate():
    """Test predicate that should pass all filters."""
    print("Testing good predicate (should pass NUCL and SPRL)...")
    
    # Create a good verbal predicate with subject
    subj_dep = DepTriple("nsubj", create_test_token(1, "ate", "VERB"), create_test_token(0, "I", "PRON"))
    pred = create_test_predicate(1, "ate", "VERB", gov_rel="root", dependents=[subj_dep])
    parse = create_test_parse(["I", "ate", "apples"])
    
    # Test NUCL filter
    result_nucl = filter_events_NUCL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be True)")
    
    # Test SPRL filter  
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  SPRL filter: {result_sprl} (should be True)")
    
    return result_nucl and result_sprl


def test_interrogative_predicate():
    """Test interrogative predicate (should be filtered out)."""
    print("Testing interrogative predicate (should fail)...")
    
    subj_dep = DepTriple("nsubj", create_test_token(1, "ate", "VERB"), create_test_token(0, "you", "PRON"))
    pred = create_test_predicate(1, "ate", "VERB", gov_rel="root", dependents=[subj_dep])
    parse = create_test_parse(["What", "did", "you", "eat"], interrogative=True)
    
    # Both filters should return None/False for interrogative
    result_nucl = filter_events_NUCL(pred, parse)
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be None/False)")
    print(f"  SPRL filter: {result_sprl} (should be None/False)")
    
    return result_nucl is None and result_sprl is None


def test_non_verbal_predicate():
    """Test non-verbal predicate (should fail verb filters)."""
    print("Testing non-verbal predicate (should fail)...")
    
    subj_dep = DepTriple("nsubj", create_test_token(1, "cat", "NOUN"), create_test_token(0, "the", "DET"))
    pred = create_test_predicate(1, "cat", "NOUN", gov_rel="root", dependents=[subj_dep])
    parse = create_test_parse(["The", "cat", "is", "big"])
    
    # Should fail because it's not a verb
    result_nucl = filter_events_NUCL(pred, parse)
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be False)")
    print(f"  SPRL filter: {result_sprl} (should be False)")
    
    return result_nucl == False and result_sprl == False


def test_copula_predicate():
    """Test copula predicate (should fail NUCL but pass SPRL)."""
    print("Testing copula predicate (NUCL rejects, SPRL accepts)...")
    
    # Create predicate with copula dependent
    cop_dep = DepTriple("cop", create_test_token(1, "tall", "ADJ"), create_test_token(2, "is", "AUX"))
    subj_dep = DepTriple("nsubj", create_test_token(1, "tall", "ADJ"), create_test_token(0, "John", "PROPN"))
    pred = create_test_predicate(1, "tall", "VERB", gov_rel="root", dependents=[cop_dep, subj_dep])
    parse = create_test_parse(["John", "is", "tall"])
    
    # NUCL fails because it has copula, SPRL passes because it doesn't check copula
    result_nucl = filter_events_NUCL(pred, parse)
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be False)")
    print(f"  SPRL filter: {result_sprl} (should be True)")
    
    return result_nucl == False and result_sprl == True


def test_have_predicate():
    """Test 'have' predicate (should fail NUCL but not SPRL)."""
    print("Testing 'have' predicate (NUCL rejects, SPRL may accept)...")
    
    subj_dep = DepTriple("nsubj", create_test_token(1, "have", "VERB"), create_test_token(0, "I", "PRON"))
    pred = create_test_predicate(1, "have", "VERB", gov_rel="root", dependents=[subj_dep])
    parse = create_test_parse(["I", "have", "a", "cat"])
    
    # NUCL rejects 'have' verbs, SPRL doesn't have that filter
    result_nucl = filter_events_NUCL(pred, parse)
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be False)")
    print(f"  SPRL filter: {result_sprl} (should be True)")
    
    return result_nucl == False and result_sprl == True


def test_embedded_predicate():
    """Test embedded predicate (should fail ancestor filter)."""
    print("Testing embedded predicate (should fail ancestor filter)...")
    
    subj_dep = DepTriple("nsubj", create_test_token(1, "eat", "VERB"), create_test_token(2, "I", "PRON"))
    pred = create_test_predicate(1, "eat", "VERB", gov_rel="ccomp", dependents=[subj_dep])
    parse = create_test_parse(["I", "think", "I", "eat", "apples"])
    
    # Should fail because it's embedded (ccomp relation)
    result_nucl = filter_events_NUCL(pred, parse)
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be False)")
    print(f"  SPRL filter: {result_sprl} (should be False)")
    
    return result_nucl == False and result_sprl == False


def test_no_subject_predicate():
    """Test predicate without subject (should fail hasSubj filter)."""
    print("Testing predicate without subject (should fail)...")
    
    obj_dep = DepTriple("dobj", create_test_token(1, "eat", "VERB"), create_test_token(2, "apples", "NOUN"))
    pred = create_test_predicate(1, "eat", "VERB", gov_rel="root", dependents=[obj_dep])
    parse = create_test_parse(["Eat", "apples"])  # Imperative without explicit subject
    
    # Should fail because it has no subject
    result_nucl = filter_events_NUCL(pred, parse)
    result_sprl = filter_events_SPRL(pred, parse)
    print(f"  NUCL filter: {result_nucl} (should be False)")
    print(f"  SPRL filter: {result_sprl} (should be False)")
    
    return result_nucl == False and result_sprl == False


def test_activate_function():
    """Test the activate function that applies all filters."""
    print("Testing activate function...")
    
    # Create a predicate with arguments
    subj_dep = DepTriple("nsubj", create_test_token(1, "ate", "VERB"), create_test_token(0, "I", "PRON"))
    obj_dep = DepTriple("dobj", create_test_token(1, "ate", "VERB"), create_test_token(2, "apple", "NOUN"))
    pred = create_test_predicate(1, "ate", "VERB", gov_rel="root", dependents=[subj_dep, obj_dep])
    
    # Add some arguments
    subj_arg = Argument(create_test_token(0, "I", "PRON", "nsubj"), dep_v1)
    obj_arg = Argument(create_test_token(2, "apple", "NOUN", "dobj"), dep_v1)
    pred.arguments = [subj_arg, obj_arg]
    
    # Apply activate function
    activate(pred)
    
    # Check that rules were added
    pred_has_rules = len(pred.rules) > 0
    args_have_rules = all(len(arg.rules) > 0 for arg in pred.arguments)
    
    print(f"  Predicate has filter rules: {pred_has_rules}")
    print(f"  Arguments have filter rules: {args_have_rules}")
    print(f"  Predicate rules: {pred.rules}")
    print(f"  Argument 0 rules: {pred.arguments[0].rules}")
    print(f"  Argument 1 rules: {pred.arguments[1].rules}")
    
    return pred_has_rules and args_have_rules


def main():
    """Run all filter combination tests."""
    print("Filter Combination Testing")
    print("=" * 35)
    
    tests = [
        test_good_predicate,
        test_interrogative_predicate,
        test_non_verbal_predicate,
        test_copula_predicate,
        test_have_predicate,
        test_embedded_predicate,
        test_no_subject_predicate,
        test_activate_function
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
    
    print("=" * 35)
    print(f"Passed {passed}/{len(tests)} tests")
    
    if passed == len(tests):
        print("All filter combination tests passed!")
        return True
    else:
        print(f"Some tests failed. {len(tests) - passed} tests need fixing.")
        return False


if __name__ == '__main__':
    main()