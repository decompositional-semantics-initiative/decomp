"""Basic test to verify the copied PredPatt code works."""

import os


def test_basic_predpatt_loading():
    """Test that we can load and process CoNLL-U data using the copied PredPatt."""
    # import from the copied PredPatt modules
    from decomp.semantics.predpatt.core.options import PredPattOpts
    from decomp.semantics.predpatt.extraction.engine import PredPattEngine as PredPatt
    from decomp.semantics.predpatt.parsing.loader import load_conllu

    # get the test data file path
    test_dir = os.path.dirname(__file__)
    conllu_file = os.path.join(test_dir, 'en-ud-dev.conllu')

    print(f"\nLoading CoNLL-U file: {conllu_file}")

    # load the CoNLL-U file
    sentences = list(load_conllu(conllu_file))
    print(f"Loaded {len(sentences)} sentences")

    # process the first sentence
    if sentences:
        sentence_id, parse = sentences[0]
        print(f"\nFirst sentence ID: {sentence_id}")
        print(f"Parse object: {parse}")

        # create PredPatt options (default)
        opts = PredPattOpts()

        # extract predicates from the first sentence
        predpatt = PredPatt(parse, opts=opts)

        print(f"\nFound {len(predpatt.instances)} predicate instances")

        # print each predicate instance
        for i, instance in enumerate(predpatt.instances):
            print(f"\nPredicate {i + 1}:")
            print(f"  Root: {instance.root}")
            print(f"  Tokens: {instance.tokens}")
            print(f"  Arguments: {len(instance.arguments)}")
            for j, arg in enumerate(instance.arguments):
                print(f"    Arg {j + 1}: {arg}")

    print("\nTest completed successfully - PredPatt is working!")
