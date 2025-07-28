"""
Tests for PredPattOpts class to verify defaults and behavior.

PredPattOpts Class Documentation
================================

Configuration options for PredPatt extraction behavior.

Default Values
--------------
simple = False              # Extract simple predicates (exclude aux/advmod)
cut = False                 # Treat xcomp as independent predicate  
resolve_relcl = False       # Resolve relative clause modifiers
resolve_appos = False       # Resolve appositives
resolve_amod = False        # Resolve adjectival modifiers
resolve_conj = False        # Resolve conjunctions
resolve_poss = False        # Resolve possessives
borrow_arg_for_relcl = True # Borrow arguments for relative clauses
big_args = False            # Include all subtree tokens in arguments
strip = True                # Strip leading/trailing punctuation
ud = "1.0"                  # Universal Dependencies version

Validation
----------
- ud must be exactly "1.0" or "2.0" (string comparison)
- AssertionError raised if ud is invalid
"""

import pytest
from decomp.semantics.predpatt.patt import PredPattOpts as OriginalOpts
from decomp.semantics.predpatt.core import PredPattOpts as ModernOpts
from decomp.semantics.predpatt.util.ud import dep_v1, dep_v2


class TestPredPattOptsDefaults:
    """Test default values match exactly."""
    
    def test_all_defaults(self):
        """Test all default values are correct."""
        opts = ModernOpts()
        
        assert opts.simple is False
        assert opts.cut is False
        assert opts.resolve_relcl is False
        assert opts.resolve_appos is False
        assert opts.resolve_amod is False
        assert opts.resolve_conj is False
        assert opts.resolve_poss is False
        assert opts.borrow_arg_for_relcl is True  # Note: True by default
        assert opts.big_args is False
        assert opts.strip is True  # Note: True by default
        assert opts.ud == "1.0"  # dep_v1.VERSION
    
    def test_defaults_match_original(self):
        """Test defaults match original implementation."""
        orig = OriginalOpts()
        modern = ModernOpts()
        
        assert orig.simple == modern.simple == False
        assert orig.cut == modern.cut == False
        assert orig.resolve_relcl == modern.resolve_relcl == False
        assert orig.resolve_appos == modern.resolve_appos == False
        assert orig.resolve_amod == modern.resolve_amod == False
        assert orig.resolve_conj == modern.resolve_conj == False
        assert orig.resolve_poss == modern.resolve_poss == False
        assert orig.borrow_arg_for_relcl == modern.borrow_arg_for_relcl == True
        assert orig.big_args == modern.big_args == False
        assert orig.strip == modern.strip == True
        assert orig.ud == modern.ud == dep_v1.VERSION == "1.0"


class TestPredPattOptsInitialization:
    """Test initialization with various parameters."""
    
    def test_all_true(self):
        """Test setting all boolean options to True."""
        opts = ModernOpts(
            simple=True,
            cut=True,
            resolve_relcl=True,
            resolve_appos=True,
            resolve_amod=True,
            resolve_conj=True,
            resolve_poss=True,
            borrow_arg_for_relcl=True,
            big_args=True,
            strip=True
        )
        
        assert all([
            opts.simple,
            opts.cut,
            opts.resolve_relcl,
            opts.resolve_appos,
            opts.resolve_amod,
            opts.resolve_conj,
            opts.resolve_poss,
            opts.borrow_arg_for_relcl,
            opts.big_args,
            opts.strip
        ])
    
    def test_all_false(self):
        """Test setting all boolean options to False."""
        opts = ModernOpts(
            simple=False,
            cut=False,
            resolve_relcl=False,
            resolve_appos=False,
            resolve_amod=False,
            resolve_conj=False,
            resolve_poss=False,
            borrow_arg_for_relcl=False,
            big_args=False,
            strip=False
        )
        
        assert not any([
            opts.simple,
            opts.cut,
            opts.resolve_relcl,
            opts.resolve_appos,
            opts.resolve_amod,
            opts.resolve_conj,
            opts.resolve_poss,
            opts.borrow_arg_for_relcl,
            opts.big_args,
            opts.strip
        ])
    
    def test_mixed_options(self):
        """Test mixed true/false options."""
        opts = ModernOpts(
            simple=True,
            cut=False,
            resolve_relcl=True,
            resolve_appos=False,
            resolve_amod=True,
            resolve_conj=False,
            resolve_poss=True,
            borrow_arg_for_relcl=False,
            big_args=True,
            strip=False
        )
        
        assert opts.simple is True
        assert opts.cut is False
        assert opts.resolve_relcl is True
        assert opts.resolve_appos is False
        assert opts.resolve_amod is True
        assert opts.resolve_conj is False
        assert opts.resolve_poss is True
        assert opts.borrow_arg_for_relcl is False
        assert opts.big_args is True
        assert opts.strip is False
    
    def test_ud_versions(self):
        """Test UD version settings."""
        # v1 (default)
        opts1 = ModernOpts()
        assert opts1.ud == "1.0"
        
        # v1 explicit
        opts2 = ModernOpts(ud="1.0")
        assert opts2.ud == "1.0"
        
        # v2
        opts3 = ModernOpts(ud="2.0")
        assert opts3.ud == "2.0"
        
        # using dep module constants
        opts4 = ModernOpts(ud=dep_v1.VERSION)
        assert opts4.ud == "1.0"
        
        opts5 = ModernOpts(ud=dep_v2.VERSION)
        assert opts5.ud == "2.0"


