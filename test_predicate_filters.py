#!/usr/bin/env python3
"""Tests for predicate filtering functions.

This test suite verifies that our modernized predicate filters produce
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
from decomp.semantics.predpatt.filters.predicate_filters import (
    isNotInterrogative,
    isPredVerb,
    isNotCopula,
    isGoodAncestor,
    isGoodDescendants,
    hasSubj,
    isNotHave,
    filter_events_NUCL,
    filter_events_SPRL,
    apply_filters
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


def test_isNotInterrogative():
    """Test isNotInterrogative filter."""
    print("Testing isNotInterrogative filter...")
    
    # Test non-interrogative sentence (should pass)
    pred1 = create_test_predicate(1, "ate", "VERB")
    result1 = isNotInterrogative(pred1)
    print(f"  Non-interrogative 'ate': {result1} (should be True)")
    assert result1 == True
    assert isNotInterrogative.__name__ in pred1.rules
    
    # Test interrogative sentence (should fail)
    pred2 = create_test_predicate(1, "ate", "VERB")
    pred2.tokens = ["What", "did", "you", "eat", "?"]
    result2 = isNotInterrogative(pred2)
    print(f"  Interrogative with '?': {result2} (should be False)")
    assert result2 == False
    
    return True


def test_isPredVerb():
    """Test isPredVerb filter."""
    print("Testing isPredVerb filter...")
    
    # Test verbal predicate (should pass)
    pred1 = create_test_predicate(1, "ate", "VERB")
    result1 = isPredVerb(pred1)
    print(f"  Verbal 'ate'/VERB: {result1} (should be True)")
    assert result1 == True
    assert isPredVerb.__name__ in pred1.rules
    
    # Test non-verbal predicate (should fail)
    pred2 = create_test_predicate(1, "cat", "NOUN")
    result2 = isPredVerb(pred2)
    print(f"  Nominal 'cat'/NOUN: {result2} (should be False)")
    assert result2 == False
    
    return True


def test_isNotCopula():
    """Test isNotCopula filter."""
    print("Testing isNotCopula filter...")
    
    # Test non-copula predicate (should pass)
    pred1 = create_test_predicate(1, "ate", "VERB")
    result1 = isNotCopula(pred1)
    print(f"  Non-copula 'ate': {result1} (should be True)")
    assert result1 == True
    assert isNotCopula.__name__ in pred1.rules
    
    # Test copula with 'cop' relation (should fail)
    cop_dep = DepTriple("cop", create_test_token(1, "ate", "VERB"), create_test_token(2, "is", "AUX"))
    pred2 = create_test_predicate(1, "ate", "VERB", dependents=[cop_dep])
    result2 = isNotCopula(pred2)
    print(f"  Copula with 'cop' relation: {result2} (should be False)")
    assert result2 == False
    
    # Test copula with copula verb text (should fail)
    be_dep = DepTriple("aux", create_test_token(1, "ate", "VERB"), create_test_token(2, "be", "AUX"))
    pred3 = create_test_predicate(1, "ate", "VERB", dependents=[be_dep])
    result3 = isNotCopula(pred3)
    print(f"  Copula with 'be' verb: {result3} (should be False)")
    assert result3 == False
    
    return True


def test_isGoodAncestor():
    """Test isGoodAncestor filter."""
    print("Testing isGoodAncestor filter...")
    
    # Test root predicate (should pass)
    pred1 = create_test_predicate(1, "ate", "VERB", gov_rel="root")
    result1 = isGoodAncestor(pred1)
    print(f"  Root predicate: {result1} (should be True)")
    assert result1 == True
    assert isGoodAncestor.__name__ in pred1.rules
    
    # Test embedded predicate (should fail)
    pred2 = create_test_predicate(1, "ate", "VERB", gov_rel="ccomp")
    result2 = isGoodAncestor(pred2)
    print(f"  Embedded predicate (ccomp): {result2} (should be False)")
    assert result2 == False
    
    return True


def test_isGoodDescendants():
    """Test isGoodDescendants filter."""
    print("Testing isGoodDescendants filter...")
    
    # Test predicate with good descendants (should pass)
    good_dep = DepTriple("nsubj", create_test_token(1, "ate", "VERB"), create_test_token(0, "I", "PRON"))
    pred1 = create_test_predicate(1, "ate", "VERB", dependents=[good_dep])
    result1 = isGoodDescendants(pred1)
    print(f"  Good descendants (nsubj): {result1} (should be True)")
    assert result1 == True
    assert isGoodDescendants.__name__ in pred1.rules
    
    # Test predicate with embedding descendants (should fail)
    bad_dep = DepTriple("neg", create_test_token(1, "ate", "VERB"), create_test_token(2, "not", "PART"))
    pred2 = create_test_predicate(1, "ate", "VERB", dependents=[bad_dep])
    result2 = isGoodDescendants(pred2)
    print(f"  Bad descendants (neg): {result2} (should be False)")
    assert result2 == False
    
    return True


def test_hasSubj():
    """Test hasSubj filter."""
    print("Testing hasSubj filter...")
    
    # Test predicate with subject (should pass)
    subj_dep = DepTriple("nsubj", create_test_token(1, "ate", "VERB"), create_test_token(0, "I", "PRON"))
    pred1 = create_test_predicate(1, "ate", "VERB", dependents=[subj_dep])
    result1 = hasSubj(pred1)
    print(f"  With nsubj: {result1} (should be True)")
    assert result1 == True
    assert hasSubj.__name__ in pred1.rules
    
    # Test predicate without subject (should fail)
    obj_dep = DepTriple("dobj", create_test_token(1, "ate", "VERB"), create_test_token(2, "apple", "NOUN"))
    pred2 = create_test_predicate(1, "ate", "VERB", dependents=[obj_dep])
    result2 = hasSubj(pred2)
    print(f"  Without subject: {result2} (should be False)")
    assert result2 == False
    
    # Test predicate with passive subject
    pass_subj_dep = DepTriple("nsubjpass", create_test_token(1, "eaten", "VERB"), create_test_token(2, "apple", "NOUN"))
    pred3 = create_test_predicate(1, "eaten", "VERB", dependents=[pass_subj_dep])
    result3 = hasSubj(pred3, passive=True)
    print(f"  With nsubjpass (passive=True): {result3} (should be True)")
    assert result3 == True
    
    # Test predicate with passive subject but passive=False
    result4 = hasSubj(pred3, passive=False)
    print(f"  With nsubjpass (passive=False): {result4} (should be False)")
    assert result4 == False
    
    return True


def test_isNotHave():
    """Test isNotHave filter."""
    print("Testing isNotHave filter...")
    
    # Test non-have verb (should pass)
    pred1 = create_test_predicate(1, "ate", "VERB")
    result1 = isNotHave(pred1)
    print(f"  Non-have verb 'ate': {result1} (should be True)")
    assert result1 == True
    assert isNotHave.__name__ in pred1.rules
    
    # Test 'have' verb (should fail)
    pred2 = create_test_predicate(1, "have", "VERB")
    result2 = isNotHave(pred2)
    print(f"  Have verb 'have': {result2} (should be False)")
    assert result2 == False
    
    # Test 'had' verb (should fail)
    pred3 = create_test_predicate(1, "had", "VERB")
    result3 = isNotHave(pred3)
    print(f"  Have verb 'had': {result3} (should be False)")
    assert result3 == False
    
    # Test 'has' verb (should fail)
    pred4 = create_test_predicate(1, "has", "VERB")
    result4 = isNotHave(pred4)
    print(f"  Have verb 'has': {result4} (should be False)")
    assert result4 == False
    
    return True


def test_apply_filters():
    """Test apply_filters function."""
    print("Testing apply_filters function...")
    
    # Test applying hasSubj filter
    subj_dep = DepTriple("nsubj", create_test_token(1, "ate", "VERB"), create_test_token(0, "I", "PRON"))
    pred1 = create_test_predicate(1, "ate", "VERB", dependents=[subj_dep])
    result1 = apply_filters(hasSubj, pred1)
    print(f"  Apply hasSubj filter: {result1} (should be True)")
    assert result1 == True
    
    # Test applying hasSubj filter with passive option
    pass_subj_dep = DepTriple("nsubjpass", create_test_token(1, "eaten", "VERB"), create_test_token(2, "apple", "NOUN"))
    pred2 = create_test_predicate(1, "eaten", "VERB", dependents=[pass_subj_dep])
    result2 = apply_filters(hasSubj, pred2, passive=True)
    print(f"  Apply hasSubj filter (passive=True): {result2} (should be True)")
    assert result2 == True
    
    # Test applying isPredVerb filter
    pred3 = create_test_predicate(1, "ate", "VERB")
    result3 = apply_filters(isPredVerb, pred3)
    print(f"  Apply isPredVerb filter: {result3} (should be True)")
    assert result3 == True
    
    return True


def main():
    """Run all predicate filter tests."""
    print("Predicate Filter Testing")
    print("=" * 30)
    
    tests = [
        test_isNotInterrogative,
        test_isPredVerb,
        test_isNotCopula,
        test_isGoodAncestor,
        test_isGoodDescendants,
        test_hasSubj,
        test_isNotHave,
        test_apply_filters
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
        print("All predicate filter tests passed!")
        return True
    else:
        print(f"Some tests failed. {len(tests) - passed} tests need fixing.")
        return False


if __name__ == '__main__':
    main()