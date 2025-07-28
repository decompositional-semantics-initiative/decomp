"""Universal Dependencies parse representation.

This module contains the UDParse class for representing dependency parses
and the DepTriple namedtuple for representing individual dependencies.
"""

from __future__ import annotations

from collections import defaultdict, namedtuple
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core.token import Token

# Import at runtime to avoid circular dependency
def _get_dep_v1():
    from ..util.ud import dep_v1
    return dep_v1


class DepTriple(namedtuple('DepTriple', 'rel gov dep')):
    """Dependency triple representing a single dependency relation.
    
    A named tuple with three fields representing a dependency edge in the parse tree.
    
    Attributes
    ----------
    rel : str
        The dependency relation type (e.g., 'nsubj', 'dobj').
    gov : int | Token
        The governor (head) of the dependency. Can be token index or Token object.
    dep : int | Token
        The dependent of the dependency. Can be token index or Token object.
        
    Notes
    -----
    The __repr__ format shows the relation with dependent first: rel(dep,gov).
    This ordering (dep before gov) is preserved for compatibility.
    """
    
    def __repr__(self) -> str:
        """Return string representation in format rel(dep,gov).
        
        Note that dependent comes before governor in the output.
        
        Returns
        -------
        str
            String representation like 'nsubj(0,2)'.
        """
        return '%s(%s,%s)' % (self.rel, self.dep, self.gov)


class UDParse:
    """Universal Dependencies parse representation.
    
    Container for a dependency parse including tokens, POS tags, and dependency relations.
    
    Parameters
    ----------
    tokens : list
        List of tokens (strings or Token objects) in the sentence.
    tags : list[str]
        List of POS tags corresponding to tokens.
    triples : list[DepTriple]
        List of dependency relations in the parse.
    ud : module, optional
        Universal Dependencies module (ignored - always uses dep_v1).
        
    Attributes
    ----------
    ud : module
        The UD module (always set to dep_v1 regardless of parameter).
    tokens : list
        List of tokens in the sentence.
    tags : list[str]
        List of POS tags.
    triples : list[DepTriple]
        List of dependency relations.
    governor : dict
        Maps dependent index/token to its governing DepTriple.
    dependents : defaultdict[list]
        Maps governor index/token to list of dependent DepTriples.
    """
    
    def __init__(
        self, 
        tokens: list[Any],
        tags: list[str],
        triples: list[DepTriple],
        ud: Any = None
    ) -> None:
        """Initialize UDParse with tokens, tags, and dependency triples.
        
        Parameters
        ----------
        tokens : list
            List of tokens (strings or Token objects).
        tags : list[str]
            List of POS tags.
        triples : list[DepTriple]
            List of dependency relations.
        ud : module, optional
            UD module (ignored - always uses dep_v1).
        """
        # maintain exact behavior - always set to dep_v1
        self.ud = _get_dep_v1()
        self.tokens = tokens
        self.tags = tags
        self.triples = triples
        
        # build governor mapping: dependent -> DepTriple
        self.governor: dict[Any, DepTriple] = {e.dep: e for e in triples}
        
        # build dependents mapping: governor -> [DepTriple]
        self.dependents: defaultdict[Any, list[DepTriple]] = defaultdict(list)
        for e in self.triples:
            self.dependents[e.gov].append(e)
    
    def pprint(self, color: bool = False, K: int = 1) -> str:
        """Pretty-print list of dependencies.
        
        Parameters
        ----------
        color : bool, optional
            Whether to use colored output (default: False).
        K : int, optional
            Number of columns to use (default: 1).
            
        Returns
        -------
        str
            Formatted string representation of dependencies.
        """
        # import here to avoid circular dependency
        from tabulate import tabulate
        from termcolor import colored
        
        tokens1 = self.tokens + ['ROOT']
        C = colored('/%s', 'magenta') if color else '/%s'
        E = ['%s(%s%s, %s%s)' % (e.rel, tokens1[e.dep],
                                 C % e.dep,
                                 tokens1[e.gov],
                                 C % e.gov)
             for e in sorted(self.triples, key=lambda x: x.dep)]
        cols = [[] for _ in range(K)]
        for i, x in enumerate(E):
            cols[i % K].append(x)
        # add padding to columns because zip stops at shortest iterator.
        for c in cols:
            c.extend('' for _ in range(len(cols[0]) - len(c)))
        return tabulate(zip(*cols), tablefmt='plain')
    
    def latex(self) -> bytes:
        """Generate LaTeX code for dependency diagram.
        
        Creates LaTeX code using tikz-dependency package for visualization.
        
        Returns
        -------
        bytes
            UTF-8 encoded LaTeX document.
        """
        # http://ctan.mirrors.hoobly.com/graphics/pgf/contrib/tikz-dependency/tikz-dependency-doc.pdf
        boilerplate = r"""\documentclass{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{tikz}
\usepackage{tikz-dependency}
\begin{document}
\begin{dependency}[theme = brazil]
\begin{deptext}
%s \\
%s \\
\end{deptext}
%s
\end{dependency}
\end{document}"""
        tok = ' \\& '.join(x.replace('&', r'and').replace('_', ' ') for x in self.tokens)
        tag = ' \\& '.join(self.tags).lower()
        dep = '\n'.join(r'\depedge{%d}{%d}{%s}' % (e.gov+1, e.dep+1, e.rel)
                        for e in self.triples if e.gov >= 0)
        return (boilerplate % (tok, tag, dep)).replace('$','\\$').encode('utf-8')
    
    def view(self, do_open: bool = True) -> str | None:
        """Open a dependency parse diagram of the sentence.
        
        Requires that pdflatex be in PATH and that Daniele Pighin's
        tikz-dependency.sty be in the current directory.
        
        Parameters
        ----------
        do_open : bool, optional
            Whether to open the PDF file (default: True).
            
        Returns
        -------
        str | None
            Path to the generated PDF file, or None if generation fails.
        """
        import os
        from hashlib import md5
        
        latex = self.latex()
        was = os.getcwd()
        try:
            os.chdir('/tmp')
            base = 'parse_%s' % md5(' '.join(self.tokens).encode('ascii', errors='ignore')).hexdigest()
            pdf = '%s.pdf' % base
            if not os.path.exists(pdf):
                with open('%s.tex' % base, 'wb') as f:
                    f.write(latex)
                os.system('pdflatex -halt-on-error %s.tex >/dev/null' % base)
            if do_open:
                os.system('xdg-open %s' % pdf)
            return os.path.abspath(pdf)
        finally:
            os.chdir(was)
    
    def toimage(self) -> str | None:
        """Convert parse diagram to PNG image.
        
        Creates a PNG image of the dependency parse diagram.
        
        Returns
        -------
        str | None
            Path to the generated PNG file, or None if generation fails.
        """
        import os
        
        img = self.view(do_open=False)
        if img is not None:
            out = img[:-4] + '.png'
            if not os.path.exists(out):
                cmd = 'gs -dBATCH -dNOPAUSE -sDEVICE=pngalpha -o %s %s' % (out, img)
                os.system(cmd)
            return out
        return None