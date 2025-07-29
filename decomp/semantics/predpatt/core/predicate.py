"""Predicate class for representing extracted predicates.

This module contains the Predicate class which represents predicates
extracted from dependency parses, including their arguments and
various predicate types (normal, possessive, appositive, adjectival).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..typing import T
from ..utils.ud_schema import dep_v1, postag
from .token import Token


if TYPE_CHECKING:
    from collections.abc import Callable

    from ..rules.base import Rule
    from ..typing import UDSchema
    from .argument import Argument

    ColorFunc = Callable[[str, str], str]

# Predicate type constants
NORMAL = "normal"
POSS = "poss"
APPOS = "appos"
AMOD = "amod"


def argument_names(args: list[T]) -> dict[T, str]:
    """Give arguments alpha-numeric names.

    Parameters
    ----------
    args : list[T]
        List of arguments to name.

    Returns
    -------
    dict[T, str]
        Mapping from argument to its name (e.g., '?a', '?b', etc.).

    Examples
    --------
    >>> names = argument_names(range(100))
    >>> [names[i] for i in range(0,100,26)]
    ['?a', '?a1', '?a2', '?a3']
    >>> [names[i] for i in range(1,100,26)]
    ['?b', '?b1', '?b2', '?b3']
    """
    # argument naming scheme: integer -> `?[a-z]` with potentially a number if
    # there more than 26 arguments.
    name = {}
    for i, arg in enumerate(args):
        c = i // 26 if i >= 26 else ''
        name[arg] = f'?{chr(97+(i % 26))}{c}'
    return name


def sort_by_position(x: list[T]) -> list[T]:
    """Sort items by their position attribute."""
    return list(sorted(x, key=lambda y: y.position))


def no_color(x: str, _: str) -> str:
    """Identity function for when color is disabled."""
    return x


class Predicate:
    """Represents a predicate extracted from a dependency parse.

    A predicate consists of a root token and potentially multiple
    tokens that form the predicate phrase, along with its arguments.

    Parameters
    ----------
    root : Token
        The root token of the predicate.
    ud : module, optional
        The Universal Dependencies module to use (default: dep_v1).
    rules : list, optional
        List of rules that led to this predicate's extraction.
    type_ : str, optional
        Type of predicate (NORMAL, POSS, APPOS, or AMOD).

    Attributes
    ----------
    root : Token
        The root token of the predicate.
    rules : list
        List of extraction rules applied.
    position : int
        Position of the root token.
    ud : module
        The UD version module being used.
    arguments : list[Argument]
        List of arguments for this predicate.
    type : str
        Type of predicate.
    tokens : list[Token]
        List of tokens forming the predicate phrase.
    """

    def __init__(
        self,
        root: Token,
        ud: UDSchema = dep_v1,
        rules: list[Rule] | None = None,
        type_: str = NORMAL
    ) -> None:
        """Initialize a Predicate."""
        self.root = root
        self.rules = rules if rules is not None else []
        self.position = root.position
        self.ud = ud
        self.arguments: list[Argument] = []
        self.type = type_
        self.tokens: list[Token] = []
        self.children: list[Predicate] = []

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Predicate({self.root})"

    def copy(self) -> Predicate:
        """Only copy the complex predicate. The arguments are shared among each other.

        Returns
        -------
        Predicate
            A new predicate with shared argument references and copied tokens.
        """
        x = Predicate(self.root, self.ud, self.rules[:])
        x.arguments = [arg.reference() for arg in self.arguments]
        x.type = self.type
        x.tokens = self.tokens[:]
        return x

    def identifier(self) -> str:
        """Generate unique identifier for this predicate.

        Returns
        -------
        str
            Identifier in format 'pred.{type}.{position}.{arg_positions}'.
        """
        arg_positions = '.'.join(str(a.position) for a in self.arguments)
        return f'pred.{self.type}.{self.position}.{arg_positions}'


    def has_token(self, token: Token) -> bool:
        """Check if predicate contains a token at given position.

        Parameters
        ----------
        token : Token
            Token to check (only position is compared).

        Returns
        -------
        bool
            True if any token in predicate has same position.
        """
        return any(t.position == token.position for t in self.tokens)

    def has_subj(self) -> bool:
        """Check if predicate has a subject argument.

        Returns
        -------
        bool
            True if any argument is a subject.
        """
        return any(arg.root.gov_rel in self.ud.SUBJ for arg in self.arguments)

    def has_obj(self) -> bool:
        """Check if predicate has an object argument.

        Returns
        -------
        bool
            True if any argument is an object.
        """
        return any(arg.root.gov_rel in self.ud.OBJ for arg in self.arguments)

    def subj(self) -> Argument | None:
        """Get the subject argument if present.

        Returns
        -------
        Argument | None
            The first subject argument, or None if no subject.
        """
        for arg in self.arguments:
            if arg.root.gov_rel in self.ud.SUBJ:
                return arg
        return None

    def obj(self) -> Argument | None:
        """Get the object argument if present.

        Returns
        -------
        Argument | None
            The first object argument, or None if no object.
        """
        for arg in self.arguments:
            if arg.root.gov_rel in self.ud.OBJ:
                return arg
        return None

    def share_subj(self, other: Predicate) -> bool | None:
        """Check if two predicates share the same subject.

        Parameters
        ----------
        other : Predicate
            The other predicate to compare with.

        Returns
        -------
        bool | None
            True if both have subjects at same position,
            None if either lacks a subject.
        """
        subj = self.subj()
        other_subj = other.subj()
        # use the exact same pattern as original to ensure identical behavior
        if subj is None or other_subj is None:
            return None
        return subj.position == other_subj.position

    def has_borrowed_arg(self) -> bool:
        """Check if any argument is borrowed (shared).

        Returns
        -------
        bool
            True if any argument has share=True and has rules.
        """
        return any(arg.share for arg in self.arguments for r in arg.rules)

    def phrase(self) -> str:
        """Get the predicate phrase with argument placeholders.

        Returns
        -------
        str
            The formatted predicate phrase.
        """
        return self._format_predicate(argument_names(self.arguments))

    def is_broken(self) -> bool | None:
        """Check if predicate is malformed.

        Returns
        -------
        bool | None
            True if broken, None if valid.
        """
        if not self.tokens:
            return True
        if any(not a.tokens for a in self.arguments):
            return True
        if self.type == POSS and len(self.arguments) != 2:
            return True
        return None

    def _format_predicate(self, name: dict[Argument, str], c: ColorFunc = no_color) -> str:  # noqa: C901
        """Format predicate with argument placeholders.

        Parameters
        ----------
        name : dict[Argument, str]
            Mapping from arguments to their names.
        c : callable, optional
            Color function for formatting.

        Returns
        -------
        str
            Formatted predicate string.
        """
        # collect tokens and arguments
        x = sort_by_position(self.tokens + self.arguments)

        if self.type == POSS:
            # possessive format: "?a 's ?b"
            assert len(self.arguments) == 2
            return f'{name[self.arguments[0]]} {self.type} {name[self.arguments[1]]}'

        elif self.type in {APPOS, AMOD}:
            # appositive/adjectival format: "?a is/are [rest]"
            # find governor argument
            gov_arg = None
            for a in self.arguments:
                if a.root == self.root.gov:
                    gov_arg = a
                    break

            if gov_arg:
                # format: gov_arg is/are other_tokens_and_args
                rest = []
                for item in x:
                    if item == gov_arg:
                        continue
                    if item in self.arguments:
                        rest.append(name[item])  # type: ignore[index]  # item is Argument when in self.arguments
                    else:
                        rest.append(item.text)  # type: ignore[union-attr]  # item is Token when not in self.arguments
                rest_str = ' '.join(rest)
                return f'{name[gov_arg]} is/are {rest_str}'
            else:
                # fallback if no governor argument found
                return ' '.join(name[item] if item in self.arguments else item.text for item in x)  # type: ignore[index,union-attr]

        else:
            # normal predicate or xcomp special case
            result = []

            # check for xcomp with non-VERB/ADJ
            if (self.root.gov_rel == self.ud.xcomp and
                self.root.tag not in {postag.VERB, postag.ADJ}):
                # add is/are after first argument
                first_arg_added = False
                for item in x:
                    if item in self.arguments:
                        result.append(name[item])  # type: ignore[index]  # item is Argument when in self.arguments
                        if not first_arg_added:
                            result.append('is/are')
                            first_arg_added = True
                    else:
                        result.append(item.text)  # type: ignore[union-attr]  # item is Token when not in self.arguments
            else:
                # normal formatting
                for item in x:
                    if item in self.arguments:
                        result.append(name[item])  # type: ignore[index]  # item is Argument when in self.arguments
                    else:
                        result.append(item.text)  # type: ignore[union-attr]  # item is Token when not in self.arguments

            return ' '.join(result)

    def format(
        self,
        track_rule: bool = False,
        c: ColorFunc = no_color,
        indent: str = '\t'
    ) -> str:
        """Format predicate with arguments for display.

        Parameters
        ----------
        track_rule : bool, optional
            Whether to include rule tracking information.
        c : callable, optional
            Color function for formatting.
        indent : str, optional
            Indentation string to use.

        Returns
        -------
        str
            Formatted predicate with arguments.
        """
        # format predicate line
        lines = []
        verbose = ''
        if track_rule:
            rules_str = ','.join(sorted(map(str, self.rules)))
            verbose = ' ' + c(f'[{self.root.text}-{self.root.gov_rel},{rules_str}]', 'magenta')

        pred_str = self._format_predicate(argument_names(self.arguments), c)
        lines.append(f'{indent}{pred_str}{verbose}')

        # format arguments
        name = argument_names(self.arguments)
        for arg in self.arguments:
            if (arg.isclausal() and arg.root.gov in self.tokens and
                    self.type == NORMAL):
                s = c('SOMETHING', 'yellow') + ' := ' + arg.phrase()
            else:
                s = c(arg.phrase(), 'green')
            rule = ''
            if track_rule:
                rules_str = ','.join(sorted(map(str, arg.rules)))
                rule = f',{rules_str}'
                verbose = c(f' [{arg.root.text}-{arg.root.gov_rel}{rule}]',
                            'magenta')
            else:
                verbose = ''
            lines.append(f'{indent*2}{name[arg]}: {s}{verbose}')

        return '\n'.join(lines)
