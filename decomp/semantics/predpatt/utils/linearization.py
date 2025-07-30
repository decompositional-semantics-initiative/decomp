"""Linearization utilities for PredPatt.

This module provides functions to convert PredPatt structures into a linearized
form that represents the predicate-argument relationships in a flat string format.
The linearization preserves hierarchical structure using special markers and can
be used for serialization, comparison, or display purposes.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, cast

from decomp.semantics.predpatt.utils.ud_schema import dep_v1, postag


if TYPE_CHECKING:
    from collections.abc import Iterator

    from decomp.semantics.predpatt.core.argument import Argument
    from decomp.semantics.predpatt.core.predicate import Predicate, PredicateType
    from decomp.semantics.predpatt.core.token import Token
    from decomp.semantics.predpatt.extraction.engine import PredPattEngine
    from decomp.semantics.predpatt.typing import HasPosition, T
    from decomp.semantics.predpatt.utils.ud_schema import (
        DependencyRelationsV1,
        DependencyRelationsV2,
    )

    UDSchema = type[DependencyRelationsV1] | type[DependencyRelationsV2]
    TokenIterator = Iterator[tuple[int, str]]
else:
    # import at runtime to avoid circular imports
    from decomp.semantics.predpatt.core.predicate import PredicateType
    from decomp.semantics.predpatt.typing import HasPosition, T


class HasChildren(HasPosition):
    """Protocol for objects that can have children list."""

    children: list[Predicate]


# regex patterns for parsing linearized forms
RE_ARG_ENC = re.compile(r"\^\(\( | \)\)\$")
RE_ARG_LEFT_ENC = re.compile(r"\^\(\(")
RE_ARG_RIGHT_ENC = re.compile(r"\)\)\$")
RE_PRED_LEFT_ENC = re.compile(r"\^\(\(\(:a|\^\(\(\(")
RE_PRED_RIGHT_ENC = re.compile(r"\)\)\)\$:a|\)\)\)\$")

# enclosure markers for different structures
ARG_ENC = ("^((", "))$")
PRED_ENC = ("^(((", ")))$")
ARGPRED_ENC = ("^(((:a", ")))$:a")

# suffix markers for different token types
ARG_SUF = ":a"
PRED_SUF = ":p"
HEADER_SUF = "_h"
ARG_HEADER = ARG_SUF + HEADER_SUF
PRED_HEADER = PRED_SUF + HEADER_SUF

# special marker for embedded clausal arguments
SOMETHING = "SOMETHING:a="


class LinearizedPPOpts:
    """Options for linearization of PredPatt structures.

    Parameters
    ----------
    recursive : bool, optional
        Whether to recursively linearize embedded predicates (default: True).
    distinguish_header : bool, optional
        Whether to distinguish predicate/argument heads with special suffix (default: True).
    only_head : bool, optional
        Whether to include only head tokens instead of full phrases (default: False).
    """

    def __init__(
        self,
        recursive: bool = True,
        distinguish_header: bool = True,
        only_head: bool = False,
    ) -> None:
        self.recursive = recursive
        self.distinguish_header = distinguish_header
        self.only_head = only_head


def sort_by_position(x: list[T]) -> list[T]:
    """Sort items by their position attribute.

    Parameters
    ----------
    x : list[Any]
        List of items with position attribute.

    Returns
    -------
    list[Any]
        Sorted list by position.
    """
    return list(sorted(x, key=lambda y: y.position))


def is_dep_of_pred(t: Token, ud: UDSchema = dep_v1) -> bool | None:
    """Check if token is a dependent of a predicate.

    Parameters
    ----------
    t : Token
        Token to check.
    ud : module, optional
        Universal Dependencies module (default: dep_v1).

    Returns
    -------
    bool | None
        True if token is predicate dependent, None otherwise.
    """
    if t.gov_rel in {ud.nsubj, ud.nsubjpass, ud.dobj, ud.iobj,
                     ud.csubj, ud.csubjpass, ud.ccomp, ud.xcomp,
                     ud.nmod, ud.advcl, ud.advmod, ud.neg}:
        return True
    return None


def important_pred_tokens(p: Predicate, ud: UDSchema = dep_v1) -> list[Token]:
    """Get important tokens from a predicate (root and negation).

    Parameters
    ----------
    p : Predicate
        The predicate to extract tokens from.
    ud : module, optional
        Universal Dependencies module (default: dep_v1).

    Returns
    -------
    list[Token]
        List of important tokens sorted by position.
    """
    ret = [p.root]
    for x in p.tokens:
        # direct dependents of the predicate
        if x.gov and x.gov.position == p.root.position and x.gov_rel in {ud.neg}:
            ret.append(x)
    return sorted(ret, key=lambda x: x.position)


def likely_to_be_pred(pred: Predicate, ud: UDSchema = dep_v1) -> bool | None:
    """Check if a predicate is likely to be a true predicate.

    Parameters
    ----------
    pred : Predicate
        The predicate to check.
    ud : module, optional
        Universal Dependencies module (default: dep_v1).

    Returns
    -------
    bool | None
        True if likely to be predicate, None otherwise.
    """
    if len(pred.arguments) == 0:
        return False
    if pred.root.tag in {postag.VERB, postag.ADJ}:
        return True
    if pred.root.gov_rel in {ud.appos}:
        return True
    for t in pred.tokens:
        if t.gov_rel == ud.cop:
            return True
    return None


def build_pred_dep(pp: PredPattEngine) -> list[Predicate]:
    """Build dependencies between predicates.

    Parameters
    ----------
    pp : PredPatt
        The PredPatt instance containing predicates.

    Returns
    -------
    list[Predicate]
        List of root predicates sorted by position.
    """
    root_to_preds: dict[int, Predicate] = {p.root.position: p for p in pp.instances}

    for p in pp.instances:
        if not hasattr(p, "children"):
            p.children = []

    id_to_root_preds: dict[str, Predicate] = {}
    for p in pp.instances:
        # only keep predicates with high confidence
        if not likely_to_be_pred(p):
            continue
        gov = p.root.gov
        # record the current predicate as a root predicate
        if gov is None:
            id_to_root_preds[p.identifier()] = p
        # climb up until finding a gov predicate
        while gov is not None and gov.position not in root_to_preds:
            gov = gov.gov
        gov_p: Predicate | None = root_to_preds[gov.position] if gov else None
        # Add the current predicate as a root predicate
        # if not find any gov predicate or
        # the gov predicate is not likely_to_be_pred.
        if gov is None or gov_p is None or not likely_to_be_pred(gov_p):
            id_to_root_preds[p.identifier()] = p
            continue
        # build a dependency between the current pred and the gov pred.
        gov_p.children.append(p)
    return sort_by_position(list(id_to_root_preds.values()))


def get_prediates(pp: PredPattEngine, only_head: bool = False) -> list[str]:
    """Get predicates as formatted strings.

    Parameters
    ----------
    pp : PredPatt
        The PredPatt instance.
    only_head : bool, optional
        Whether to return only head tokens (default: False).

    Returns
    -------
    list[str]
        List of formatted predicate strings.
    """
    idx_list = []
    preds = []
    for pred in pp.instances:
        if pred.root.position not in idx_list:
            idx_list.append(pred.root.position)
            preds.append(pred)
    if only_head:
        return [pred.root.text for pred in sort_by_position(preds)]
    else:
        enc = PRED_ENC
        ret = []
        for pred in preds:
            pred_str = pred.phrase()    # " ".join(token.text for token in pred.tokens)
            ret.append(f"{enc[0]} {pred_str} {enc[1]}")
        return ret


def linearize(
    pp: PredPattEngine,
    opt: LinearizedPPOpts | None = None,
    ud: UDSchema = dep_v1,
) -> str:
    """Convert PredPatt output to linearized form.

    Here we define the way to represent the predpatt output in a linearized
    form:

    1. Add a label to each token to indicate that it is a predicate
       or argument token:

       - argument_token:a
       - predicate_token:p

    2. Build the dependency tree among the heads of predicates.

    3. Print the predpatt output in a depth-first manner. At each layer,
       items are sorted by position. There are following items:

       - argument_token
       - predicate_token
       - predicate that depends on token in this layer

    4. The output of each layer is enclosed by a pair of parentheses:

       - Special parentheses "(:a predpatt_output ):a" are used
         for predicates that are dependents of clausal predicate.
       - Normal parentheses "( predpatt_output )" are used for
         for predicates that are noun dependents.

    Parameters
    ----------
    pp : PredPatt
        The PredPatt instance to linearize.
    opt : LinearizedPPOpts, optional
        Linearization options (default: LinearizedPPOpts()).
    ud : module, optional
        Universal Dependencies module (default: dep_v1).

    Returns
    -------
    str
        Linearized representation of the PredPatt structure.
    """
    if opt is None:
        opt = LinearizedPPOpts()

    ret = []
    roots = build_pred_dep(pp)
    for root in roots:
        repr_root = flatten_and_enclose_pred(root, opt, ud)
        ret.append(repr_root)
    return " ".join(ret)


def flatten_and_enclose_pred(pred: Predicate, opt: LinearizedPPOpts, ud: UDSchema) -> str:
    """Flatten and enclose a predicate with appropriate markers.

    Parameters
    ----------
    pred : Predicate
        The predicate to flatten.
    opt : LinearizedPPOpts
        Linearization options.
    ud : module
        Universal Dependencies module.

    Returns
    -------
    str
        Flattened and enclosed predicate string.
    """
    repr_y, is_argument = flatten_pred(pred, opt, ud)
    enc = PRED_ENC
    if is_argument:
        enc = ARGPRED_ENC
    return f"{enc[0]} {repr_y} {enc[1]}"


def flatten_pred(pred: Predicate, opt: LinearizedPPOpts, ud: UDSchema) -> tuple[str, bool | None]:  # noqa: C901
    """Flatten a predicate into a string representation.

    Parameters
    ----------
    pred : Predicate
        The predicate to flatten.
    opt : LinearizedPPOpts
        Linearization options.
    ud : module
        Universal Dependencies module.

    Returns
    -------
    tuple[str, bool | None]
        Flattened string and whether it's a dependent of predicate.
    """
    ret = []
    args = pred.arguments
    child_preds = pred.children if hasattr(pred, "children") else []

    if pred.type == PredicateType.POSS:
        arg_i = 0
        # only take the first two arguments into account.
        for y in sort_by_position(args[:2] + child_preds):
            if hasattr(y, "tokens") and hasattr(y, "root"):
                # type narrow y to Argument
                arg_y = cast(Argument, y)
                arg_i += 1
                if arg_i == 1:
                    # generate the special ``poss'' predicate with label.
                    poss = PredicateType.POSS.value + (PRED_HEADER if opt.distinguish_header
                                     else PRED_SUF)
                    ret += [phrase_and_enclose_arg(arg_y, opt), poss]
                else:
                    ret += [phrase_and_enclose_arg(arg_y, opt)]
            else:
                # y must be a Predicate if it doesn't have tokens and root
                pred_y = cast(Predicate, y)
                if opt.recursive:
                    repr_y = flatten_and_enclose_pred(pred_y, opt, ud)
                    ret.append(repr_y)
        return " ".join(ret), False

    if pred.type in {PredicateType.AMOD, PredicateType.APPOS}:
        # special handling for `amod` and `appos` because the target
        # relation `is/are` deviates from the original word order.
        arg0 = None
        other_args = []
        for arg in args:
            if arg.root == pred.root.gov:
                arg0 = arg
            else:
                other_args.append(arg)
        relation = "is/are" + (PRED_HEADER if opt.distinguish_header
                               else PRED_SUF)
        if arg0 is not None:
            ret = [phrase_and_enclose_arg(arg0, opt), relation]
            args = other_args
        else:
            ret = [phrase_and_enclose_arg(args[0], opt), relation]
            args = args[1:]

    # mix arguments with predicate tokens. Use word order to derive a
    # nice-looking name.
    items: list[Token | Argument | Predicate] = pred.tokens + args + child_preds
    if opt.only_head:
        items = important_pred_tokens(pred, ud) + args + child_preds

    sorted_mixed = sorted(items, key=lambda x: x.position)
    for _i, elem in enumerate(sorted_mixed):
        if hasattr(elem, "tokens") and hasattr(elem, "root"):
            # type narrow elem to Argument
            arg_elem = cast(Argument, elem)
            if (arg_elem.isclausal() and arg_elem.root.gov in pred.tokens):
                # in theory, "SOMETHING:a=" should be followed by a embedded
                # predicate. but in the real world, the embedded predicate
                # could be broken, which means such predicate could be empty
                # or missing. therefore, it is necessary to add this special
                # symbol "SOMETHING:a=" to indicate that there is a embedded
                # predicate viewed as an argument of the predicate under
                # processing.
                ret.append(SOMETHING)
                ret.append(phrase_and_enclose_arg(arg_elem, opt))
            else:
                ret.append(phrase_and_enclose_arg(arg_elem, opt))
        elif hasattr(elem, "type") and hasattr(elem, "arguments"):
            # elem must be a Predicate if it has type and arguments
            pred_elem = cast(Predicate, elem)
            if opt.recursive:
                repr_elem = flatten_and_enclose_pred(pred_elem, opt, ud)
                ret.append(repr_elem)
        else:
            # elem must be a Token
            token_elem = elem
            if opt.distinguish_header and token_elem.position == pred.root.position:
                ret.append(token_elem.text + PRED_HEADER)
            else:
                ret.append(token_elem.text + PRED_SUF)
    return " ".join(ret), is_dep_of_pred(pred.root, ud)


def phrase_and_enclose_arg(arg: Argument, opt: LinearizedPPOpts) -> str:
    """Format and enclose an argument with markers.

    Parameters
    ----------
    arg : Argument
        The argument to format.
    opt : LinearizedPPOpts
        Linearization options.

    Returns
    -------
    str
        Formatted and enclosed argument string.
    """
    repr_arg = ""
    if opt.only_head:
        root_text = arg.root.text
        repr_arg = root_text + ARG_HEADER if opt.distinguish_header else root_text + ARG_SUF
    else:
        ret = []
        for x in arg.tokens:
            if opt.distinguish_header and x.position == arg.root.position:
                ret.append(x.text + ARG_HEADER)
            else:
                ret.append(x.text + ARG_SUF)
        repr_arg = " ".join(ret)
    return f"{ARG_ENC[0]} {repr_arg} {ARG_ENC[1]}"


def collect_embebdded_tokens(tokens_iter: TokenIterator, start_token: str) -> list[str]:
    """Collect tokens within embedded structure markers.

    Parameters
    ----------
    tokens_iter : iterator
        Iterator over (index, token) pairs.
    start_token : str
        The starting token marker.

    Returns
    -------
    list[str]
        List of embedded tokens.
    """
    end_token = PRED_ENC[1] if start_token == PRED_ENC[0] else ARGPRED_ENC[1]

    missing_end_token = 1
    embedded_tokens: list[str] = []
    for _, t in tokens_iter:
        if t == start_token:
            missing_end_token += 1
        if t == end_token:
            missing_end_token -= 1
        if missing_end_token == 0:
            return embedded_tokens
        embedded_tokens.append(t)
    # no ending bracket for the predicate.
    return embedded_tokens


def linear_to_string(tokens: list[str]) -> list[str]:
    """Convert linearized tokens back to plain text.

    Parameters
    ----------
    tokens : list[str]
        List of linearized tokens.

    Returns
    -------
    list[str]
        List of plain text tokens.
    """
    ret = []
    for t in tokens:
        if t in PRED_ENC or t in ARG_ENC or t in ARGPRED_ENC or t == SOMETHING or ":" not in t:
            continue
        else:
            ret.append(t.rsplit(":", 1)[0])
    return ret


def get_something(something_idx: int, tokens_iter: TokenIterator) -> Argument:
    """Get SOMETHING argument from token iterator.

    Parameters
    ----------
    something_idx : int
        Index of SOMETHING token.
    tokens_iter : iterator
        Iterator over (index, token) pairs.

    Returns
    -------
    Argument
        The SOMETHING argument.
    """
    for _idx, t in tokens_iter:
        if t  == ARG_ENC[0]:
            argument = construct_arg_from_flat(tokens_iter)
            argument.type = SOMETHING
            return argument
    root = Token(something_idx, "SOMETHING", "")
    from decomp.semantics.predpatt.utils.ud_schema import dep_v1
    arg = Argument(root, dep_v1, [])
    arg.tokens = [root]
    return arg


def is_argument_finished(t: str, current_argument: Argument) -> bool:
    """Check if argument construction is finished.

    Parameters
    ----------
    t : str
        Current token.
    current_argument : Argument
        Argument being constructed.

    Returns
    -------
    bool
        True if argument is finished.
    """
    if current_argument.position != -1:
        # only one head is allowed.
        if t.endswith(ARG_SUF):
            return False
    else:
        if t.endswith(ARG_SUF) or t.endswith(ARG_HEADER):
            return False
    return True


def construct_arg_from_flat(tokens_iter: TokenIterator) -> Argument:
    """Construct an argument from flat token iterator.

    Parameters
    ----------
    tokens_iter : iterator
        Iterator over (index, token) pairs.

    Returns
    -------
    Argument
        Constructed argument.
    """
    # import at runtime to avoid circular imports
    from decomp.semantics.predpatt.core.argument import Argument
    from decomp.semantics.predpatt.core.token import Token

    empty_token = Token(-1, "", "")
    from decomp.semantics.predpatt.utils.ud_schema import dep_v1
    argument = Argument(empty_token, dep_v1, [])
    idx = -1
    for idx, t in tokens_iter:
        if t == ARG_ENC[1]:
            if argument.root.position == -1:
                # special case: no head is found.
                argument.position = idx
            return argument
        # add argument token
        if ARG_SUF in t:
            text, _ = t.rsplit(ARG_SUF, 1)
        else:
            # special case: a predicate tag is given.
            text, _ = t.rsplit(":", 1)
        token = Token(idx, text, "")
        argument.tokens.append(token)
        # update argument root
        if t.endswith(ARG_HEADER):
            argument.root = token
            argument.position = token.position
    # no ending bracket for the argument.
    if argument.root.position == -1:
        # Special case: No head is found.
        argument.position = idx
    return argument


def construct_pred_from_flat(tokens: list[str]) -> list[Predicate]:
    """Construct predicates from flat token list.

    Parameters
    ----------
    tokens : list[str]
        List of tokens to parse.

    Returns
    -------
    list[Predicate]
        List of constructed predicates.
    """
    if tokens is None or len(tokens) == 0:
        return []
    # construct one-layer predicates
    ret = []
    # use this empty_token to initialize a predicate or argument.
    empty_token = Token(-1, "", "")
    # initialize a predicate in advance, because argument or sub-level
    # predicates may come before we meet the first predicate token, and
    # they need to build connection with the predicate.
    current_predicate = Predicate(empty_token)
    tokens_iter = enumerate(iter(tokens))
    for idx, t in tokens_iter:
        if t  == ARG_ENC[0]:
            argument = construct_arg_from_flat(tokens_iter)
            current_predicate.arguments.append(argument)
        elif t in {PRED_ENC[0], ARGPRED_ENC[0]}:
            # get the embedded tokens, including special tokens.
            embedded = collect_embebdded_tokens(tokens_iter, t)
            # recursively construct sub-level predicates.
            preds = construct_pred_from_flat(embedded)
            ret += preds
        elif t == SOMETHING:
            current_predicate.arguments.append(get_something(idx, tokens_iter))
        elif t.endswith(PRED_SUF) or t.endswith(PRED_HEADER):
            # add predicate token
            text, _ = t.rsplit(PRED_SUF, 1)
            token = Token(idx, text, "")
            current_predicate.tokens.append(token)
            # update predicate root
            if t.endswith(PRED_HEADER):
                current_predicate.root = token
                ret += [current_predicate]
        else:
            continue
    return ret


def check_recoverability(tokens: list[str]) -> tuple[bool, list[str]]:
    """Check if linearized tokens can be recovered to predicates.

    Parameters
    ----------
    tokens : list[str]
        List of tokens to check.

    Returns
    -------
    tuple[bool, list[str]]
        Whether tokens are recoverable and the token list.
    """
    def encloses_allowed() -> bool:
        return (counter["arg_left"] >= counter["arg_right"] and
                counter["pred_left"] >= counter["pred_right"] and
                counter["argpred_left"] >= counter["argpred_right"])

    def encloses_matched() -> bool:
        return (counter["arg_left"] == counter["arg_right"] and
                counter["pred_left"] == counter["pred_right"] and
                counter["argpred_left"] == counter["argpred_right"])


    encloses = {"arg_left": ARG_ENC[0], "arg_right": ARG_ENC[1],
                "pred_left": PRED_ENC[0], "pred_right": PRED_ENC[1],
                "argpred_left": ARGPRED_ENC[0], "argpred_right": ARGPRED_ENC[1]}
    sym2name = {y: x for x, y in encloses.items()}
    counter = {x: 0 for x in encloses}
    # check the first enclose
    if tokens[0] not in {encloses["pred_left"], encloses["argpred_left"]}:
        return False, tokens
    # check the last enclose
    if tokens[-1] not in {encloses["pred_right"], encloses["argpred_right"]}:
        return False, tokens
    for t in tokens:
        if t in sym2name:
            counter[sym2name[t]] += 1
            if not encloses_allowed():
                return False, tokens
    return encloses_matched(), tokens


def pprint_preds(preds: list[Predicate]) -> list[str]:
    """Pretty print list of predicates.

    Parameters
    ----------
    preds : list[Predicate]
        List of predicates to format.

    Returns
    -------
    list[str]
        List of formatted predicate strings.
    """
    return [format_pred(p) for p in preds]


def argument_names(args: list[Argument]) -> dict[Argument, str]:
    """Give arguments alpha-numeric names.

    Examples
    --------
    >>> names = argument_names(range(100))
    >>> [names[i] for i in range(0,100,26)]
    ['?a', '?a1', '?a2', '?a3']
    >>> [names[i] for i in range(1,100,26)]
    ['?b', '?b1', '?b2', '?b3']

    Parameters
    ----------
    args : list[Any]
        List of arguments to name.

    Returns
    -------
    dict[Any, str]
        Mapping from argument to its name.
    """
    # argument naming scheme: integer -> `?[a-z]` with potentially a number if
    # there more than 26 arguments.
    name = {}
    for i, arg in enumerate(args):
        c = i // 26 if i >= 26 else ""
        name[arg] = f"?{chr(97+(i % 26))}{c}"
    return name


def format_pred(pred: Predicate, indent: str = "\t") -> str:
    r"""Format a predicate for display.

    Parameters
    ----------
    pred : Predicate
        The predicate to format.
    indent : str, optional
        Indentation string (default: "\t").

    Returns
    -------
    str
        Formatted predicate string.
    """
    lines = []
    name = argument_names(pred.arguments)
    # Format predicate
    lines.append(f"{indent}{_format_predicate(pred, name)}")
    # Format arguments
    for arg in pred.arguments:
        s = arg.phrase()
        if hasattr(arg, "type") and arg.type == SOMETHING:
            s = "SOMETHING := " + s
        lines.append(f"{indent*2}{name[arg]}: {s}")
    return "\n".join(lines)


def _format_predicate(pred: Predicate, name: dict[Argument, str]) -> str:
    """Format predicate with argument placeholders.

    Parameters
    ----------
    pred : Predicate
        The predicate to format.
    name : dict[Any, str]
        Mapping from arguments to names.

    Returns
    -------
    str
        Formatted predicate string.
    """
    ret: list[str] = []
    args: list[Argument] = pred.arguments
    # mix arguments with predicate tokens. Use word order to derive a
    # nice-looking name.
    mixed_items: list[Token | Argument] = pred.tokens + args
    for _i, y in enumerate(sort_by_position(mixed_items)):
        if hasattr(y, "tokens") and hasattr(y, "root"):
            # it's an Argument
            assert isinstance(y, Argument)
            ret.append(name[y])
        else:
            # it's a Token
            assert hasattr(y, "text")
            ret.append(y.text)
    return " ".join(ret)


def pprint(s: str) -> str:
    """Pretty print linearized string with readable brackets.

    Parameters
    ----------
    s : str
        Linearized string to pretty print.

    Returns
    -------
    str
        Pretty printed string with brackets.
    """
    return re.sub(RE_ARG_RIGHT_ENC, ")",
                  re.sub(RE_ARG_LEFT_ENC, "(",
                         re.sub(RE_PRED_LEFT_ENC, "[",
                                re.sub(RE_PRED_RIGHT_ENC, "]", s))))


def test(data: str) -> None:
    """Test linearization functionality.

    Parameters
    ----------
    data : str
        Path to test data file.
    """
    from decomp.semantics.predpatt.extraction.engine import PredPattEngine as PredPatt
    from decomp.semantics.predpatt.parsing.loader import load_conllu

    def fail(g: list[str], t: list[str]) -> bool:
        if len(g) != len(t):
            return True
        return any(i not in t for i in g)

    def no_color(x: str, _: str) -> str:
        return x
    count, failed = 0, 0
    ret = ""
    for _sent_id, ud_parse in load_conllu(data):
        count += 1
        pp = PredPatt(ud_parse)
        sent = " ".join((t if isinstance(t, str) else t.text) for t in pp.tokens)
        linearized_pp = linearize(pp)
        gold_preds = [predicate.format(c=no_color, track_rule=False)
                for predicate in pp.instances if likely_to_be_pred(predicate)]
        test_preds = pprint_preds(construct_pred_from_flat(linearized_pp.split()))
        if fail(gold_preds, test_preds):
            failed += 1
            gold_str = "\n".join(gold_preds)
            test_str = "\n".join(test_preds)
            ret += (
                f"Sent: {sent}\n"
                f"Linearized PredPatt:\n\t{linearized_pp}\n"
                f"Gold:\n{gold_str}\n"
                f"Yours:\n{test_str}\n\n"
            )
    print(ret)
    print(f"you have test {count} instances, and {failed} failed the test.")
