"""
Differential testing harness for PredPatt modernization.

This test suite compares the output of the original PredPatt implementation
with our modernized version to ensure byte-for-byte identical output.

Per MODERNIZATION_PLAN.md: "If ANY test produces even ONE CHARACTER of different
output compared to original PredPatt, the implementation is WRONG and must be fixed."
"""

import pytest
import os
from io import StringIO

# Import both implementations for comparison
try:
    import predpatt as original_predpatt
    # Ensure util module is importable
    import sys
    import os
    predpatt_path = os.path.dirname(original_predpatt.__file__)
    util_path = os.path.join(predpatt_path, 'util')
    if os.path.exists(util_path) and util_path not in sys.path:
        sys.path.insert(0, predpatt_path)
    from predpatt.util.load import load_conllu as original_load_conllu
    from predpatt.util.load import load_comm as original_load_comm
    ORIGINAL_AVAILABLE = True
except ImportError as e:
    ORIGINAL_AVAILABLE = False
    print(f"Import error: {e}")
    pytest.skip("Original PredPatt not available for differential testing", allow_module_level=True)

from decomp.semantics.predpatt import PredPatt, PredPattOpts, load_conllu
from decomp.semantics.predpatt.util.load import load_comm


def compare_predpatt_output(sentence_text, ud_parse, opts_dict):
    """
    Compare output of original and modernized PredPatt implementations.
    
    Parameters
    ----------
    sentence_text : str
        The sentence text to process.
    ud_parse : object
        The parsed Universal Dependencies tree.
    opts_dict : dict
        Dictionary of options to pass to PredPattOpts.
        
    Returns
    -------
    tuple[bool, str, str]
        (outputs_match, original_output, modern_output)
    """
    # create options for both implementations
    original_opts = original_predpatt.PredPattOpts(**opts_dict)
    modern_opts = PredPattOpts(**opts_dict)
    
    # run original implementation
    original_pp = original_predpatt.PredPatt(ud_parse, opts=original_opts)
    original_output = original_pp.pprint(track_rule=True, color=False)
    
    # run modern implementation  
    modern_pp = PredPatt(ud_parse, opts=modern_opts)
    modern_output = modern_pp.pprint(track_rule=True, color=False)
    
    # compare outputs
    outputs_match = (original_output == modern_output)
    
    return outputs_match, original_output, modern_output


def find_first_difference(str1, str2):
    """Find the first character position where two strings differ."""
    for i, (c1, c2) in enumerate(zip(str1, str2)):
        if c1 != c2:
            return i, c1, c2
    # check if one string is longer
    if len(str1) != len(str2):
        return min(len(str1), len(str2)), None, None
    return -1, None, None


class TestDifferentialBasic:
    """Basic differential tests comparing individual sentences."""
    
    def test_simple_sentence(self):
        """Test a simple sentence."""
        conllu = """1	John	John	PROPN	NNP	_	2	nsubj	_	_
2	runs	run	VERB	VBZ	_	0	root	_	_
3	.	.	PUNCT	.	_	2	punct	_	_"""
        
        # parse with both implementations
        original_parse = list(original_load_conllu(conllu))[0][1]
        modern_parse = list(load_conllu(conllu))[0][1]
        
        opts = {'resolve_relcl': False, 'resolve_conj': False}
        match, orig, modern = compare_predpatt_output("John runs.", original_parse, opts)
        
        if not match:
            pos, c1, c2 = find_first_difference(orig, modern)
            pytest.fail(
                f"Output mismatch at position {pos}:\n"
                f"Original char: {repr(c1)}\n"
                f"Modern char: {repr(c2)}\n"
                f"Original output:\n{orig}\n"
                f"Modern output:\n{modern}"
            )
    
    def test_complex_sentence(self):
        """Test a more complex sentence with multiple predicates."""
        conllu = """1	The	the	DET	DT	_	2	det	_	_
2	cat	cat	NOUN	NN	_	3	nsubj	_	_
3	sat	sit	VERB	VBD	_	0	root	_	_
4	on	on	ADP	IN	_	6	case	_	_
5	the	the	DET	DT	_	6	det	_	_
6	mat	mat	NOUN	NN	_	3	nmod	_	_
7	and	and	CCONJ	CC	_	8	cc	_	_
8	slept	sleep	VERB	VBD	_	3	conj	_	_
9	.	.	PUNCT	.	_	3	punct	_	_"""
        
        original_parse = list(original_load_conllu(conllu))[0][1]
        modern_parse = list(load_conllu(conllu))[0][1]
        
        opts = {'resolve_relcl': True, 'resolve_conj': True}
        match, orig, modern = compare_predpatt_output(
            "The cat sat on the mat and slept.", original_parse, opts
        )
        
        assert match, f"Output mismatch:\nOriginal:\n{orig}\nModern:\n{modern}"
    
    def test_all_option_combinations(self):
        """Test various combinations of PredPattOpts."""
        conllu = """1	Mary	Mary	PROPN	NNP	_	2	nsubj	_	_
2	saw	see	VERB	VBD	_	0	root	_	_
3	John	John	PROPN	NNP	_	2	dobj	_	_
4	.	.	PUNCT	.	_	2	punct	_	_"""
        
        original_parse = list(original_load_conllu(conllu))[0][1]
        modern_parse = list(load_conllu(conllu))[0][1]
        
        # test different option combinations
        option_sets = [
            {'resolve_relcl': False, 'resolve_conj': False, 'cut': False},
            {'resolve_relcl': True, 'resolve_conj': False, 'cut': False},
            {'resolve_relcl': False, 'resolve_conj': True, 'cut': False},
            {'resolve_relcl': True, 'resolve_conj': True, 'cut': False},
            {'resolve_relcl': True, 'resolve_conj': True, 'cut': True},
            {'resolve_relcl': True, 'resolve_conj': True, 'simple': True},
        ]
        
        for opts in option_sets:
            match, orig, modern = compare_predpatt_output(
                "Mary saw John.", original_parse, opts
            )
            assert match, (
                f"Output mismatch with options {opts}:\n"
                f"Original:\n{orig}\nModern:\n{modern}"
            )


