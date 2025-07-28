"""Linearization utilities for PredPatt.

This module provides functions to convert PredPatt structures into a linearized
form that represents the predicate-argument relationships in a flat string format.
The linearization preserves hierarchical structure using special markers and can
be used for serialization, comparison, or display purposes.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from .ud_schema import dep_v1, postag


if TYPE_CHECKING:
    from ..core.argument import Argument
    from ..core.predicate import Predicate
    from ..core.token import Token

# Import constants directly to avoid circular imports
NORMAL = "normal"
POSS = "poss"
AMOD = "amod"
APPOS = "appos"

# Regex patterns for parsing linearized forms
RE_ARG_ENC = re.compile(r"\^\(\( | \)\)\$")
RE_ARG_LEFT_ENC = re.compile(r"\^\(\(")
RE_ARG_RIGHT_ENC = re.compile(r"\)\)\$")
RE_PRED_LEFT_ENC = re.compile(r"\^\(\(\(:a|\^\(\(\(")
RE_PRED_RIGHT_ENC = re.compile(r"\)\)\)\$:a|\)\)\)\$")

# Enclosure markers for different structures
ARG_ENC = ("^((", "))$")
PRED_ENC = ("^(((", ")))$")
ARGPRED_ENC = ("^(((:a", ")))$:a")

# Suffix markers for different token types
ARG_SUF = ":a"
PRED_SUF = ":p"
HEADER_SUF = "_h"
ARG_HEADER = ARG_SUF + HEADER_SUF
PRED_HEADER = PRED_SUF + HEADER_SUF

# Special marker for embedded clausal arguments
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


def sort_by_position(x: list[Any]) -> list[Any]:
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


def is_dep_of_pred(t: Token, ud: Any = dep_v1) -> bool | None:
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


def important_pred_tokens(p: Any, ud: Any = dep_v1) -> list[Any]:
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
    return sort_by_position(ret)


def likely_to_be_pred(pred: Any, ud: Any = dep_v1) -> bool | None:
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


def build_pred_dep(pp: Any) -> list[Any]:
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
    root_to_preds = {p.root.position: p for p in pp.instances}

    for p in pp.instances:
        if not hasattr(p, "children"):
            p.children = []

    id_to_root_preds = {}
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
        gov_p = root_to_preds[gov.position] if gov else None
        # Add the current predicate as a root predicate
        # if not find any gov predicate or
        # the gov predicate is not likely_to_be_pred.
        if gov is None or not likely_to_be_pred(gov_p):
            id_to_root_preds[p.identifier()] = p
            continue
        # build a dependency between the current pred and the gov pred.
        gov_p.children.append(p)
    return sort_by_position(id_to_root_preds.values())


def get_prediates(pp: Any, only_head: bool = False) -> list[str]:
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


def linearize(pp: Any, opt: LinearizedPPOpts | None = None, ud: Any = dep_v1) -> str:
    """Convert PredPatt output to linearized form.

    Here we define the way to represent the predpatt output in a linearized
    form:
        1. Add a label to each token to indicate that it is a predicate
           or argument token:
                (1) argument_token:a
                (2) predicate_token:p
        2. Build the dependency tree among the heads of predicates.
        3. Print the predpatt output in a depth-first manner. At each layer,
           items are sorted by position. There are following items:
                (1) argument_token
                (2) predicate_token
                (3) predicate that depends on token in this layer.
        4. The output of each layer is enclosed by a pair of parentheses:
                (1) Special parentheses "(:a predpatt_output ):a" are used
                    for predicates that are dependents of clausal predicate.
                (2) Normal parentheses "( predpatt_output )" are used for
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


def flatten_and_enclose_pred(pred: Any, opt: LinearizedPPOpts, ud: Any) -> str:
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
    return f'{enc[0]} {repr_y} {enc[1]}'