class TestPredPattOptsValidation:
    """Test validation logic."""
    
    def test_invalid_ud_version(self):
        """Test invalid UD version raises AssertionError."""
        with pytest.raises(AssertionError) as exc_info:
            ModernOpts(ud="3.0")
        assert 'the ud version "3.0" is not in {"1.0", "2.0"}' in str(exc_info.value)
        
        with pytest.raises(AssertionError) as exc_info:
            ModernOpts(ud="v1")
        assert 'the ud version "v1" is not in {"1.0", "2.0"}' in str(exc_info.value)
        
        with pytest.raises(AssertionError) as exc_info:
            ModernOpts(ud="")
        assert 'the ud version "" is not in {"1.0", "2.0"}' in str(exc_info.value)
    
    def test_ud_string_conversion(self):
        """Test ud is converted to string."""
        # float 1.0 becomes "1.0" which is valid
        opts = ModernOpts(ud=1.0)
        assert opts.ud == "1.0"
        
        # float 2.0 becomes "2.0" which is valid
        opts2 = ModernOpts(ud=2.0)
        assert opts2.ud == "2.0"
        
        # but int 1 becomes "1" which is invalid
        with pytest.raises(AssertionError) as exc_info:
            ModernOpts(ud=1)
        assert 'the ud version "1" is not in {"1.0", "2.0"}' in str(exc_info.value)
        
        # int 2 becomes "2" which is invalid
        with pytest.raises(AssertionError) as exc_info:
            ModernOpts(ud=2)
        assert 'the ud version "2" is not in {"1.0", "2.0"}' in str(exc_info.value)
    
    def test_validation_matches_original(self):
        """Test validation behavior matches original."""
        # valid versions work in both
        orig1 = OriginalOpts(ud="1.0")
        modern1 = ModernOpts(ud="1.0")
        assert orig1.ud == modern1.ud == "1.0"
        
        orig2 = OriginalOpts(ud="2.0")
        modern2 = ModernOpts(ud="2.0")
        assert orig2.ud == modern2.ud == "2.0"
        
        # invalid versions fail in both
        with pytest.raises(AssertionError):
            OriginalOpts(ud="invalid")
        with pytest.raises(AssertionError):
            ModernOpts(ud="invalid")


class TestPredPattOptsAttributeOrder:
    """Test attribute initialization order matches original."""
    
    def test_initialization_order(self):
        """Test attributes are set in exact same order as original."""
        # We can't directly test order, but we can verify all attributes exist
        opts = ModernOpts()
        
        # attributes in order from original __init__
        expected_attrs = [
            'simple', 'cut', 'resolve_relcl', 'resolve_appos', 
            'resolve_amod', 'resolve_poss', 'resolve_conj',
            'big_args', 'strip', 'borrow_arg_for_relcl', 'ud'
        ]
        
        for attr in expected_attrs:
            assert hasattr(opts, attr)


class TestPredPattOptsCombinations:
    """Test various option combinations."""
    
    def test_simple_mode(self):
        """Test simple mode configuration."""
        opts = ModernOpts(simple=True)
        
        assert opts.simple is True
        # other options remain default
        assert opts.cut is False
        assert opts.resolve_relcl is False
        assert opts.strip is True
    
    def test_cut_mode(self):
        """Test cut mode configuration."""
        opts = ModernOpts(cut=True)
        
        assert opts.cut is True
        # other options remain default
        assert opts.simple is False
        assert opts.borrow_arg_for_relcl is True
    
    def test_resolve_all(self):
        """Test enabling all resolve options."""
        opts = ModernOpts(
            resolve_relcl=True,
            resolve_appos=True,
            resolve_amod=True,
            resolve_conj=True,
            resolve_poss=True
        )
        
        assert opts.resolve_relcl is True
        assert opts.resolve_appos is True
        assert opts.resolve_amod is True
        assert opts.resolve_conj is True
        assert opts.resolve_poss is True
        
        # other options remain default
        assert opts.simple is False
        assert opts.cut is False
    
    def test_typical_configurations(self):
        """Test typical configuration combinations."""
        # Configuration 1: Simple predicates with conjunction resolution
        opts1 = ModernOpts(simple=True, resolve_conj=True)
        assert opts1.simple is True
        assert opts1.resolve_conj is True
        assert opts1.strip is True  # default
        
        # Configuration 2: Full resolution
        opts2 = ModernOpts(
            resolve_relcl=True,
            resolve_appos=True,
            resolve_amod=True,
            resolve_conj=True,
            resolve_poss=True,
            big_args=False,
            strip=True
        )
        assert all([
            opts2.resolve_relcl,
            opts2.resolve_appos,
            opts2.resolve_amod,
            opts2.resolve_conj,
            opts2.resolve_poss
        ])
        assert opts2.big_args is False
        assert opts2.strip is True
        
        # Configuration 3: Cut mode with borrowed arguments
        opts3 = ModernOpts(
            cut=True,
            borrow_arg_for_relcl=True,
            resolve_relcl=True
        )
        assert opts3.cut is True
        assert opts3.borrow_arg_for_relcl is True
        assert opts3.resolve_relcl is True