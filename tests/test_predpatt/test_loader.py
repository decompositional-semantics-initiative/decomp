"""
Tests for CoNLL-U loader functionality to document current behavior.

load_conllu() Function Documentation
===================================

The load_conllu function loads CoNLL-U format files (Universal Dependencies treebank format).

Input Format
-----------
- Takes either a filename (path to file) or content string
- Windows workaround: handles ValueError from os.path.isfile for long strings
- Splits content by double newlines to get sentence blocks
- Skips empty blocks

Sentence ID Parsing
------------------
1. Default: "sent_<number>" where number starts at 1
2. If line starts with "# sent_id", extracts ID after that prefix
3. Otherwise, if line starts with "#" (and no sent_id found), uses rest of comment as ID
4. Sets has_sent_id=1 after finding "# sent_id" to prevent subsequent comments from overriding

Line Parsing
-----------
- Skips comment lines (starting with #)
- Skips multi-token lines (where first column contains '-')
- Expects exactly 10 tab-separated columns
- Columns: ID, TOKEN, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC

Triple Creation
--------------
- Creates DepTriple(rel, gov-1, dep) for each token
- gov is decremented by 1 (CoNLL-U uses 1-based indexing, internal uses 0-based)
- dep is the token index (0-based)
- Note: DepTriple is defined locally in load.py, not imported!

Output
------
- Yields tuples of (sent_id, UDParse)
- UDParse created with (tokens, tags, triples)
- tags come from column 4 (UPOS)
"""

import pytest
import os
from decomp.semantics.predpatt.parsing.loader import load_conllu, DepTriple
from decomp.semantics.predpatt.parsing.udparse import UDParse


class TestLoadConlluBasic:
    """Test basic CoNLL-U loading functionality."""
    
    def test_load_simple_sentence(self):
        """Test loading a simple CoNLL-U sentence."""
        content = """1	I	I	PRP	PRP	_	2	nsubj	_	_
2	eat	eat	VBP	VBP	_	0	root	_	_
3	apples	apple	NNS	NNS	_	2	dobj	_	_"""
        
        results = list(load_conllu(content))
        assert len(results) == 1
        
        sent_id, parse = results[0]
        assert sent_id == "sent_1"
        assert isinstance(parse, UDParse)
        assert parse.tokens == ["I", "eat", "apples"]
        assert parse.tags == ("PRP", "VBP", "NNS")  # stored as tuple!
        assert len(parse.triples) == 3
    
    def test_load_from_file(self, tmp_path):
        """Test loading from a file."""
        content = """1	Test	test	NN	NN	_	0	root	_	_"""
        
        # Create a temporary file
        test_file = tmp_path / "test.conllu"
        test_file.write_text(content, encoding='utf-8')
        
        results = list(load_conllu(str(test_file)))
        assert len(results) == 1
        sent_id, parse = results[0]
        assert parse.tokens == ["Test"]
    
    def test_multiple_sentences(self):
        """Test loading multiple sentences."""
        content = """1	First	first	JJ	JJ	_	0	root	_	_

1	Second	second	JJ	JJ	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        assert len(results) == 2
        
        sent_id1, parse1 = results[0]
        sent_id2, parse2 = results[1]
        
        assert sent_id1 == "sent_1"
        assert sent_id2 == "sent_2"
        assert parse1.tokens == ["First"]
        assert parse2.tokens == ["Second"]
    
    def test_empty_content(self):
        """Test loading empty content."""
        results = list(load_conllu(""))
        assert len(results) == 0
        
        results = list(load_conllu("\n\n\n"))
        assert len(results) == 0


class TestLoadConlluComments:
    """Test comment and sentence ID handling."""
    
    def test_sent_id_comment(self):
        """Test parsing # sent_id comments."""
        content = """# sent_id = test_sentence_1
1	Word	word	NN	NN	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        assert sent_id == "= test_sentence_1"
    
    def test_regular_comment_as_id(self):
        """Test using regular comment as ID when no sent_id."""
        content = """# This is a test sentence
1	Word	word	NN	NN	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        assert sent_id == "This is a test sentence"
    
    def test_sent_id_takes_precedence(self):
        """Test that sent_id takes precedence over other comments."""
        content = """# First comment
# sent_id = actual_id
# Another comment
1	Word	word	NN	NN	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        assert sent_id == "= actual_id"
    
    def test_has_sent_id_flag(self):
        """Test that has_sent_id prevents subsequent comments from being used."""
        content = """# sent_id = correct_id
# This should not be used as ID
1	Word	word	NN	NN	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        assert sent_id == "= correct_id"
    
    def test_no_comment_default_id(self):
        """Test default ID when no comments."""
        content = """1	Word	word	NN	NN	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        assert sent_id == "sent_1"


class TestLoadConlluMultiTokens:
    """Test handling of multi-token lines."""
    
    def test_skip_multitoken_lines(self):
        """Test that lines with - in ID are skipped."""
        content = """1-2	vámonos	_	_	_	_	_	_	_	_
