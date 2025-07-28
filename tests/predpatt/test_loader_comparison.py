"""
Comparison tests between original and modernized loader implementations.

These tests ensure that the modernized version behaves identically to the original.
"""

import pytest
import os

# Import both versions
from decomp.semantics.predpatt.util.load import load_conllu as original_load_conllu
from decomp.semantics.predpatt.util.load import DepTriple as OriginalDepTriple
from decomp.semantics.predpatt.parsing.loader import load_conllu as modern_load_conllu
from decomp.semantics.predpatt.parsing.loader import DepTriple as ModernDepTriple


class TestDepTripleComparison:
    """Test that modern DepTriple behaves identically to original."""
    
    def test_deptriple_identical(self):
        """Test that both DepTriples have identical behavior."""
        orig = OriginalDepTriple(rel="nsubj", gov=2, dep=0)
        modern = ModernDepTriple(rel="nsubj", gov=2, dep=0)
        
        assert repr(orig) == repr(modern) == "nsubj(0,2)"
        assert orig.rel == modern.rel
        assert orig.gov == modern.gov
        assert orig.dep == modern.dep
    
    def test_deptriple_separate_classes(self):
        """Test that loader uses its own DepTriple class."""
        from decomp.semantics.predpatt.UDParse import DepTriple as UDParseDepTriple
        
        # All three should be different classes
        assert OriginalDepTriple is not UDParseDepTriple
        assert ModernDepTriple is not UDParseDepTriple
        assert OriginalDepTriple is not ModernDepTriple


class TestLoadConlluComparison:
    """Test that modern load_conllu behaves identically to original."""
    
    def test_simple_sentence_identical(self):
        """Test loading simple sentence produces identical results."""
        content = """1	I	I	PRP	PRP	_	2	nsubj	_	_
2	eat	eat	VBP	VBP	_	0	root	_	_
3	apples	apple	NNS	NNS	_	2	dobj	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        assert len(orig_results) == len(modern_results) == 1
        
        orig_id, orig_parse = orig_results[0]
        modern_id, modern_parse = modern_results[0]
        
        assert orig_id == modern_id == "sent_1"
        assert orig_parse.tokens == modern_parse.tokens
        assert orig_parse.tags == modern_parse.tags
        assert len(orig_parse.triples) == len(modern_parse.triples)
    
    def test_sent_id_comment_identical(self):
        """Test sent_id comment parsing is identical."""
        content = """# sent_id = test_123
1	Word	word	NN	NN	_	0	root	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_id, _ = orig_results[0]
        modern_id, _ = modern_results[0]
        
        # Both should include the "= " part!
        assert orig_id == modern_id == "= test_123"
    
    def test_regular_comment_identical(self):
        """Test regular comment parsing is identical."""
        content = """# This is a comment
1	Word	word	NN	NN	_	0	root	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_id, _ = orig_results[0]
        modern_id, _ = modern_results[0]
        
        # Should strip the # and leading space
        assert orig_id == modern_id == "This is a comment"
    
    def test_multitoken_skip_identical(self):
        """Test multi-token line skipping is identical."""
        content = """1-2	vámonos	_	_	_	_	_	_	_	_
1	vamos	ir	VERB	VERB	_	0	root	_	_
2	nos	nosotros	PRON	PRON	_	1	dobj	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_id, orig_parse = orig_results[0]
        modern_id, modern_parse = modern_results[0]
        
        assert orig_parse.tokens == modern_parse.tokens == ["vamos", "nos"]
    
    def test_triple_creation_identical(self):
        """Test that triple creation is identical."""
        content = """1	I	I	PRP	PRP	_	2	nsubj	_	_
2	eat	eat	VBP	VBP	_	0	root	_	_
3	apples	apple	NNS	NNS	_	2	dobj	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_parse = orig_results[0][1]
        modern_parse = modern_results[0][1]
        
        # Check each triple
        for i in range(len(orig_parse.triples)):
            orig_t = orig_parse.triples[i]
            modern_t = modern_parse.triples[i]
            assert orig_t.rel == modern_t.rel
            assert orig_t.gov == modern_t.gov
            assert orig_t.dep == modern_t.dep
    
    def test_tags_are_tuples_identical(self):
        """Test that tags are stored as tuples in both versions."""
        content = """1	The	the	DET	DT	_	2	det	_	_
