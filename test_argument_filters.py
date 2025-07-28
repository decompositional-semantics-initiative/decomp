#!/usr/bin/env python3
"""Tests for argument filtering functions.

This test suite verifies that our modernized argument filters produce
exactly the same results as the original implementation.
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
from decomp.semantics.predpatt.filters.argument_filters import (
    isSbjOrObj,
    isNotPronoun,
    has_direct_arc
)
from decomp.semantics.predpatt.util.ud import dep_v1


def create_test_token(position, text, tag, gov_rel="root", gov=None):
    """Create a test token for filtering tests."""
    token = Token(position, text, tag, dep_v1)
    token.gov_rel = gov_rel
    token.gov = gov
    token.dependents = []
    return token


def create_test_argument(position, text, tag, gov_rel="nsubj"):
    """Create a test argument for filtering tests."""
    root = create_test_token(position, text, tag, gov_rel)
    arg = Argument(root, dep_v1, [])
    return arg


def create_test_predicate(position, text, tag):
    """Create a test predicate for filtering tests."""
    root = create_test_token(position, text, tag)
    pred = Predicate(root, dep_v1, [])
    return pred


def test_isSbjOrObj():
    """Test isSbjOrObj filter."""
    print("Testing isSbjOrObj filter...")
    
    # Test subject argument (should pass)
    arg1 = create_test_argument(0, "I", "PRON", "nsubj")
    result1 = isSbjOrObj(arg1)
    print(f"  Subject 'I'/nsubj: {result1} (should be True)")
    assert result1 == True
    assert isSbjOrObj.__name__ in arg1.rules
    
    # Test direct object argument (should pass)
    arg2 = create_test_argument(2, "apple", "NOUN", "dobj")
    result2 = isSbjOrObj(arg2)
    print(f"  Direct object 'apple'/dobj: {result2} (should be True)")
    assert result2 == True
    assert isSbjOrObj.__name__ in arg2.rules
    
    # Test indirect object argument (should pass)
    arg3 = create_test_argument(1, "him", "PRON", "iobj")
    result3 = isSbjOrObj(arg3)
    print(f"  Indirect object 'him'/iobj: {result3} (should be True)")
    assert result3 == True
    assert isSbjOrObj.__name__ in arg3.rules
    
    # Test non-core argument (should fail)
    arg4 = create_test_argument(3, "quickly", "ADV", "advmod")
    result4 = isSbjOrObj(arg4)
    print(f"  Adverbial 'quickly'/advmod: {result4} (should be False)")
    assert result4 == False
    
    # Test nominal modifier (should fail)
    arg5 = create_test_argument(2, "table", "NOUN", "nmod")
    result5 = isSbjOrObj(arg5)
    print(f"  Nominal modifier 'table'/nmod: {result5} (should be False)")
    assert result5 == False
    
    return True


def test_isNotPronoun():
    """Test isNotPronoun filter."""
    print("Testing isNotPronoun filter...")
    
    # Test regular noun (should pass)
    arg1 = create_test_argument(2, "apple", "NOUN", "dobj")
    result1 = isNotPronoun(arg1)
    print(f"  Noun 'apple'/NOUN: {result1} (should be True)")
    assert result1 == True
    assert isNotPronoun.__name__ in arg1.rules
    
    # Test proper noun (should pass)
    arg2 = create_test_argument(0, "John", "PROPN", "nsubj")
    result2 = isNotPronoun(arg2)
    print(f"  Proper noun 'John'/PROPN: {result2} (should be True)")
    assert result2 == True
    assert isNotPronoun.__name__ in arg2.rules
    
    # Test regular word not in pronoun list (should pass)
    arg3 = create_test_argument(1, "book", "NOUN", "dobj")
    result3 = isNotPronoun(arg3)
    print(f"  Regular word 'book': {result3} (should be True)")
    assert result3 == True
    
    # Test personal pronoun with PRP tag (should fail)
    arg4 = create_test_argument(0, "I", "PRP", "nsubj")
    result4 = isNotPronoun(arg4)
    print(f"  Personal pronoun 'I'/PRP: {result4} (should be False)")
    assert result4 == False
    
    # Test 'that' (should fail)
    arg5 = create_test_argument(2, "that", "PRON", "dobj")
    result5 = isNotPronoun(arg5)
    print(f"  Demonstrative 'that': {result5} (should be False)")
    assert result5 == False
    
    # Test 'this' (should fail)
    arg6 = create_test_argument(2, "this", "PRON", "dobj")
    result6 = isNotPronoun(arg6)
    print(f"  Demonstrative 'this': {result6} (should be False)")
    assert result6 == False
    
    # Test 'which' (should fail)
    arg7 = create_test_argument(2, "which", "PRON", "dobj")
    result7 = isNotPronoun(arg7)
    print(f"  Interrogative 'which': {result7} (should be False)")
    assert result7 == False
    
    # Test 'what' (should fail)
    arg8 = create_test_argument(2, "what", "PRON", "dobj")
    result8 = isNotPronoun(arg8)
    print(f"  Interrogative 'what': {result8} (should be False)")
    assert result8 == False
    
    # Test case insensitive (should fail)
    arg9 = create_test_argument(2, "THAT", "PRON", "dobj")
    result9 = isNotPronoun(arg9)
    print(f"  Uppercase 'THAT': {result9} (should be False)")
    assert result9 == False
    
    return True


def test_has_direct_arc():
    """Test has_direct_arc filter."""
    print("Testing has_direct_arc filter...")
    
    # Create predicate and argument tokens
    pred_token = create_test_token(1, "ate", "VERB")
    arg_token = create_test_token(0, "I", "PRON", "nsubj", pred_token)
    
    # Create predicate and argument objects
    pred = Predicate(pred_token, dep_v1, [])
    arg = Argument(arg_token, dep_v1, [])
    
    # Test direct arc (should pass)
    result1 = has_direct_arc(pred, arg)
    print(f"  Direct arc (arg.gov == pred.root): {result1} (should be True)")
    assert result1 == True
    assert has_direct_arc.__name__ in arg.rules
    
    # Test indirect arc (should fail)
    other_token = create_test_token(2, "quickly", "ADV")
    arg2_token = create_test_token(3, "apple", "NOUN", "dobj", other_token)
    arg2 = Argument(arg2_token, dep_v1, [])
    
    result2 = has_direct_arc(pred, arg2)
    print(f"  Indirect arc (arg.gov != pred.root): {result2} (should be False)")
    assert result2 == False
    
    # Test no governor (should fail)
    arg3_token = create_test_token(4, "orphan", "NOUN", "nsubj", None)
    arg3 = Argument(arg3_token, dep_v1, [])
    
    result3 = has_direct_arc(pred, arg3)
    print(f"  No governor (arg.gov == None): {result3} (should be False)")
    assert result3 == False
    
    return True


def test_filter_combinations():
    """Test combinations of argument filters."""
    print("Testing argument filter combinations...")
    
    # Create predicate
    pred = create_test_predicate(1, "gave", "VERB")
    
    # Test argument that passes all filters
    arg1 = create_test_argument(2, "book", "NOUN", "dobj")
    arg1.root.gov = pred.root  # Set up direct arc
    
    passes_core = isSbjOrObj(arg1)
    passes_pronoun = isNotPronoun(arg1)
    passes_direct = has_direct_arc(pred, arg1)
    
    print(f"  Good argument 'book'/dobj:")
    print(f"    isSbjOrObj: {passes_core}")
    print(f"    isNotPronoun: {passes_pronoun}")
    print(f"    has_direct_arc: {passes_direct}")
    print(f"    All pass: {passes_core and passes_pronoun and passes_direct}")
    
    assert passes_core and passes_pronoun and passes_direct
    
    # Test pronoun subject (fails pronoun filter)
    arg2 = create_test_argument(0, "I", "PRP", "nsubj")
    arg2.root.gov = pred.root
    
    passes_core2 = isSbjOrObj(arg2)
    passes_pronoun2 = isNotPronoun(arg2)
    passes_direct2 = has_direct_arc(pred, arg2)
    
    print(f"  Pronoun subject 'I'/PRP/nsubj:")
    print(f"    isSbjOrObj: {passes_core2}")
    print(f"    isNotPronoun: {passes_pronoun2}")
    print(f"    has_direct_arc: {passes_direct2}")
    print(f"    All pass: {passes_core2 and passes_pronoun2 and passes_direct2}")
    
    assert passes_core2 and not passes_pronoun2 and passes_direct2
    assert not (passes_core2 and passes_pronoun2 and passes_direct2)
    
    # Test adverbial modifier (fails core and direct arc)
    arg3 = create_test_argument(3, "quickly", "ADV", "advmod")
    # Don't set direct arc
    
    passes_core3 = isSbjOrObj(arg3)
    passes_pronoun3 = isNotPronoun(arg3)
    passes_direct3 = has_direct_arc(pred, arg3)
    
    print(f"  Adverbial 'quickly'/advmod:")
    print(f"    isSbjOrObj: {passes_core3}")
    print(f"    isNotPronoun: {passes_pronoun3}")
    print(f"    has_direct_arc: {passes_direct3}")
    print(f"    All pass: {passes_core3 and passes_pronoun3 and passes_direct3}")
    
    assert not passes_core3 and passes_pronoun3 and not passes_direct3
    assert not (passes_core3 and passes_pronoun3 and passes_direct3)
    
    return True


def test_filter_order():
    """Test that filter order doesn't matter for individual results."""
    print("Testing filter order independence...")
    
    pred = create_test_predicate(1, "saw", "VERB")
    arg = create_test_argument(2, "book", "NOUN", "dobj")
    arg.root.gov = pred.root
    
    # Apply filters in different orders
    arg1 = create_test_argument(2, "book", "NOUN", "dobj")
    arg1.root.gov = pred.root
    
    # Order 1: core -> pronoun -> direct
    result1_core = isSbjOrObj(arg1)
    result1_pronoun = isNotPronoun(arg1)
    result1_direct = has_direct_arc(pred, arg1)
    
    arg2 = create_test_argument(2, "book", "NOUN", "dobj")
    arg2.root.gov = pred.root
    
    # Order 2: direct -> core -> pronoun
    result2_direct = has_direct_arc(pred, arg2)
    result2_core = isSbjOrObj(arg2)
    result2_pronoun = isNotPronoun(arg2)
    
    arg3 = create_test_argument(2, "book", "NOUN", "dobj")
    arg3.root.gov = pred.root
    
    # Order 3: pronoun -> direct -> core
    result3_pronoun = isNotPronoun(arg3)
    result3_direct = has_direct_arc(pred, arg3)
    result3_core = isSbjOrObj(arg3)
    
    print(f"  Order 1 results: {result1_core}, {result1_pronoun}, {result1_direct}")
    print(f"  Order 2 results: {result2_direct}, {result2_core}, {result2_pronoun}")
    print(f"  Order 3 results: {result3_pronoun}, {result3_direct}, {result3_core}")
    
    # All orders should give same individual results
    assert result1_core == result2_core == result3_core
    assert result1_pronoun == result2_pronoun == result3_pronoun
    assert result1_direct == result2_direct == result3_direct
    
    print("  Filter order independence verified!")
    return True


