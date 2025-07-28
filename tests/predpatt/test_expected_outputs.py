"""Test PredPatt output against expected baseline files."""

import os
import pytest
import subprocess
import sys
from io import StringIO
from contextlib import redirect_stdout


# test configurations matching run.bash
TEST_CONFIGS = [
    {
        "name": "cut",
        "expect_file": "data.100.fine.all.ud-cut.expect",
        "options": {
            "resolve_poss": True,
            "resolve_relcl": True,
            "resolve_amod": True,
            "resolve_conj": True,
            "resolve_appos": True,
            "format": "plain",
            "cut": True,
            "track_rule": True,
            "show_deps": False,
            "simple": False,
        }
    },
    {
        "name": "norelcl",
        "expect_file": "data.100.fine.all.ud-norelcl.expect",
        "options": {
            "resolve_poss": False,
            "resolve_relcl": False,
            "resolve_amod": False,
            "resolve_conj": True,
            "resolve_appos": False,
            "format": "plain",
            "cut": False,
            "track_rule": True,
            "show_deps": True,
            "simple": False,
        }
    },
    {
        "name": "all",
        "expect_file": "data.100.fine.all.ud.expect",
        "options": {
            "resolve_poss": True,
            "resolve_relcl": True,
            "resolve_amod": True,
            "resolve_conj": True,
            "resolve_appos": True,
            "format": "plain",
            "cut": False,
            "track_rule": True,
            "show_deps": True,
            "simple": False,
        }
    },
    {
        "name": "simple",
        "expect_file": "data.100.fine.all.ud-simple.expect",
        "options": {
            "resolve_poss": True,
            "resolve_relcl": True,
            "resolve_amod": True,
            "resolve_conj": True,
            "resolve_appos": True,
            "format": "plain",
            "cut": False,
            "track_rule": True,
            "show_deps": True,
            "simple": True,
        }
    }
]


def run_predpatt_with_options(input_file, options):
    """Run PredPatt with specified options and return output."""
    from decomp.semantics.predpatt.util.load import load_comm
    from decomp.semantics.predpatt.patt import PredPatt, PredPattOpts
    
    # create PredPattOpts with the specified options
    opts = PredPattOpts(
        resolve_poss=options.get("resolve_poss", False),
        resolve_relcl=options.get("resolve_relcl", False),
        resolve_amod=options.get("resolve_amod", False),
        resolve_conj=options.get("resolve_conj", False),
        resolve_appos=options.get("resolve_appos", False),
        cut=options.get("cut", False),
        simple=options.get("simple", False),
    )
    
    # capture output
    output = StringIO()
    
    # process each sentence
    sentences = list(load_comm(input_file))
    for i, (sent_id, parse) in enumerate(sentences):
        # print sentence label and tokens (matching __main__.py)
        output.write(f'label:    {sent_id}\n')
        output.write(f'sentence: {" ".join(parse.tokens)}\n')
        
        # show dependencies if requested
        if options.get("show_deps", False):
            output.write('\n')
            output.write(f'tags: {" ".join("%s/%s" % (x, tag) for tag, x in list(zip(parse.tags, parse.tokens)))}\n')
            output.write('\n')
            output.write(parse.pprint(color=False, K=4))  # K=4 matches default show_deps_cols
            output.write('\n')
        
        # create and print predpatt
        predpatt = PredPatt(parse, opts=opts)
        
        output.write('\nppatt:\n')
        result = predpatt.pprint(
            track_rule=options.get("track_rule", False),
            color=False
        )
        output.write(result)
        
        # add three newlines after each sentence
        output.write('\n\n\n')
    
    return output.getvalue()


@pytest.mark.parametrize("config", TEST_CONFIGS, ids=[c["name"] for c in TEST_CONFIGS])
def test_predpatt_expected_output(config):
    """Test PredPatt output matches expected baseline files."""
    test_dir = os.path.dirname(__file__)
    input_file = os.path.join(test_dir, "data.100.fine.all.ud.comm")
    expect_file = os.path.join(test_dir, config["expect_file"])
    
    # check that input and expect files exist
    assert os.path.exists(input_file), f"Input file not found: {input_file}"
    assert os.path.exists(expect_file), f"Expected output file not found: {expect_file}"
    
    # get actual output
    actual_output = run_predpatt_with_options(input_file, config["options"])
    
    # read expected output
    with open(expect_file, 'r', encoding='utf-8') as f:
        expected_output = f.read()
    
    # normalize line endings
    actual_output = actual_output.replace('\r\n', '\n').replace('\r', '\n')
    expected_output = expected_output.replace('\r\n', '\n').replace('\r', '\n')
    
    # compare outputs
    if actual_output != expected_output:
        # write actual output for debugging
        debug_file = expect_file.replace('.expect', '.actual')
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(actual_output)
        
        # show first differing lines for debugging
        actual_lines = actual_output.splitlines()
        expected_lines = expected_output.splitlines()
        
        for i, (actual, expected) in enumerate(zip(actual_lines, expected_lines)):
            if actual != expected:
                pytest.fail(
                    f"Output mismatch at line {i+1}:\n"
                    f"Expected: {repr(expected)}\n"
                    f"Actual:   {repr(actual)}\n"
                    f"Debug output written to: {debug_file}"
                )
        
        # check line count difference
        if len(actual_lines) != len(expected_lines):
            pytest.fail(
                f"Line count mismatch:\n"
                f"Expected: {len(expected_lines)} lines\n"
                f"Actual:   {len(actual_lines)} lines\n"
                f"Debug output written to: {debug_file}"
            )
    
    # if we get here, outputs match
    assert actual_output == expected_output, "Output should match expected baseline"