class TestDifferentialCorpus:
    """Test against the full PredPatt test corpus."""
    
    @pytest.mark.parametrize("test_file,options", [
        ("data.100.fine.all.ud.comm", {
            'resolve_poss': True,
            'resolve_relcl': True,
            'resolve_amod': True,
            'resolve_conj': True,
            'resolve_appos': True,
            'cut': False,
            'simple': False,
        }),
        ("data.100.fine.all.ud.comm", {
            'resolve_poss': True,
            'resolve_relcl': True,
            'resolve_amod': True,
            'resolve_conj': True,
            'resolve_appos': True,
            'cut': True,
            'simple': False,
        }),
    ])
    def test_corpus_sentences(self, test_file, options):
        """Test all sentences in the test corpus."""
        test_dir = os.path.dirname(__file__)
        test_path = os.path.join(test_dir, test_file)
        
        if not os.path.exists(test_path):
            pytest.skip(f"Test file {test_file} not found")
        
        # load sentences with both implementations
        original_sentences = list(original_load_comm(test_path))
        modern_sentences = list(load_comm(test_path))
        
        assert len(original_sentences) == len(modern_sentences), \
            f"Different number of sentences loaded: {len(original_sentences)} vs {len(modern_sentences)}"
        
        # test each sentence
        for i, ((orig_id, orig_parse), (mod_id, mod_parse)) in enumerate(
            zip(original_sentences, modern_sentences)
        ):
            assert orig_id == mod_id, f"Sentence ID mismatch at index {i}"
            
            # create PredPatt instances
            orig_opts = original_predpatt.PredPattOpts(**options)
            mod_opts = PredPattOpts(**options)
            
            orig_pp = original_predpatt.PredPatt(orig_parse, opts=orig_opts)
            mod_pp = PredPatt(mod_parse, opts=mod_opts)
            
            # compare string representations
            orig_str = orig_pp.pprint(track_rule=True, color=False)
            mod_str = mod_pp.pprint(track_rule=True, color=False)
            
            if orig_str != mod_str:
                pos, c1, c2 = find_first_difference(orig_str, mod_str)
                pytest.fail(
                    f"Sentence {i} ({orig_id}) output mismatch at position {pos}:\n"
                    f"Original char: {repr(c1)}\n"
                    f"Modern char: {repr(c2)}\n"
                    f"Original:\n{orig_str}\n"
                    f"Modern:\n{mod_str}"
                )


class TestDifferentialEdgeCases:
    """Test edge cases and quirky behaviors."""
    
    def test_empty_input(self):
        """Test empty input handling."""
        conllu = ""
        
        # both should handle empty input the same way
        try:
            original_result = list(original_load_conllu(conllu))
        except Exception as e:
            original_error = type(e).__name__
        else:
            original_error = None
            
        try:
            modern_result = list(load_conllu(conllu))
        except Exception as e:
            modern_error = type(e).__name__
        else:
            modern_error = None
            
        assert original_error == modern_error, \
            f"Different error handling for empty input: {original_error} vs {modern_error}"
    
    def test_mutable_default_behavior(self):
        """Test that mutable default argument behavior is preserved."""
        conllu = """1	test	test	VERB	VB	_	0	root	_	_"""
        
        original_parse = list(original_load_conllu(conllu))[0][1]
        modern_parse = list(load_conllu(conllu))[0][1]
        
        # create multiple PredPatt instances to test mutable default
        opts = {'resolve_relcl': False, 'resolve_conj': False}
        
        # original behavior
        orig_pp1 = original_predpatt.PredPatt(original_parse, opts=original_predpatt.PredPattOpts(**opts))
        orig_pp2 = original_predpatt.PredPatt(original_parse, opts=original_predpatt.PredPattOpts(**opts))
        
        # modern behavior
        mod_pp1 = PredPatt(modern_parse, opts=PredPattOpts(**opts))
        mod_pp2 = PredPatt(modern_parse, opts=PredPattOpts(**opts))
        
        # outputs should still match
        assert orig_pp1.pprint() == mod_pp1.pprint()
        assert orig_pp2.pprint() == mod_pp2.pprint()