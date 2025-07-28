"""Main extraction engine for PredPatt predicate-argument extraction.

This module contains the PredPattEngine class which is responsible for orchestrating
the entire predicate-argument extraction pipeline from Universal Dependencies parses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..core.options import PredPattOpts
from ..utils.ud_schema import dep_v1, dep_v2, postag


if TYPE_CHECKING:
    from ..core.predicate import Predicate
    from ..parsing.udparse import UDParse

# predicate type constants
NORMAL, POSS, APPOS, AMOD = ("normal", "poss", "appos", "amod")


_PARSER = None


def gov_looks_like_predicate(e, ud):
    """Check if e.gov looks like a predicate because it has potential arguments.

    Parameters
    ----------
    e : DepTriple
        The dependency edge to check.
    ud : object
        Universal Dependencies schema object.

    Returns
    -------
    bool
        True if the governor looks like a predicate based on its arguments.
    """
    # if e.gov "looks like" a predicate because it has potential arguments
    if e.gov.tag in {postag.VERB} and e.rel in {
            ud.nmod, ud.nmod_npmod, ud.obl, ud.obl_npmod}:
        return True
    return e.rel in {ud.nsubj, ud.nsubjpass, ud.csubj, ud.csubjpass,
                     ud.dobj, ud.iobj,
                     ud.ccomp, ud.xcomp, ud.advcl}


def sort_by_position(x):
    """Sort objects by their position attribute.

    Parameters
    ----------
    x : list
        List of objects with position attributes.

    Returns
    -------
    list
        Sorted list ordered by position.
    """
    return list(sorted(x, key=lambda y: y.position))


def convert_parse(parse: UDParse, ud) -> UDParse:
    """Convert dependency parse on integers into a dependency parse on Tokens.

    Parameters
    ----------
    parse : UDParse
        The parse to convert with integer-based dependencies.
    ud : object
        Universal Dependencies schema object (dep_v1 or dep_v2).

    Returns
    -------
    UDParse
        Parse converted to use Token objects with full dependency structure.
    """
    from ..core.token import Token
    from ..parsing.udparse import DepTriple
    from ..parsing.udparse import UDParse as ModernUDParse

    tokens = []
    for i, w in enumerate(parse.tokens):
        tokens.append(Token(i, w, parse.tags[i], ud))

    def convert_edge(e) -> DepTriple:
        return DepTriple(gov=tokens[e.gov], dep=tokens[e.dep], rel=e.rel)

    for i, _ in enumerate(tokens):
        tokens[i].gov = (None if i not in parse.governor or parse.governor[i].gov == -1
                         else tokens[parse.governor[i].gov])
        tokens[i].gov_rel = parse.governor[i].rel if i in parse.governor else 'root'
        tokens[i].dependents = [convert_edge(e) for e in parse.dependents[i]]

    return ModernUDParse(tokens, parse.tags, [convert_edge(e) for e in parse.triples], ud)


class PredPattEngine:
    """Main extraction engine for PredPatt predicate-argument structures.

    This class orchestrates the complete extraction pipeline for identifying
    predicates and their arguments from Universal Dependencies parses. It follows
    the exact same processing order and behavior as the original PredPatt
    implementation.

    Parameters
    ----------
    parse : UDParse
        The Universal Dependencies parse to extract from.
    opts : PredPattOpts, optional
        Configuration options for extraction. If None, uses default options.

    Attributes
    ----------
    options : PredPattOpts
        Configuration options controlling extraction behavior.
    ud : object
        Universal Dependencies schema (dep_v1 or dep_v2) based on options.
    tokens : list[Token]
        List of Token objects from the parse.
    edges : list[DepTriple]
        List of dependency triples from the parse.
    instances : list[Predicate]
        Final list of predicate instances after all processing.
    events : list[Predicate] | None
        List of predicate events before coordination expansion.
    event_dict : dict[Token, Predicate] | None
        Mapping from root tokens to their predicate objects.
    """

    def __init__(self, parse: UDParse, opts: PredPattOpts | None = None) -> None:
        """Initialize PredPattEngine with parse and options.

        Sets up the extraction engine with configuration and prepares the parse
        for processing. Automatically triggers the complete extraction pipeline.

        Parameters
        ----------
        parse : UDParse
            The Universal Dependencies parse to extract from.
        opts : PredPattOpts, optional
            Configuration options for extraction. If None, uses default options.
        """
        # initialize in exact same order as original
        self.options = opts or PredPattOpts()   # use defaults
        self.ud = dep_v1 if self.options.ud == dep_v1.VERSION else dep_v2
        parse = convert_parse(parse, self.ud)
        self._parse = parse
        self.edges = parse.triples
        self.tokens = parse.tokens
        self.instances: list[Predicate] = []
        self.events: list[Predicate] | None = None
        self.event_dict: dict | None = None  # map from token position to Predicate

        # trigger extraction pipeline
        self.extract()

    @classmethod
    def from_constituency(cls, parse_string: str, cacheable: bool = True,
                         opts: PredPattOpts | None = None) -> PredPattEngine:
        """Create PredPattEngine from a constituency parse string.

        Converts constituency parse to Universal Dependencies automatically.
        [English only]

        Parameters
        ----------
        parse_string : str
            The constituency parse string to convert.
        cacheable : bool, optional
            Whether to use cached parser instance. Default: True.
        opts : PredPattOpts, optional
            Configuration options for extraction.

        Returns
        -------
        PredPattEngine
            Engine instance with extraction results from converted parse.
        """
        from ..util.UDParser import Parser
        global _PARSER
        if _PARSER is None:
            _PARSER = Parser.get_instance(cacheable)
        parse = _PARSER.to_ud(parse_string)
        return cls(parse, opts=opts)

    @classmethod
    def from_sentence(cls, sentence: str, cacheable: bool = True,
                     opts: PredPattOpts | None = None) -> PredPattEngine:
        """Create PredPattEngine from a sentence string.

        Parses sentence and converts to Universal Dependencies automatically.
        [English only]

        Parameters
        ----------
        sentence : str
            The sentence string to parse and extract from.
        cacheable : bool, optional
            Whether to use cached parser instance. Default: True.
        opts : PredPattOpts, optional
            Configuration options for extraction.

        Returns
        -------
        PredPattEngine
            Engine instance with extraction results from parsed sentence.
        """
        from ..util.UDParser import Parser
        global _PARSER
        if _PARSER is None:
            _PARSER = Parser.get_instance(cacheable)
        parse = _PARSER(sentence)
        return cls(parse, opts=opts)

    def extract(self) -> None:
        """Execute the complete predicate-argument extraction pipeline.

        Orchestrates all phases of extraction in the exact order specified
        in the PREDPATT_EXTRACTION_PIPELINE.md documentation:

        1. Predicate root identification
        2. Event dictionary creation
        3. Argument root extraction
        4. Argument resolution
        5. Argument sorting
        6. Phrase extraction
        7. Argument simplification (optional)
        8. Conjunction resolution
        9. Coordination expansion
        10. Relative clause cleanup
        11. Final cleanup

        This method modifies the engine state and populates the instances
        attribute with the final extraction results.
        """
        # TODO: Implement extraction pipeline phases
        # This will be implemented in subsequent phases following the
        # exact order documented in PREDPATT_EXTRACTION_PIPELINE.md

        # Phase 1: Predicate Root Identification
        events = self.identify_predicate_roots()

        # Phase 2: Event Dictionary Creation
        self.event_dict = {p.root: p for p in events}

        # Phase 3: Argument Root Extraction
        for e in events:
            e.arguments = self.argument_extract(e)

        # Phase 4: Argument Resolution
        events = sort_by_position(self._argument_resolution(events))

        # Phase 5: Argument Sorting
        for p in events:
            p.arguments.sort(key=lambda x: x.root.position)

        # Store events before phrase extraction (needed for phrase extraction rules)
        self.events = events

        # Phase 6-9: Extract phrases and process each predicate
        # CRITICAL: Must process each predicate completely before moving to next
        # This matches the original implementation's structure
        for p in events:
            # Phase 6: Phrase Extraction
            self._pred_phrase_extract(p)
            for arg in p.arguments:
                if not arg.is_reference() and arg.tokens == []:
                    self._arg_phrase_extract(p, arg)

            # Phase 7: Argument Simplification (Optional)
            if self.options.simple:
                # Simplify predicate's by removing non-core arguments.
                p.arguments = [arg for arg in p.arguments if self._simple_arg(p, arg)]

            # Phase 8: Conjunction Resolution
            if p.root.gov_rel == self.ud.conj:
                # Special cases for predicate conjunctions.
                self._conjunction_resolution(p)

            # Phase 9: Coordination Expansion
            if len(p.tokens):
                self.instances.extend(self.expand_coord(p))

        # Phase 10: Relative Clause Cleanup
        if self.options.resolve_relcl and self.options.borrow_arg_for_relcl:
            # Filter dummy arguments (that, which, who)
            for p in self.instances:
                from ..rules import argument_rules as R  # noqa: N812
                if any(isinstance(r, R.PredResolveRelcl) for r in p.rules):
                    new = [a for a in p.arguments if a.phrase() not in {'that', 'which', 'who'}]
                    if new != p.arguments:
                        p.arguments = new
                        p.rules.append(R.EnRelclDummyArgFilter())

        # Phase 11: Final Cleanup
        self._cleanup()
        self._remove_broken_predicates()

        # Store results
        self.events = events
        # self.instances is now populated by coordination expansion and cleanup

    def identify_predicate_roots(self) -> list[Predicate]:
        """Predicate root identification.

        Identifies predicate root tokens by applying predicate identification rules
        in the exact same order as the original implementation. This includes
        special predicate types (APPOS, POSS, AMOD) and conjunction expansion.

        Returns
        -------
        list[Predicate]
            List of predicate objects sorted by position.
        """
        from ..core.predicate import Predicate
        from ..rules import predicate_rules as R  # noqa: N812

        roots = {}

        def nominate(root, rule, type_=NORMAL):
            """Create or update a predicate instance with rules.

            Parameters
            ----------
            root : Token
                The root token of the predicate.
            rule : Rule
                The rule that identified this predicate.
            type_ : str, optional
                The predicate type (NORMAL, POSS, APPOS, AMOD).

            Returns
            -------
            Predicate
                The predicate instance.
            """
            if root not in roots:
                roots[root] = Predicate(root, self.ud, [rule], type_=type_)
            else:
                roots[root].rules.append(rule)
            return roots[root]

        # Apply predicate identification rules in exact order
        for e in self.edges:
            # Punctuation can't be a predicate
            if not e.dep.isword:
                continue

            # Special predicate types (conditional on options)
            if self.options.resolve_appos and e.rel == self.ud.appos:
                nominate(e.dep, R.D(), APPOS)

            if self.options.resolve_poss and e.rel == self.ud.nmod_poss:
                nominate(e.dep, R.V(), POSS)

            # If resolve amod flag is enabled, then the dependent of an amod
            # arc is a predicate (but only if the dependent is an
            # adjective). We also filter cases where ADJ modifies ADJ.
            if self.options.resolve_amod and e.rel == self.ud.amod and e.dep.tag == postag.ADJ and e.gov.tag != postag.ADJ:
                nominate(e.dep, R.E(), AMOD)

            # Avoid 'dep' arcs, they are normally parse errors.
            # Note: we allow amod, poss, and appos predicates, even with a dep arc.
            if e.gov.gov_rel == self.ud.dep:
                continue

            # Core predicate patterns
            # If it has a clausal subject or complement its a predicate.
            if e.rel in {self.ud.ccomp, self.ud.csubj, self.ud.csubjpass}:
                nominate(e.dep, R.A1())

            # Dependent of clausal modifier is a predicate.
            if self.options.resolve_relcl and e.rel in {self.ud.advcl, self.ud.acl, self.ud.aclrelcl}:
                nominate(e.dep, R.B())

            if e.rel == self.ud.xcomp:
                # Dependent of an xcomp is a predicate
                nominate(e.dep, R.A2())

            if gov_looks_like_predicate(e, self.ud):
                # Look into e.gov
                if e.rel == self.ud.ccomp and e.gov.argument_like():
                    # In this case, e.gov looks more like an argument than a predicate
                    #
                    # For example, declarative context sentences
                    #
                    # We expressed [ our hope that someday the world will know peace ]
                    #                     |                                ^
                    #                    gov ------------ ccomp --------- dep
                    #
                    pass
                elif e.gov.gov_rel == self.ud.xcomp:
                    # TODO: I don't think we need this case.
                    if e.gov.gov is not None and not e.gov.gov.hard_to_find_arguments():
                        nominate(e.gov, R.C(e))
                else:
                    if not e.gov.hard_to_find_arguments():
                        nominate(e.gov, R.C(e))

        # Add all conjoined predicates using breadth-first search
        q = list(roots.values())
        while q:
            gov = q.pop()
            if gov.root.dependents:  # check if dependents exist
                for e in gov.root.dependents:
                    if e.rel == self.ud.conj and self.qualified_conjoined_predicate(e.gov, e.dep):
                        q.append(nominate(e.dep, R.F()))

        return sort_by_position(roots.values())

    def qualified_conjoined_predicate(self, gov, dep) -> bool:
        """Check if the conjunction (dep) of a predicate (gov) is another predicate.

        Parameters
        ----------
        gov : Token
            The governing token (existing predicate).
        dep : Token
            The dependent token (potential conjoined predicate).

        Returns
        -------
        bool
            True if the dependent qualifies as a conjoined predicate.
        """
        if not dep.isword:
            return False
        if gov.tag in {postag.VERB}:
            # Conjoined predicates should have the same tag as the root.
            # For example,
            # There is nothing wrong with a negotiation, but nothing helpful .
            #       ^---------------conj-----------------------^
            return gov.tag == dep.tag
        return True

    def argument_extract(self, predicate) -> list:
        """Extract argument root tokens for a given predicate.

        Applies argument identification rules in the exact same order as the
        original implementation. This includes core arguments (g1), nominal
        modifiers (h1, h2), clausal arguments (k), and special predicate
        type arguments (i, j, w1, w2).

        Parameters
        ----------
        predicate : Predicate
            The predicate to extract arguments for.

        Returns
        -------
        list[Argument]
            List of argument objects for this predicate.
        """
        from ..core.argument import Argument
        from ..rules import argument_rules as R  # noqa: N812

        arguments = []

        # Apply argument identification rules in exact order
        for e in predicate.root.dependents:

            # Core arguments (g1 rule)
            if e.rel in {self.ud.nsubj, self.ud.nsubjpass, self.ud.dobj, self.ud.iobj}:
                arguments.append(Argument(e.dep, self.ud, [R.G1(e)]))

            # Nominal modifiers (h1 rule) - exclude AMOD predicates
            elif ((e.rel.startswith(self.ud.nmod) or e.rel.startswith(self.ud.obl))
                  and predicate.type != AMOD):
                arguments.append(Argument(e.dep, self.ud, [R.H1()]))

            # Clausal arguments (k rule)
            elif (e.rel in {self.ud.ccomp, self.ud.csubj, self.ud.csubjpass}
                  or (self.options.cut and e.rel == self.ud.xcomp)):
                arguments.append(Argument(e.dep, self.ud, [R.K()]))

        # Indirect modifiers (h2 rule) - through advmod
        for e in predicate.root.dependents:
            if e.rel == self.ud.advmod:
                for tr in e.dep.dependents:
                    if tr.rel.startswith(self.ud.nmod) or tr.rel in {self.ud.obl}:
                        arguments.append(Argument(tr.dep, self.ud, [R.H2()]))

        # Special predicate type arguments
        if predicate.type == AMOD:
            # i rule: AMOD predicates get their governor
            arguments.append(Argument(predicate.root.gov, self.ud, [R.I()]))

        elif predicate.type == APPOS:
            # j rule: APPOS predicates get their governor
            arguments.append(Argument(predicate.root.gov, self.ud, [R.J()]))

        elif predicate.type == POSS:
            # w1 rule: POSS predicates get their governor
            arguments.append(Argument(predicate.root.gov, self.ud, [R.W1()]))
            # w2 rule: POSS predicates also get themselves as argument
            arguments.append(Argument(predicate.root, self.ud, [R.W2()]))

        return arguments

    def _argument_resolution(self, events) -> list:
        """Resolve and share arguments between predicates.

        Implements the argument resolution phase which includes:
        1. XComp merging (if not cut mode)
        2. Relative clause resolution (if resolve_relcl)
        3. Conjunction argument borrowing
        4. Adverbial clause subject borrowing
        5. Cut mode processing (if cut enabled)

        Parameters
        ----------
        events : list[Predicate]
            List of predicate objects with initial arguments.

        Returns
        -------
        list[Predicate]
            List of predicates with resolved arguments.
        """
        from ..core.argument import Argument
        from ..rules import argument_rules as R  # noqa: N812

        # Lexicalized exceptions for object control verbs

        # 1. XComp merging (if not cut mode)
        for p in list(events):
            if p.root.gov_rel == self.ud.xcomp and not self.options.cut:
                # Merge the arguments of xcomp to its gov. (Unlike ccomp, an open
                # clausal complement (xcomp) shares its arguments with its gov.)
                g = self._get_top_xcomp(p)
                if g is not None:
                    # Extend the arguments of event's governor
                    args = [arg for arg in p.arguments]
                    g.rules.append(R.L())
                    g.arguments.extend(args)
                    # copy arg rules of `event` to its gov's rule tracker.
                    for arg in args:
                        arg.rules.append(R.L())
                    # remove p in favor of it's xcomp governor g.
                    events = [e for e in events if e.position != p.position]

        # 2. Relative clause resolution (if resolve_relcl)
        for p in sort_by_position(events):
            # Add an argument to predicate inside relative clause. The
            # missing argument is rooted at the governor of the `acl`
            # dependency relation (type acl) pointing here.
            if (self.options.resolve_relcl and self.options.borrow_arg_for_relcl
                    and p.root.gov_rel.startswith(self.ud.acl)):
                new = Argument(p.root.gov, self.ud, [R.ArgResolveRelcl()])
                p.rules.append(R.PredResolveRelcl())
                p.arguments.append(new)

        # 3. Conjunction argument borrowing
        for p in sort_by_position(events):
            if p.root.gov_rel == self.ud.conj:
                g = self.event_dict.get(p.root.gov)
                if g is not None:
                    if not p.has_subj():
                        if g.has_subj():
                            # If an event governed by a conjunction is missing a
                            # subject, try borrowing the subject from the other
                            # event.
                            new_arg = g.subj().reference()
                            new_arg.rules.append(R.BorrowSubj(new_arg, g))
                            p.arguments.append(new_arg)
                        else:
                            # Try borrowing the subject from g's xcomp (if any)
                            g_ = self._get_top_xcomp(g)
                            if g_ is not None and g_.has_subj():
                                new_arg = g_.subj().reference()
                                new_arg.rules.append(R.BorrowSubj(new_arg, g_))
                                p.arguments.append(new_arg)
                    if len(p.arguments) == 0 and g.has_obj():
                            # If an event governed by a conjunction is missing an
                            # argument, try borrowing the object from the other
                            # event.
                            new_arg = g.obj().reference()
                            new_arg.rules.append(R.BorrowObj(new_arg, g))
                            p.arguments.append(new_arg)

        # 4. Adverbial clause subject borrowing
        for p in sort_by_position(events):
            # Lexicalized exceptions: from/for marked clauses
            from_for = any([e.dep.text in ['from', 'for'] and e.rel == 'mark'
                           for e in p.root.dependents])

            if p.root.gov_rel == self.ud.advcl and not p.has_subj() and not from_for:
                g = self.event_dict.get(p.root.gov)
                if g is not None and g.has_subj():
                    new_arg = g.subj().reference()
                    new_arg.rules.append(R.BorrowSubj(new_arg, g))
                    p.arguments.append(new_arg)

        # 5. Cut mode processing (if cut enabled)
        for p in sort_by_position(events):
            if p.root.gov_rel == self.ud.xcomp and self.options.cut:
                for g in self.parents(p):
                    # Subject of an xcomp is most likely to come from the
                    # object of the governing predicate.
                    if g.has_obj():
                        # "I like you to finish this work"
                        #      ^   ^       ^
                        #      g  g.obj    p
                        new_arg = g.obj().reference()
                        new_arg.rules.append(R.CutBorrowObj(new_arg, g))
                        p.arguments.append(new_arg)
                        break
                    elif g.has_subj():
                        # "I  'd   like to finish this work"
                        #  ^         ^       ^
                        #  g.subj    g       p
                        new_arg = g.subj().reference()
                        new_arg.rules.append(R.CutBorrowSubj(new_arg, g))
                        p.arguments.append(new_arg)
                        break
                    elif g.root.gov_rel in self.ud.ADJ_LIKE_MODS:
                        # PredPatt recognizes structures which are shown to be accurate .
                        #                         ^                  ^      ^
                        #                       g.subj               g      p
                        from ..core.argument import Argument
                        new_arg = Argument(
                            g.root.gov, self.ud, [R.CutBorrowOther(g.root.gov, g)]
                        )
                        p.arguments.append(new_arg)
                        break

        # 6. Special advcl borrowing (from/for marked clauses)
        for p in sort_by_position(events):
            if (p.root.gov_rel == self.ud.advcl
                    and not p.has_subj()
                    and any([e.dep.text in ['from', 'for']
                                    and e.rel == 'mark'
                                    for e in p.root.dependents])
                ):
                g = self.event_dict.get(p.root.gov)
                # set to the OBJECT not SUBJECT
                if g is not None and g.has_obj():
                    new_arg = g.obj().reference()
                    new_arg.rules.append(R.BorrowSubj(new_arg, g))
                    p.arguments.append(new_arg)

        # 7. General subject borrowing for missing subjects
        # Note: The following rule improves coverage a lot in Spanish and
        # Portuguese. Without it, miss a lot of arguments.
        for p in sort_by_position(events):
            if (not p.has_subj()
                and p.type == NORMAL
                and p.root.gov_rel not in {self.ud.csubj, self.ud.csubjpass}
                and not p.root.gov_rel.startswith(self.ud.acl)
                and not p.has_borrowed_arg()
                #and p.root.gov.text not in exclude
            ):
                g = self.event_dict.get(p.root.gov)
                if g is not None:
                    if g.has_subj():
                        new_arg = g.subj().reference()
                        new_arg.rules.append(R.BorrowSubj(new_arg, g))
                        p.arguments.append(new_arg)
                    else:
                        # Still no subject. Try looking at xcomp of conjunction root.
                        g = self._get_top_xcomp(p)
                        if g is not None and g.has_subj():
                            new_arg = g.subj().reference()
                            new_arg.rules.append(R.BorrowSubj(new_arg, g))
                            p.arguments.append(new_arg)

        return events

    def _get_top_xcomp(self, predicate):
        """Find the top-most governing xcomp predicate.

        Traverses up the chain of xcomp governors to find the top-most
        predicate in the xcomp chain. If there are no xcomp governors,
        returns the current predicate.

        Parameters
        ----------
        predicate : Predicate
            The predicate to start traversing from.

        Returns
        -------
        Predicate | None
            The top-most xcomp predicate or None if not found.
        """
        c = predicate.root.gov
        while c is not None and c.gov_rel == self.ud.xcomp and c in self.event_dict:
            c = c.gov
        return self.event_dict.get(c)

    def parents(self, predicate):
        """Iterate over the chain of parents (governing predicates).

        Yields predicates that govern the given predicate by following
        the chain of governor tokens.

        Parameters
        ----------
        predicate : Predicate
            The predicate to start from.

        Yields
        ------
        Predicate
            Each governing predicate in the chain.
        """
        c = predicate.root.gov
        while c is not None:
            if c in self.event_dict:
                yield self.event_dict[c]
            c = c.gov

    def expand_coord(self, predicate):
        """Expand coordinated arguments.

        Creates separate predicate instances for each combination of
        coordinated arguments (Cartesian product). For example:
        "A and B eat C and D" → 4 instances: (A,C), (A,D), (B,C), (B,D)

        Parameters
        ----------
        predicate : Predicate
            The predicate to expand coordinated arguments for.

        Returns
        -------
        list[Predicate]
            List of predicate instances with expanded argument combinations.
        """
        import itertools

        # Don't expand amod unless resolve_conj is enabled
        if not self.options.resolve_conj or predicate.type == AMOD:
            predicate.arguments = [arg for arg in predicate.arguments if arg.tokens]
            if not predicate.arguments:
                return []
            return [predicate]

        # Cleanup (strip before we take conjunctions)
        self._strip(predicate)
        for arg in predicate.arguments:
            if not arg.is_reference():
                self._strip(arg)

        aaa = []
        for arg in predicate.arguments:
            if not arg.share and not arg.tokens:
                continue
            c_list = []
            for c in arg.coords():
                if not c.is_reference() and not c.tokens:
                    # Extract argument phrase (if we haven't already). This
                    # happens because are haven't processed the subrees of the
                    # 'conj' node in the argument until now.
                    self._arg_phrase_extract(predicate, c)
                c_list.append(c)
            aaa = [c_list, *aaa]

        expanded = itertools.product(*aaa)
        instances = []
        for args in expanded:
            if not args:
                continue
            predicate.arguments = args
            instances.append(predicate.copy())
        return instances

    def _conjunction_resolution(self, p):
        """Conjunction resolution.

        Borrows auxiliary and negation tokens from governing predicate
        for conjoined predicates. Only applied when predicates share subjects.

        Parameters
        ----------
        p : Predicate
            The conjoined predicate to process.
        """
        from ..rules import predicate_rules as R  # noqa: N812

        # pull aux and neg from governing predicate.
        g = self.event_dict.get(p.root.gov)
        if g is not None and p.share_subj(g):
            # Only applied when p and g share subj. For example,
            # He did make mistakes, but that was okay .
            #         ^                           ^
            #         -----------conj--------------
            # No need to add "did" to "okay" in this case.
            for d in g.root.dependents:
                if d.rel in {self.ud.neg}: # {ud.aux, ud.neg}:
                    p.tokens.append(d.dep)
                    p.rules.append(R.PredConjBorrowAuxNeg(g, d))

        # Post-processing of predicate name for predicate conjunctions
        # involving xcomp.
        # Not applied to the cut mode, because in the cut mode xcomp
        # is recognized as a independent predicate. For example,
        # They start firing and shooting .
        #        ^     ^           ^
        #        |     |----conj---|
        #        -xcomp-
        # cut == True:
        #    (They, start, SOMETHING := firing and shooting)
        #    (They, firing)
        #    (They, shooting)
        # cut == False:
        #    (They, start firing)
        #    (They, start shooting)
        if not self.options.cut and p.root.gov.gov_rel == self.ud.xcomp:
                g = self._get_top_xcomp(p)
                if g is not None:
                    for y in g.tokens:
                        if (y != p.root.gov
                            and (y.gov != p.root.gov or y.gov_rel != self.ud.advmod)
                            and y.gov_rel != self.ud.case):
                            p.tokens.append(y)
                            p.rules.append(R.PredConjBorrowTokensXcomp(g, y))

    def _strip(self, thing):
        """Simplify expression by removing punct, cc, and mark from beginning and end of tokens.

        Removes trivial tokens (punctuation, coordinating conjunctions, and marks)
        from the beginning and end of token sequences to clean up phrase boundaries.

        For example:
        - Trailing punctuation: 'said ; .' -> 'said'
        - Function words: 'to shore up' -> 'shore up'

        Parameters
        ----------
        thing : Predicate | Argument
            The object to strip punctuation from.
        """
        from ..core.argument import Argument
        from ..rules import predicate_rules as R  # noqa: N812
        from ..utils.ud_schema import postag

        if self.options.big_args:
            return

        tokens = sort_by_position(thing.tokens)

        if not self.options.strip:
            thing.tokens = tokens
            return
        orig_len = len(tokens)

        protected = set()

        try:
            # prefix
            while tokens[0].gov_rel in self.ud.TRIVIALS and tokens[0].position not in protected:
                if (isinstance(thing, Argument)
                    and tokens[0].gov_rel == self.ud.mark
                    and tokens[1].tag == postag.VERB):
                    break
                tokens.pop(0)
            # suffix
            while tokens[-1].gov_rel in self.ud.TRIVIALS and tokens[-1].position not in protected:
                tokens.pop()
        except IndexError:
            tokens = []
        # remove repeated punctuation from the middle (happens when we remove an appositive)
        tokens = [tk for i, tk in enumerate(tokens)
                  if ((tk.gov_rel != self.ud.punct or
                       (i+1 < len(tokens) and tokens[i+1].gov_rel != self.ud.punct))
                      or tk.position in protected)]
        if orig_len != len(tokens):
            thing.rules.append(R.U())
        thing.tokens = tokens

    def _remove_broken_predicates(self):
        """Remove broken predicates.

        Filters out predicates that are considered broken or invalid
        from the final instances list.
        """
        instances = []
        for p in self.instances:
            if p.is_broken():
                continue
            instances.append(p)
        self.instances = instances

    @staticmethod
    def subtree(s, follow=lambda _: True):
        """Breadth-first iterator over nodes in a dependency tree.

        Parameters
        ----------
        s : Token
            Initial state token to start traversal from.
        follow : callable, optional
            Function that takes an edge and returns True if we should follow
            the edge. Default follows all edges.

        Yields
        ------
        Token
            Each token in the dependency subtree in breadth-first order.
        """
        q = [s]
        while q:
            s = q.pop()
            yield s
            q.extend(e.dep for e in s.dependents if follow(e))

    def _pred_phrase_extract(self, predicate):
        """Collect tokens for predicate phrase in the dependency subtree of predicate root token.

        Extracts tokens that belong to the predicate phrase by traversing the
        dependency subtree of the predicate root token and applying filtering
        rules to determine which tokens to include.

        Parameters
        ----------
        predicate : Predicate
            The predicate to extract phrase tokens for.
        """
        from ..rules import argument_rules as AR  # noqa: N812
        from ..rules import predicate_rules as R  # noqa: N812

        assert predicate.tokens == []
        if predicate.type == POSS:
            predicate.tokens = [predicate.root]
            return
        predicate.tokens.extend(self.subtree(predicate.root,
                                             lambda e: self._pred_phrase_helper(predicate, e)))

        if not self.options.simple:
            for arg in predicate.arguments:
                # Hoist case phrases in arguments into predicate phrase.
                #
                # Exception: do not extract case phrase from amod, appos and
                # relative clauses.
                #
                # e.g. 'Mr. Vinken is chairman of Elsevier , the Dutch publisher .'
                #       'Elsevier' is the arg phrase, but 'of' shouldn't
                #       be kept as a case token.
                #
                if (predicate.root.gov_rel not in self.ud.ADJ_LIKE_MODS
                    or predicate.root.gov != arg.root):
                    for e in arg.root.dependents:
                        if e.rel == self.ud.case:
                            arg.rules.append(AR.MoveCaseTokenToPred(e.dep))
                            predicate.tokens.extend(self.subtree(e.dep))
                            predicate.rules.append(R.N6(e.dep))

    def _pred_phrase_helper(self, pred, e):
        """Determine which tokens to extract for the predicate phrase.

        This function is used when determining which edges to traverse when
        extracting predicate phrases. We add the dependent of each edge we
        traverse. Rules are appended to predicate as a side-effect.

        Parameters
        ----------
        pred : Predicate
            The predicate being processed.
        e : DepTriple
            The dependency edge to check.

        Returns
        -------
        bool
            True if we should include this edge in the predicate phrase.
        """
        from ..rules import predicate_rules as R  # noqa: N812

        if e.dep in {a.root for a in pred.arguments}:
            # pred token shouldn't be argument root token.
            pred.rules.append(R.N2(e.dep))
            return False
        if e.dep in {p.root for p in self.events} and e.rel != self.ud.amod:
            # pred token shouldn't be other pred root token.
            pred.rules.append(R.N3(e.dep))
            return False
        if e.rel in self.ud.PRED_DEPS_TO_DROP:
            # pred token shouldn't be a dependent of any rels above.
            pred.rules.append(R.N4(e.dep))
            return False
        if ((e.gov == pred.root or e.gov.gov_rel == self.ud.xcomp)
            and e.rel in {self.ud.cc, self.ud.conj}):
            # pred token shouldn't take conjuncts of pred
            # root token or xcomp's dependent.
            pred.rules.append(R.N5(e.dep))
            return False
        if self.options.simple:
            # Simple predicates don't have nodes governed by advmod or aux.
            if e.rel == self.ud.advmod:
                pred.rules.append(R.Q())
                return False
            elif e.rel == self.ud.aux:
                pred.rules.append(R.R())
                return False

        pred.rules.append(R.N1(e.dep))
        return True

    def _arg_phrase_extract(self, predicate, argument):
        """Collect tokens for argument phrase in the dependency subtree of argument root token.

        Extracts tokens that belong to the argument phrase by traversing the
        dependency subtree of the argument root token and applying filtering
        rules to determine which tokens to include.

        Parameters
        ----------
        predicate : Predicate
            The predicate this argument belongs to.
        argument : Argument
            The argument to extract phrase for.
        """
        assert argument.tokens == []
        argument.tokens.extend(
            self.subtree(
                argument.root,
                lambda e: self._arg_phrase_helper(predicate, argument, e)
            )
        )

    def _arg_phrase_helper(self, pred, arg, e):
        """Determine which tokens to extract for the argument phrase.

        Determines which tokens to extract for the argument phrase from the subtree
        rooted at argument's root token. Rules are provided as a side-effect.

        Parameters
        ----------
        pred : Predicate
            The predicate being processed.
        arg : Argument
            The argument being processed.
        e : DepTriple
            The dependency edge to check.

        Returns
        -------
        bool
            True if we should include this edge in the argument phrase.
        """
        from ..rules import argument_rules as R  # noqa: N812

        if self.options.big_args:
            return True

        if pred.has_token(e.dep):
            arg.rules.append(R.PredicateHas(e.dep))
            return False

        # Case tokens are added to predicate, not argument.
        if e.gov == arg.root and e.rel == self.ud.case:
            return False

        if self.options.resolve_appos and e.rel in {self.ud.appos}:
            arg.rules.append(R.DropAppos(e.dep))
            return False

        if e.rel in {self.ud.dep}:
            arg.rules.append(R.DropUnknown(e.dep))
            return False

        # Direct dependents of the predicate root of the follow types shouldn't
        # be added the predicate phrase.
        # If the argument root is the gov of the predicate root, then drop
        # the following direct dependent of the argument root.
        if (arg.root == pred.root.gov and e.gov == arg.root
                and e.rel in self.ud.SPECIAL_ARG_DEPS_TO_DROP):
            arg.rules.append(R.SpecialArgDropDirectDep(e.dep))
            return False

        if self.options.resolve_conj:

            # Remove top-level conjunction tokens if work expanding conjunctions.
            if e.gov == arg.root and e.rel in {self.ud.cc, self.ud.cc_preconj}:
                arg.rules.append(R.DropCc(e.dep))
                return False

            # Argument shouldn't include anything from conjunct subtree.
            if e.gov == arg.root and e.rel == self.ud.conj:
                arg.rules.append(R.DropConj(e.dep))
                return False

        # If none of the filters fired, then we accept the token.
        arg.rules.append(R.CleanArgToken(e.dep))
        return True

    def _simple_arg(self, pred, arg):
        """Filter out some arguments to simplify pattern.

        Determines whether an argument should be kept in simple mode by
        applying simplification rules based on dependency relations and
        argument types.

        Parameters
        ----------
        pred : Predicate
            The predicate being processed.
        arg : Argument
            The argument to filter.

        Returns
        -------
        bool
            True if the argument should be kept, False if it should be filtered out.
        """
        from ..rules import predicate_rules as R  # noqa: N812

        if pred.type == POSS:
            return True
        if (pred.root.gov_rel in self.ud.ADJ_LIKE_MODS
            and pred.root.gov == arg.root):
            # keep the post-added argument, which neither directly nor
            # indirectly depends on the predicate root. Say, the governor
            # of amod, appos and acl.
            return True
        if arg.root.gov_rel in self.ud.SUBJ:
            # All subjects are core arguments, even "borrowed" one.
            return True
        if arg.root.gov_rel in self.ud.NMODS:
            # remove the argument which is a nominal modifier.
            # this condition check must be in front of the following one.
            pred.rules.append(R.P1())
            return False
        # keep argument directly depending on pred root token,
        # except argument is the dependent of 'xcomp' rel.
        return arg.root.gov == pred.root or arg.root.gov.gov_rel == self.ud.xcomp

    def _cleanup(self):
        """Cleanup operations: Sort instances and arguments by text order.

        Performs final cleanup by sorting instances and their arguments by
        position and applying stripping to remove punctuation and mark tokens.
        """
        self.instances = sort_by_position(self.instances)
        for p in self.instances:
            p.arguments = sort_by_position(p.arguments)
            self._strip(p)
            for arg in p.arguments:
                self._strip(arg)

    def pprint(self, color: bool = False, track_rule: bool = False) -> str:
        """Pretty-print extracted predicate-argument tuples.

        Parameters
        ----------
        color : bool, optional
            Whether to use colored output (default: False).
        track_rule : bool, optional
            Whether to include rule tracking information (default: False).

        Returns
        -------
        str
            Pretty-printed string representation of predicates and arguments.
        """
        from ..utils.visualization import pprint as pprint_predpatt
        return pprint_predpatt(self, color=color, track_rule=track_rule)
