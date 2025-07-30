"""Base rule classes for PredPatt extraction system.

This module defines the abstract base classes for all rules used in PredPatt.
Rules track the logic behind extraction decisions and provide explanations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..core.token import Token


class Rule:
    """Abstract base class for all PredPatt rules.

    Rules are used to track extraction logic and provide explanations
    for why certain tokens were identified as predicates or arguments.
    """

    def __init__(self) -> None:
        """Initialize rule instance."""
        pass

    def __repr__(self) -> str:
        """Return string representation of the rule.

        Returns
        -------
        str
            The rule's name by default.
        """
        return self.name()

    @classmethod
    def name(cls) -> str:
        """Get the rule's name.

        Returns
        -------
        str
            The class name without module prefix, converted to lowercase
            for backward compatibility with expected outputs.
        """
        # convert PascalCase to lowercase/snake_case for output compatibility
        name = cls.__name__.split('.')[-1]

        # base classes keep their PascalCase names
        base_classes = {
            'Rule', 'PredicateRootRule', 'ArgumentRootRule', 'PredConjRule',
            'ArgumentResolution', 'ConjunctionResolution', 'SimplifyRule',
            'PredPhraseRule', 'ArgPhraseRule', 'LanguageSpecific', 'EnglishSpecific'
        }
        if name in base_classes:
            return name

        # handle RuleI -> i special case
        if name == 'RuleI':
            return 'i'

        # handle single letter rules (A1 -> a1, G1 -> g1, etc.)
        if len(name) <= 2 and name[0].isupper():
            return name.lower()

        # handle PascalCase rules (PredConjBorrowAuxNeg -> pred_conj_borrow_aux_neg)
        # insert underscore before uppercase letters
        result = []
        for i, char in enumerate(name):
            if i > 0 and char.isupper() and (i == 0 or not name[i-1].isupper()):
                result.append('_')
            result.append(char.lower())

        return ''.join(result)

    @classmethod
    def explain(cls) -> str:
        """Get explanation of what this rule does.

        Returns
        -------
        str
            The rule's docstring explaining its purpose.
        """
        return cls.__doc__ or ""

    def __eq__(self, other: object) -> bool:
        """Compare rules for equality.

        Parameters
        ----------
        other : object
            Another object to compare with.

        Returns
        -------
        bool
            True if rules are of the same type.
        """
        return isinstance(other, self.__class__)

    def __hash__(self) -> int:
        """Get hash of rule for use in sets/dicts.

        Returns
        -------
        int
            Hash based on class name.
        """
        return hash(self.__class__.__name__)


class PredicateRootRule(Rule):
    """Base class for rules that identify predicate root tokens.

    These rules are applied during the predicate extraction phase
    to identify which tokens should be considered predicate roots.
    """

    rule_type: str = 'predicate_root'


class ArgumentRootRule(Rule):
    """Base class for rules that identify argument root tokens.

    These rules are applied during the argument extraction phase
    to identify which tokens should be considered argument roots.
    """

    rule_type: str = 'argument_root'


class PredConjRule(Rule):
    """Base class for rules handling predicate conjunctions.

    These rules manage how conjoined predicates share or borrow
    elements like auxiliaries and negations.
    """

    type: str = 'predicate_conj'


class ArgumentResolution(Rule):
    """Base class for rules that resolve missing or borrowed arguments.

    These rules handle cases where predicates need to borrow arguments
    from other predicates or resolve missing arguments.
    """

    type: str = 'argument_resolution'


class ConjunctionResolution(Rule):
    """Base class for rules handling argument conjunctions.

    These rules manage how conjoined arguments are processed
    and expanded.
    """

    type: str = 'conjunction_resolution'


class SimplifyRule(Rule):
    """Base class for rules that simplify patterns.

    These rules are applied when options.simple=True to create
    simpler predicate-argument patterns.
    """

    type: str = 'simple'


class PredPhraseRule(Rule):
    """Base class for rules that build predicate phrases.

    These rules determine which tokens from the dependency subtree
    should be included in the predicate phrase.
    """

    type: str = 'pred_phrase'

    def __init__(self, x: Token) -> None:
        """Initialize with the token being processed.

        Parameters
        ----------
        x : Token
            The token being considered for the predicate phrase.
        """
        self.x = x
        super().__init__()


class ArgPhraseRule(Rule):
    """Base class for rules that build argument phrases.

    These rules determine which tokens from the dependency subtree
    should be included in the argument phrase.
    """

    type: str = 'arg_phrase'


class LanguageSpecific(Rule):
    """Base class for language-specific rules.

    These rules apply only to specific languages and handle
    language-specific phenomena.
    """

    lang: str | None = None


class EnglishSpecific(LanguageSpecific):
    """Base class for English-specific rules.

    These rules handle English-specific phenomena like possessives
    and certain syntactic constructions.
    """

    lang: str = 'English'