def test_argument_types():
    """Test filters with various argument types."""
    print("Testing various argument types...")
    
    pred = create_test_predicate(1, "gave", "VERB")
    
    test_cases = [
        # (text, tag, gov_rel, expected_core, expected_pronoun, description)
        ("John", "PROPN", "nsubj", True, True, "proper noun subject"),
        ("he", "PRP", "nsubj", True, False, "pronoun subject"),
        ("book", "NOUN", "dobj", True, True, "noun direct object"),
        ("it", "PRP", "dobj", True, False, "pronoun direct object"),
        ("her", "PRP", "iobj", True, False, "pronoun indirect object"),
        ("teacher", "NOUN", "iobj", True, True, "noun indirect object"),
        ("table", "NOUN", "nmod", False, True, "nominal modifier"),
        ("that", "PRON", "dobj", True, False, "demonstrative pronoun object"),
        ("which", "PRON", "dobj", True, False, "interrogative pronoun object"),
        ("quickly", "ADV", "advmod", False, True, "adverb modifier"),
        ("yesterday", "NOUN", "nmod:tmod", False, True, "temporal modifier"),
    ]
    
    for i, (text, tag, gov_rel, expected_core, expected_pronoun, description) in enumerate(test_cases):
        arg = create_test_argument(i + 2, text, tag, gov_rel)
        arg.root.gov = pred.root  # Set up direct arc
        
        result_core = isSbjOrObj(arg)
        result_pronoun = isNotPronoun(arg)
        result_direct = has_direct_arc(pred, arg)
        
        print(f"  {description}: core={result_core}, pronoun={result_pronoun}, direct={result_direct}")
        
        assert result_core == expected_core, f"Core filter failed for {description}"
        assert result_pronoun == expected_pronoun, f"Pronoun filter failed for {description}"
        assert result_direct == True, f"Direct arc failed for {description}"  # All should have direct arc
    
    return True


def main():
    """Run all argument filter tests."""
    print("Argument Filter Testing")
    print("=" * 30)
    
    tests = [
        test_isSbjOrObj,
        test_isNotPronoun,
        test_has_direct_arc,
        test_filter_combinations,
        test_filter_order,
        test_argument_types
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
        print("All argument filter tests passed!")
        return True
    else:
        print(f"Some tests failed. {len(tests) - passed} tests need fixing.")
        return False


if __name__ == '__main__':
    main()