def flatten_pred(pred: Any, opt: LinearizedPPOpts, ud: Any) -> tuple[str, bool | None]:
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
    child_preds = pred.children if hasattr(pred, 'children') else []

    if pred.type == POSS:
        arg_i = 0
        # Only take the first two arguments into account.
        for y in sort_by_position(args[:2] + child_preds):
            if hasattr(y, 'tokens') and hasattr(y, 'root'):
                arg_i += 1
                if arg_i == 1:
                    # Generate the special ``poss'' predicate with label.
                    poss = POSS + (PRED_HEADER if opt.distinguish_header
                                     else PRED_SUF)
                    ret += [phrase_and_enclose_arg(y, opt), poss]
                else:
                    ret += [phrase_and_enclose_arg(y, opt)]
            else:
                if opt.recursive:
                    repr_y = flatten_and_enclose_pred(y, opt, ud)
                    ret.append(repr_y)
        return ' '.join(ret), False

    if pred.type in {AMOD, APPOS}:
        # Special handling for `amod` and `appos` because the target
        # relation `is/are` deviates from the original word order.
        arg0 = None
        other_args = []
        for arg in args:
            if arg.root == pred.root.gov:
                arg0 = arg
            else:
                other_args.append(arg)
        relation = 'is/are' + (PRED_HEADER if opt.distinguish_header
                               else PRED_SUF)
        if arg0 is not None:
            ret = [phrase_and_enclose_arg(arg0, opt), relation]
            args = other_args
        else:
            ret = [phrase_and_enclose_arg(args[0], opt), relation]
            args = args[1:]

    # Mix arguments with predicate tokens. Use word order to derive a
    # nice-looking name.
    items = pred.tokens + args + child_preds
    if opt.only_head:
        items = important_pred_tokens(pred, ud) + args + child_preds

    for _i, y in enumerate(sort_by_position(items)):
        if hasattr(y, 'tokens') and hasattr(y, 'root'):
            if (y.isclausal() and y.root.gov in pred.tokens):
                # In theory, "SOMETHING:a=" should be followed by a embedded
                # predicate. But in the real world, the embedded predicate
                # could be broken, which means such predicate could be empty
                # or missing. Therefore, it is necessary to add this special
                # symbol "SOMETHING:a=" to indicate that there is a embedded
                # predicate viewed as an argument of the predicate under
                # processing.
                ret.append(SOMETHING)
                ret.append(phrase_and_enclose_arg(y, opt))
            else:
                ret.append(phrase_and_enclose_arg(y, opt))
        elif hasattr(y, 'type') and hasattr(y, 'arguments'):
            if opt.recursive:
                repr_y = flatten_and_enclose_pred(y, opt, ud)
                ret.append(repr_y)
        else:
            if opt.distinguish_header and y.position == pred.root.position:
                ret.append(y.text + PRED_HEADER)
            else:
                ret.append(y.text + PRED_SUF)
    return ' '.join(ret), is_dep_of_pred(pred.root, ud)


def phrase_and_enclose_arg(arg: Any, opt: LinearizedPPOpts) -> str:
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
    repr_arg = ''
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
        repr_arg = ' '.join(ret)
    return f"{ARG_ENC[0]} {repr_arg} {ARG_ENC[1]}"


def collect_embebdded_tokens(tokens_iter: Any, start_token: str) -> list[str]:
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
    embedded_tokens = []
    for _, t in tokens_iter:
        if t == start_token:
            missing_end_token += 1
        if t == end_token:
            missing_end_token -= 1
        if missing_end_token == 0:
            return embedded_tokens
        embedded_tokens.append(t)
    # No ending bracket for the predicate.
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


def get_something(something_idx: int, tokens_iter: Any) -> Any:
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
            argument.type = SOMETHING  # type: ignore[attr-defined]
            return argument
    root = Token(something_idx, "SOMETHING", None)
    from ..utils.ud_schema import dep_v1
    arg = Argument(root, dep_v1, [])
    arg.tokens = [root]
    return arg


def is_argument_finished(t: str, current_argument: Any) -> bool:
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