1	vamos	ir	VERB	_	_	0	root	_	_
2	nos	nosotros	PRON	_	_	1	dobj	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        
        # Multi-token line should be skipped
        assert parse.tokens == ["vamos", "nos"]
        assert len(parse.triples) == 2


class TestLoadConlluTripleCreation:
    """Test DepTriple creation from CoNLL-U data."""
    
    def test_triple_indexing(self):
        """Test that triples use correct 0-based indexing."""
        content = """1	I	I	PRP	PRP	_	2	nsubj	_	_
2	eat	eat	VBP	VBP	_	0	root	_	_
3	apples	apple	NNS	NNS	_	2	dobj	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        
        # Check triple structure
        # Token 0 (I) depends on token 1 (eat) with relation nsubj
        triple0 = parse.triples[0]
        assert triple0.dep == 0  # I
        assert triple0.gov == 1  # eat (2-1=1)
        assert triple0.rel == "nsubj"
        
        # Token 1 (eat) depends on ROOT with relation root
        triple1 = parse.triples[1]
        assert triple1.dep == 1  # eat
        assert triple1.gov == -1  # ROOT (0-1=-1)
        assert triple1.rel == "root"
        
        # Token 2 (apples) depends on token 1 (eat) with relation dobj
        triple2 = parse.triples[2]
        assert triple2.dep == 2  # apples
        assert triple2.gov == 1  # eat (2-1=1)
        assert triple2.rel == "dobj"
    
    def test_local_deptriple(self):
        """Test that loader uses its own DepTriple class."""
        from decomp.semantics.predpatt.parsing.loader import DepTriple as LoaderDepTriple
        from decomp.semantics.predpatt.parsing.udparse import DepTriple as UDParseDepTriple
        
        # They should be different classes (loader has its own)
        assert LoaderDepTriple is not UDParseDepTriple
        
        # But should have same repr format
        dt1 = LoaderDepTriple(rel="nsubj", gov=2, dep=0)
        dt2 = UDParseDepTriple(rel="nsubj", gov=2, dep=0)
        assert repr(dt1) == repr(dt2) == "nsubj(0,2)"


class TestLoadConlluEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_invalid_column_count(self):
        """Test that invalid column count raises assertion error."""
        content = """1	Word	word	NN	NN	_	0	root"""  # Only 8 columns
        
        with pytest.raises(AssertionError):
            list(load_conllu(content))
    
    def test_windows_long_string_workaround(self):
        """Test the Windows ValueError workaround for long strings."""
        # Create a very long string that would fail os.path.isfile on Windows
        # Each sentence needs to be separated by double newlines
        single_sentence = "1\tWord\tword\tNN\tNN\t_\t0\troot\t_\t_"
        long_content = "\n\n".join([single_sentence] * 1000)
        
        # Should not raise ValueError, should treat as content
        results = list(load_conllu(long_content))
        assert len(results) == 1000  # Should parse all 1000 sentences
    
    def test_unicode_content(self):
        """Test loading Unicode content."""
        content = """1	café	café	NN	NN	_	0	root	_	_
2	niño	niño	NN	NN	_	1	nmod	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        assert parse.tokens == ["café", "niño"]
    
    def test_empty_blocks_skipped(self):
        """Test that empty blocks are skipped."""
        content = """1	First	first	JJ	JJ	_	0	root	_	_


1	Second	second	JJ	JJ	_	0	root	_	_"""
        
        results = list(load_conllu(content))
        assert len(results) == 2  # Empty block in middle is skipped


class TestLoadConlluRealData:
    """Test with actual CoNLL-U files."""
    
    def test_load_test_data(self):
        """Test loading the test data file."""
        test_file = "/Users/awhite48/Projects/decomp/tests/data/rawtree.conllu"
        if os.path.exists(test_file):
            results = list(load_conllu(test_file))
            assert len(results) == 1
            
            sent_id, parse = results[0]
            assert sent_id == "sent_1"  # No sent_id comment in this file
            assert len(parse.tokens) == 29
            assert parse.tokens[0] == "The"
            assert parse.tokens[-1] == "."
    
    def test_column_data_extraction(self):
        """Test that correct columns are extracted."""
        content = """1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	cat	cat	NOUN	NN	Number=Sing	3	nsubj	_	_
3	sat	sit	VERB	VBD	Mood=Ind|Tense=Past	0	root	_	_"""
        
        results = list(load_conllu(content))
        sent_id, parse = results[0]
        
        # Column 2 is token
        assert parse.tokens == ["The", "cat", "sat"]
        
        # Column 3 is UPOS tag (0-indexed: column 3 is index 3)
        assert parse.tags == ("DET", "NOUN", "VERB")
        
        # Column 7 is dependency relation, column 6 is head
        assert parse.triples[0].rel == "det"
        assert parse.triples[1].rel == "nsubj"
        assert parse.triples[2].rel == "root"