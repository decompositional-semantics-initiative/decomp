#!/usr/bin/env python3
"""Compare outputs between external PredPatt with this package's PredPatt."""


# Import both implementations for comparison
import predpatt as original_predpatt
from predpatt import PredPatt as OriginalPredPatt
from predpatt import PredPattOpts as OriginalPredPattOpts
from predpatt.util.load import load_conllu as original_load_conllu

# Modernized imports
from decomp.semantics.predpatt.core.options import PredPattOpts as ModernPredPattOpts
from decomp.semantics.predpatt.extraction.engine import PredPattEngine as ModernPredPatt
from decomp.semantics.predpatt.parsing.loader import load_conllu as modern_load_conllu


def test_comparison():
    """Compare external and modernized implementations to ensure identical behavior."""

    # Test data
    test_conllu = """1	The	the	DET	DT	_	2	det	_	_
2	cat	cat	NOUN	NN	_	3	nsubj	_	_
3	chased	chase	VERB	VBD	_	0	root	_	_
4	the	the	DET	DT	_	5	det	_	_
5	mouse	mouse	NOUN	NN	_	3	dobj	_	_
6	.	.	PUNCT	.	_	3	punct	_	_

"""

    # Load with both implementations
    original_sentences = list(original_load_conllu(test_conllu))
    modern_sentences = list(modern_load_conllu(test_conllu))

    assert len(original_sentences) == len(modern_sentences), f"Different sentence counts: {len(original_sentences)} vs {len(modern_sentences)}"

    # Test different option configurations
    test_configs = [
        {"cut": True, "resolve_relcl": True, "resolve_conj": False},
        {"cut": False, "resolve_relcl": False, "resolve_conj": True},
        {"simple": True},
        {"resolve_amod": True, "resolve_appos": True},
    ]

    for config in test_configs:
        print(f"\nTesting config: {config}")

        # Process with both implementations
        original_opts = OriginalPredPattOpts(**config)
        modern_opts = ModernPredPattOpts(**config)

        original_parse = original_sentences[0][1]
        modern_parse = modern_sentences[0][1]

        original_pp = OriginalPredPatt(original_parse, opts=original_opts)
        modern_pp = ModernPredPatt(modern_parse, opts=modern_opts)

        # Compare outputs
        original_output = original_pp.pprint(color=False, track_rule=False)
        modern_output = modern_pp.pprint(color=False, track_rule=False)

        if original_output != modern_output:
            print("MISMATCH!")
            print(f"Original output:\n{original_output}")
            print(f"Modern output:\n{modern_output}")
            assert False, "Output mismatch detected"
        else:
            print("✓ Outputs match")

    print("\n✓ All tests passed!")


if __name__ == "__main__":
    test_comparison()