def construct_arg_from_flat(tokens_iter: Any) -> Any:
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
    # Import at runtime to avoid circular imports
    from ..core.argument import Argument
    from ..core.token import Token

    empty_token = Token(-1, None, None)
    from ..utils.ud_schema import dep_v1
    argument = Argument(empty_token, dep_v1, [])
    idx = -1
    for idx, t in tokens_iter:
        if t == ARG_ENC[1]:
            if argument.root.position == -1:
                # Special case: No head is found.
                argument.position = idx
            return argument
        # add argument token
        if ARG_SUF in t:
            text, _ = t.rsplit(ARG_SUF, 1)
        else:
            # Special case: a predicate tag is given.
            text, _ = t.rsplit(":", 1)
        token = Token(idx, text, None)
        argument.tokens.append(token)
        # update argument root
        if t.endswith(ARG_HEADER):
            argument.root = token
            argument.position = token.position
    # No ending bracket for the argument.
    if argument.root.position == -1:
        # Special case: No head is found.
        argument.position = idx
    return argument


def construct_pred_from_flat(tokens: list[str]) -> list[Any]:
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
    # Construct one-layer predicates
    ret = []
    # Use this empty_token to initialize a predicate or argument.
    empty_token = Token(-1, None, None)
    # Initialize a predicate in advance, because argument or sub-level
    # predicates may come before we meet the first predicate token, and
    # they need to build connection with the predicate.
    current_predicate = Predicate(empty_token, [])
    tokens_iter = enumerate(iter(tokens))
    for idx, t in tokens_iter:
        if t  == ARG_ENC[0]:
            argument = construct_arg_from_flat(tokens_iter)
            current_predicate.arguments.append(argument)
        elif t in {PRED_ENC[0], ARGPRED_ENC[0]}:
            # Get the embedded tokens, including special tokens.
            embedded = collect_embebdded_tokens(tokens_iter, t)
            # Recursively construct sub-level predicates.
            preds = construct_pred_from_flat(embedded)
            ret += preds
        elif t == SOMETHING:
            current_predicate.arguments.append(get_something(idx, tokens_iter))
        elif t.endswith(PRED_SUF) or t.endswith(PRED_HEADER):
            # add predicate token
            text, _ = t.rsplit(PRED_SUF, 1)
            token = Token(idx, text, None)
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


def pprint_preds(preds: list[Any]) -> list[str]:
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


def argument_names(args: list[Any]) -> dict[Any, str]:
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
        c = i // 26 if i >= 26 else ''
        name[arg] = f'?{chr(97+(i % 26))}{c}'
    return name


def format_pred(pred: Any, indent: str = "\t") -> str:
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
    lines.append(f'{indent}{_format_predicate(pred, name)}')
    # Format arguments
    for arg in pred.arguments:
        s = arg.phrase()
        if hasattr(arg, "type") and arg.type == SOMETHING:
            s = "SOMETHING := " + s
        lines.append(f'{indent*2}{name[arg]}: {s}')
    return '\n'.join(lines)


def _format_predicate(pred: Any, name: dict[Any, str]) -> str:
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
    ret = []
    args = pred.arguments
    # Mix arguments with predicate tokens. Use word order to derive a
    # nice-looking name.
    for _i, y in enumerate(sort_by_position(pred.tokens + args)):
        if hasattr(y, 'tokens') and hasattr(y, 'root'):
            ret.append(name[y])
        else:
            ret.append(y.text)
    return ' '.join(ret)


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
    from ..extraction.engine import PredPattEngine as PredPatt
    from ..parsing.loader import load_conllu

    def fail(g: list[str], t: list[str]) -> bool:
        if len(g) != len(t):
            return True
        else:
            for i in g:
                if i not in t:
                    return True
        return False

    def no_color(x, _):
        return x
    count, failed = 0, 0
    ret = ""
    for _sent_id, ud_parse in load_conllu(data):
        count += 1
        pp = PredPatt(ud_parse)
        sent = ' '.join(t.text for t in pp.tokens)
        linearized_pp = linearize(pp)
        gold_preds = [predicate.format(C=no_color, track_rule=False)
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
    print(f"You have test {count} instances, and {failed} failed the test.")
