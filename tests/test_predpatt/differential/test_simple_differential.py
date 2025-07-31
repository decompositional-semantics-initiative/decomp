"""Simple test of differential imports."""

import pytest


print("Starting test file...")

# Import external predpatt for comparison
import predpatt
print(f"predpatt imported: {predpatt}")

# Import from predpatt.patt
print("Importing from predpatt.patt...")
from predpatt.patt import Argument, Token


print("Import successful!")

def test_simple():
    """Simple test that imports work."""
    tok = Token(position=1, text="test", tag="NN")
    arg = Argument(tok)
    assert arg.root == tok
    print("Test passed!")

if __name__ == "__main__":
    test_simple()