2	cat	cat	NOUN	NN	_	0	root	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_parse = orig_results[0][1]
        modern_parse = modern_results[0][1]
        
        # Both should store tags as tuples
        assert isinstance(orig_parse.tags, tuple)
        assert isinstance(modern_parse.tags, tuple)
        assert orig_parse.tags == modern_parse.tags
    
    def test_column_extraction_identical(self):
        """Test that correct columns are extracted identically."""
        # Use UPOS (column 4) not XPOS (column 5)
        content = """1	The	the	DET	DT	_	3	det	_	_
2	cat	cat	NOUN	NN	_	3	nsubj	_	_
3	sat	sit	VERB	VBD	_	0	root	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_parse = orig_results[0][1]
        modern_parse = modern_results[0][1]
        
        # Should use column 4 (UPOS): DET, NOUN, VERB
        assert orig_parse.tags == modern_parse.tags == ("DET", "NOUN", "VERB")
    
    def test_empty_content_identical(self):
        """Test empty content handling is identical."""
        orig_results = list(original_load_conllu(""))
        modern_results = list(modern_load_conllu(""))
        
        assert len(orig_results) == len(modern_results) == 0
    
    def test_unicode_handling_identical(self):
        """Test Unicode content is handled identically."""
        content = """1	café	café	NN	NN	_	0	root	_	_
2	niño	niño	NN	NN	_	1	nmod	_	_"""
        
        orig_results = list(original_load_conllu(content))
        modern_results = list(modern_load_conllu(content))
        
        orig_parse = orig_results[0][1]
        modern_parse = modern_results[0][1]
        
        assert orig_parse.tokens == modern_parse.tokens == ["café", "niño"]
    
    def test_file_loading_identical(self, tmp_path):
        """Test loading from file is identical."""
        content = """1	Test	test	NN	NN	_	0	root	_	_"""
        
        test_file = tmp_path / "test.conllu"
        test_file.write_text(content, encoding='utf-8')
        
        orig_results = list(original_load_conllu(str(test_file)))
        modern_results = list(modern_load_conllu(str(test_file)))
        
        assert len(orig_results) == len(modern_results) == 1
        assert orig_results[0][0] == modern_results[0][0]
        assert orig_results[0][1].tokens == modern_results[0][1].tokens


class TestRealDataComparison:
    """Test with real CoNLL-U files."""
    
    def test_rawtree_file_identical(self):
        """Test loading rawtree.conllu produces identical results."""
        test_file = "/Users/awhite48/Projects/decomp/tests/data/rawtree.conllu"
        if not os.path.exists(test_file):
            pytest.skip("Test file not found")
        
        orig_results = list(original_load_conllu(test_file))
        modern_results = list(modern_load_conllu(test_file))
        
        assert len(orig_results) == len(modern_results)
        
        for i, (orig, modern) in enumerate(zip(orig_results, modern_results)):
            orig_id, orig_parse = orig
            modern_id, modern_parse = modern
            
            assert orig_id == modern_id
            assert orig_parse.tokens == modern_parse.tokens
            assert orig_parse.tags == modern_parse.tags
            assert len(orig_parse.triples) == len(modern_parse.triples)
    
    def test_en_ud_dev_identical(self):
        """Test loading en-ud-dev.conllu produces identical results."""
        test_file = "/Users/awhite48/Projects/decomp/tests/predpatt/en-ud-dev.conllu"
        if not os.path.exists(test_file):
            pytest.skip("Test file not found")
        
        # Just check first few sentences for performance
        orig_results = list(original_load_conllu(test_file))[:5]
        modern_results = list(modern_load_conllu(test_file))[:5]
        
        assert len(orig_results) == len(modern_results)
        
        for orig, modern in zip(orig_results, modern_results):
            orig_id, orig_parse = orig
            modern_id, modern_parse = modern
            
            assert orig_id == modern_id
            assert orig_parse.tokens == modern_parse.tokens
            assert orig_parse.tags == modern_parse.tags


class TestWindowsWorkaroundComparison:
    """Test Windows ValueError workaround behaves identically."""
    
    def test_long_string_handling(self):
        """Test that long strings are handled identically."""
        # Create a long string with proper tab separation
        long_content = "\t".join(["1", "Word", "word", "NN", "NN", "_", "0", "root", "_", "_"]) * 100
        
        # Both should treat as content, not filename
        try:
            orig_results = list(original_load_conllu(long_content))
        except:
            orig_results = []
        
        try:
            modern_results = list(modern_load_conllu(long_content))
        except:
            modern_results = []
        
        # Both should fail in the same way (or both succeed)
        assert len(orig_results) == len(modern_results)