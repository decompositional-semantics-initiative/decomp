#!/usr/bin/env python
"""Visualization and output formatting utilities for PredPatt.

This module provides functions for pretty-printing PredPatt extractions,
including support for colored output, rule tracking, and various output formats.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, cast


if TYPE_CHECKING:
    from ..core.argument import Argument
    from ..core.predicate import Predicate
    from ..core.token import Token
    from ..extraction.engine import PredPattEngine
    from ..parsing.udparse import UDParse


try:
    from termcolor import colored as _termcolor_colored
    # Wrap termcolor's colored to have consistent signature
    def colored(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None) -> str:
        """Wrapper for termcolor.colored with consistent signature."""
        return _termcolor_colored(text, color, on_color, attrs)
except ImportError:
    # Fallback if termcolor is not available
    def colored(text: str, color: str | None = None, on_color: str | None = None, attrs: list[str] | None = None) -> str:
        """Fallback colored function when termcolor is not available."""
        return text

if TYPE_CHECKING:
    from decomp.semantics.predpatt.core.argument import Argument
    from decomp.semantics.predpatt.core.predicate import Predicate
    from decomp.semantics.predpatt.core.token import Token


def no_color(x: str, _: str) -> str:
    """No-color function for plain text output."""
    return x


def argument_names(args: list[Argument]) -> dict[Argument, str]:
    """Give arguments alpha-numeric names.

    Arguments are named using lowercase letters with optional numeric suffixes
    when there are more than 26 arguments.

    Parameters
    ----------
    args : list[Argument]
        List of arguments to name

    Returns
    -------
    dict[Argument, str]
        Mapping from arguments to their names (e.g., ?a, ?b, ?c, ?a1, ?b1, etc.)

    Examples
    --------
    >>> names = argument_names(list(range(100)))
    >>> [names[i] for i in range(0, 100, 26)]
    ['?a', '?a1', '?a2', '?a3']
    >>> [names[i] for i in range(1, 100, 26)]
    ['?b', '?b1', '?b2', '?b3']
    """
    # Argument naming scheme: integer -> `?[a-z]` with potentially a number if
    # there are more than 26 arguments.
    name = {}
    for i, arg in enumerate(args):
        c = i // 26 if i >= 26 else ''
        name[arg] = f'?{chr(97 + (i % 26))}{c}'
    return name


def format_predicate(
    predicate: Predicate,
    name: dict[Argument, str],
    c: Callable[[str, str], str] = no_color
) -> str:
    """Format a predicate with its arguments interpolated.

    Parameters
    ----------
    predicate : Predicate
        The predicate to format
    name : dict[Argument, str]
        Mapping from arguments to their names
    c : Callable[[str, str], str], optional
        Color function for special predicate types

    Returns
    -------
    str
        Formatted predicate string with argument placeholders
    """
    from decomp.semantics.predpatt.core.predicate import PredicateType

    ret = []
    args = predicate.arguments

    if predicate.type == PredicateType.POSS:
        return ' '.join([name[args[0]], c(PredicateType.POSS.value, 'yellow'), name[args[1]]])

    if predicate.type in {PredicateType.AMOD, PredicateType.APPOS}:
        # Special handling for `amod` and `appos` because the target
        # relation `is/are` deviates from the original word order.
        arg0 = None
        other_args = []
        for arg in args:
            if arg.root == predicate.root.gov:
                arg0 = arg
            else:
                other_args.append(arg)

        if arg0 is not None:
            ret = [name[arg0], c('is/are', 'yellow')]
            args = other_args
        else:
            ret = [name[args[0]], c('is/are', 'yellow')]
            args = args[1:]

    # Mix arguments with predicate tokens. Use word order to derive a
    # nice-looking name.
    from decomp.semantics.predpatt.utils.ud_schema import postag

    # Mix tokens and arguments, both have position attribute
    mixed_items: list[Token | Argument] = predicate.tokens + args
    sorted_items = sorted(mixed_items, key=lambda x: x.position)

    for i, y in enumerate(sorted_items):
        # Check if y is an Argument (has 'tokens' and 'root' attributes)
        if hasattr(y, 'tokens') and hasattr(y, 'root'):
            # It's an Argument - type narrowing through hasattr checks
            # Cast to Argument since we've verified it has the right attributes
            from ..core.argument import Argument
            arg_y = cast(Argument, y)
            ret.append(name[arg_y])
            if (predicate.root.gov_rel == predicate.ud.xcomp and
                predicate.root.tag not in {postag.VERB, postag.ADJ} and
                i == 0):
                ret.append(c('is/are', 'yellow'))
        else:
            # It's a Token
            ret.append(c(y.text, 'green'))

    return ' '.join(ret)


def format_predicate_instance(
    predicate: Predicate,
    track_rule: bool = False,
    c: Callable[[str, str], str] = no_color,
    indent: str = '\t'
) -> str:
    """Format a single predicate instance with its arguments.

    Parameters
    ----------
    predicate : Predicate
        The predicate instance to format
    track_rule : bool, optional
        Whether to include rule tracking information
    c : Callable[[str, str], str], optional
        Color function for output
    indent : str, optional
        Indentation string for formatting

    Returns
    -------
    str
        Formatted predicate instance with arguments listed below
    """
    from decomp.semantics.predpatt.core.predicate import PredicateType

    lines = []
    name = argument_names(predicate.arguments)

    # Format predicate
    verbose = ''
    if track_rule:
        rules_str = ','.join(sorted(map(str, predicate.rules)))
        rule = f',{rules_str}'
        verbose = c(f'{indent}[{predicate.root.text}-{predicate.root.gov_rel}{rule}]',
                    'magenta')
    lines.append(f'{indent}{format_predicate(predicate, name, c=c)}{verbose}')

    # Format arguments
    for arg in predicate.arguments:
        if (arg.isclausal() and arg.root.gov in predicate.tokens and
                predicate.type == PredicateType.NORMAL):
            s = c('SOMETHING', 'yellow') + ' := ' + arg.phrase()
        else:
            s = c(arg.phrase(), 'green')

        verbose = ''
        if track_rule:
            rules_str = ','.join(sorted(map(str, arg.rules)))
            rule = f',{rules_str}'
            verbose = c(f'{indent}[{arg.root.text}-{arg.root.gov_rel}{rule}]',
                        'magenta')
        lines.append(f'{indent * 2}{name[arg]}: {s}{verbose}')

    return '\n'.join(lines)


def pprint(
    predpatt: PredPattEngine,
    color: bool = False,
    track_rule: bool = False
) -> str:
    """Pretty-print extracted predicate-argument tuples.

    Parameters
    ----------
    predpatt : PredPatt
        The PredPatt instance containing extracted predicates
    color : bool, optional
        Whether to use colored output
    track_rule : bool, optional
        Whether to include rule tracking information

    Returns
    -------
    str
        Formatted string representation of all predicates
    """
    c = colored if color else no_color
    return '\n'.join(
        format_predicate_instance(p, track_rule=track_rule, c=c)
        for p in predpatt.instances
    )


def pprint_ud_parse(
    parse: UDParse,
    color: bool = False,
    k: int = 1
) -> str:
    """Pretty-print list of dependencies from a UDParse instance.

    Parameters
    ----------
    parse : UDParse
        The dependency parse to visualize
    color : bool, optional
        Whether to use colored output
    k : int, optional
        Number of columns for output

    Returns
    -------
    str
        Formatted dependency relations in tabular format
    """
    from tabulate import tabulate

    tokens1 = [*parse.tokens, 'ROOT']
    c = colored('/%s', 'magenta') if color else '/%s'
    e = [f'{e.rel}({tokens1[e.dep]}{c % e.dep}, {tokens1[e.gov]}{c % e.gov})'
         for e in sorted(parse.triples, key=lambda x: x.dep)]

    cols: list[list[str]] = [[] for _ in range(k)]
    for i, x in enumerate(e):
        cols[i % k].append(x)

    # add padding to columns because zip stops at shortest iterator.
    for col in cols:
        col.extend('' for _ in range(len(cols[0]) - len(col)))

    return tabulate(zip(*cols, strict=False), tablefmt='plain')
