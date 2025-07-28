"""
Load different sources of data.

This module provides functions to load dependency parses from various formats,
particularly focusing on CoNLL-U format files.
"""

from __future__ import annotations

import codecs
import os
from collections.abc import Iterator
from typing import Any

from ..parsing.udparse import DepTriple, UDParse


def load_comm(
    filename: str,
    tool: str = 'ud converted ptb trees using pyStanfordDependencies'
) -> Iterator[tuple[str, UDParse]]:
    """Load a concrete communication file with required pyStanfordDependencies output.

    Parameters
    ----------
    filename : str
        Path to the concrete communication file.
    tool : str, optional
        The tool name to look for in the dependency parse metadata.

    Yields
    ------
    tuple[str, UDParse]
        Tuples of (section_label, parse) for each sentence.
    """
    # import here to avoid requiring concrete
    from concrete.util.file_io import read_communication_from_file
    comm = read_communication_from_file(filename)
    if comm.sectionList:
        for sec in comm.sectionList:
            if sec.sentenceList:
                for sent in sec.sentenceList:
                    yield sec.label, get_udparse(sent, tool)


def load_conllu(filename_or_content: str) -> Iterator[tuple[str, UDParse]]:
    """Load CoNLL-U style files (e.g., the Universal Dependencies treebank).

    Parameters
    ----------
    filename_or_content : str
        Either a path to a CoNLL-U file or the content string itself.

    Yields
    ------
    tuple[str, UDParse]
        Tuples of (sentence_id, parse) for each sentence in the file.

    Notes
    -----
    - Sentence IDs default to "sent_N" where N starts at 1
    - Lines starting with "# sent_id" override the sentence ID
    - Other comment lines (starting with #) are used as ID if no sent_id found
    - Multi-token lines (with '-' in first column) are skipped
    - Expects 10 tab-separated columns per data line
    """
    sent_num = 1
    try:
        if os.path.isfile(filename_or_content):
            with codecs.open(filename_or_content, encoding='utf-8') as f:
                content = f.read().strip()
        else:
            content = filename_or_content.strip()
    except ValueError:
        # work around an issue on windows: `os.path.isfile` will call `os.stat`,
        # which throws a ValueError if the "filename" is too long. Possibly
        # a python bug in that this could be caught in os.path.isfile? Though
        # I found some related issues where discussion suggests it was deemed
        # not a bug.
        content = filename_or_content.strip()

    for block in content.split('\n\n'):
        block = block.strip()
        if not block:
            continue
        lines = []
        sent_id = f'sent_{sent_num}'
        has_sent_id = 0
        for line in block.split('\n'):
            if line.startswith('#'):
                if line.startswith('# sent_id'):
                    sent_id = line[10:].strip()
                    has_sent_id = 1
                else:
                    if not has_sent_id:   # don't take subsequent comments as sent_id
                        sent_id = line[1:].strip()
                continue
            parts = line.split('\t') # data appears to use '\t'
            if '-' in parts[0]:      # skip multi-tokens, e.g., on Spanish UD bank
                continue
            assert len(parts) == 10, parts
            lines.append(parts)
        [_, tokens, _, tags, _, _, gov, gov_rel, _, _] = list(zip(*lines, strict=False))
        triples = [
            DepTriple(rel, int(gov)-1, dep)
            for dep, (rel, gov) in enumerate(zip(gov_rel, gov, strict=False))
        ]
        parse = UDParse(list(tokens), list(tags), triples)
        yield sent_id, parse
        sent_num += 1


def get_tags(tokenization: Any, tagging_type: str = 'POS') -> list[str]:
    """Extract tags of a specific type from a tokenization.

    Parameters
    ----------
    tokenization : Tokenization
        A Concrete tokenization object.
    tagging_type : str, optional
        The type of tagging to extract (default: 'POS').

    Returns
    -------
    list[str]
        List of tags in token order.
    """
    for token_tagging in tokenization.tokenTaggingList:
        if token_tagging.taggingType == tagging_type:
            idx2pos = {taggedToken.tokenIndex: taggedToken.tag
                       for taggedToken in token_tagging.taggedTokenList}
            return [idx2pos[idx] for idx in sorted(idx2pos.keys())]
    # Return empty list if no matching tagging type found
    return []


def get_udparse(sent: Any, tool: str) -> UDParse:
    """Create a ``UDParse`` from a sentence extracted from a Communication.

    Parameters
    ----------
    sent : Sentence
        A Concrete Sentence object.
    tool : str
        The tool name to look for in dependency parse metadata.

    Returns
    -------
    UDParse
        The parsed representation of the sentence.
    """
    # extract dependency parse for Communication.
    triples = []
    for ud_parse in sent.tokenization.dependencyParseList:
        if ud_parse.metadata.tool == tool:
            for dependency in ud_parse.dependencyList:
                triples.append(DepTriple(dependency.edgeType,
                                         dependency.gov, dependency.dep))
            break

    # Extract token strings
    tokens = [x.text for x in sent.tokenization.tokenList.tokenList]

    # Extract POS tags
    tags = get_tags(sent.tokenization, 'POS')

    #triples.sort(key=lambda triple: triple.dep)
    parse = UDParse(tokens=tokens, tags=tags, triples=triples)

    # Extract lemmas
    #parse.lemmas = get_tags(sent.tokenization, 'LEMMA')

    return parse
