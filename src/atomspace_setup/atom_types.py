"""
atom_types.py
=============
Defines the core atom types used in the OpenCog Medical Demo.
Pure-Python simulation of OpenCog's AtomSpace type system.
"""

from __future__ import annotations
import uuid
from enum import Enum
from typing import List, Optional


# ── Truth Value ───────────────────────────────────────────────────────────────

class TruthValue:
    """Simple Truth Value (STV): strength × confidence pair."""

    def __init__(self, strength: float = 1.0, confidence: float = 1.0):
        self.strength = max(0.0, min(1.0, float(strength)))
        self.confidence = max(0.0, min(1.0, float(confidence)))

    @property
    def score(self) -> float:
        """Composite ranking score: strength × confidence."""
        return self.strength * self.confidence

    def __repr__(self) -> str:
        return f"TV(s={self.strength:.3f}, c={self.confidence:.3f})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TruthValue):
            return NotImplemented
        return (abs(self.strength - other.strength) < 1e-6 and
                abs(self.confidence - other.confidence) < 1e-6)

    @classmethod
    def null(cls) -> "TruthValue":
        return cls(0.0, 0.0)


# ── Atom Type Enum ────────────────────────────────────────────────────────────

class AtomType(Enum):
    CONCEPT_NODE     = "ConceptNode"
    PREDICATE_NODE   = "PredicateNode"
    NUMBER_NODE      = "NumberNode"
    VARIABLE_NODE    = "VariableNode"
    INHERITANCE_LINK = "InheritanceLink"
    EVALUATION_LINK  = "EvaluationLink"
    IMPLICATION_LINK = "ImplicationLink"
    AND_LINK         = "AndLink"
    OR_LINK          = "OrLink"
    NOT_LINK         = "NotLink"
    LIST_LINK        = "ListLink"
    MEMBER_LINK      = "MemberLink"
    SIMILARITY_LINK  = "SimilarityLink"


# ── Base Atom ─────────────────────────────────────────────────────────────────

class Atom:
    """Abstract base class for all AtomSpace atoms."""

    def __init__(self, atom_type: AtomType, tv: Optional[TruthValue] = None):
        self._handle = str(uuid.uuid4())
        self._type = atom_type
        self._tv = tv or TruthValue(1.0, 0.0)

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def atom_type(self) -> AtomType:
        return self._type

    @property
    def tv(self) -> TruthValue:
        return self._tv

    @tv.setter
    def tv(self, value: TruthValue):
        self._tv = value

    def is_node(self) -> bool:
        return isinstance(self, Node)

    def is_link(self) -> bool:
        return isinstance(self, Link)

    def __hash__(self) -> int:
        return hash(self._handle)


# ── Node Types ────────────────────────────────────────────────────────────────

class Node(Atom):
    """Base class for node atoms (identified by name)."""

    def __init__(self, atom_type: AtomType, name: str,
                 tv: Optional[TruthValue] = None):
        super().__init__(atom_type, tv)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f'{self._type.value}("{self._name}") {self._tv}'

    def __str__(self) -> str:
        return f'{self._type.value}("{self._name}")'


class ConceptNode(Node):
    """Represents a concept: disease, symptom, patient, etc."""
    def __init__(self, name: str, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.CONCEPT_NODE, name, tv)


class PredicateNode(Node):
    """Represents a predicate / relation used in EvaluationLinks."""
    def __init__(self, name: str, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.PREDICATE_NODE, name, tv)


class NumberNode(Node):
    """Represents a numeric constant."""
    def __init__(self, value: float, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.NUMBER_NODE, str(value), tv)
        self._value = value

    @property
    def value(self) -> float:
        return self._value


class VariableNode(Node):
    """Logical variable for pattern matching (name prefixed with ?)."""
    def __init__(self, name: str, tv: Optional[TruthValue] = None):
        if not name.startswith("?"):
            name = "?" + name
        super().__init__(AtomType.VARIABLE_NODE, name, tv)


# ── Link Types ────────────────────────────────────────────────────────────────

class Link(Atom):
    """Base class for link atoms (connect two or more atoms)."""

    def __init__(self, atom_type: AtomType, outgoing: List[Atom],
                 tv: Optional[TruthValue] = None):
        super().__init__(atom_type, tv)
        self._outgoing = outgoing

    @property
    def outgoing(self) -> List[Atom]:
        return self._outgoing

    def arity(self) -> int:
        return len(self._outgoing)

    def __repr__(self) -> str:
        args = ", ".join(str(a) for a in self._outgoing)
        return f"{self._type.value}({args}) {self._tv}"

    def __str__(self) -> str:
        args = ", ".join(str(a) for a in self._outgoing)
        return f"{self._type.value}({args})"


class InheritanceLink(Link):
    """InheritanceLink(A, B): A is a kind of / has property B."""
    def __init__(self, source: Atom, target: Atom,
                 tv: Optional[TruthValue] = None):
        super().__init__(AtomType.INHERITANCE_LINK, [source, target], tv)

    @property
    def source(self) -> Atom:
        return self._outgoing[0]

    @property
    def target(self) -> Atom:
        return self._outgoing[1]


class ListLink(Link):
    """Ordered list of atoms — groups arguments for EvaluationLink."""
    def __init__(self, *atoms: Atom, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.LIST_LINK, list(atoms), tv)


class EvaluationLink(Link):
    """EvaluationLink(predicate, ListLink(args...)): predicate applied to args."""
    def __init__(self, predicate: PredicateNode, arguments: ListLink,
                 tv: Optional[TruthValue] = None):
        super().__init__(AtomType.EVALUATION_LINK, [predicate, arguments], tv)

    @property
    def predicate(self) -> PredicateNode:
        return self._outgoing[0]  # type: ignore

    @property
    def arguments(self) -> ListLink:
        return self._outgoing[1]  # type: ignore


class ImplicationLink(Link):
    """ImplicationLink(A, B): A implies B with probabilistic TV."""
    def __init__(self, antecedent: Atom, consequent: Atom,
                 tv: Optional[TruthValue] = None):
        super().__init__(AtomType.IMPLICATION_LINK, [antecedent, consequent], tv)

    @property
    def antecedent(self) -> Atom:
        return self._outgoing[0]

    @property
    def consequent(self) -> Atom:
        return self._outgoing[1]


class AndLink(Link):
    """Logical conjunction."""
    def __init__(self, *atoms: Atom, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.AND_LINK, list(atoms), tv)


class OrLink(Link):
    """Logical disjunction."""
    def __init__(self, *atoms: Atom, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.OR_LINK, list(atoms), tv)


class NotLink(Link):
    """Logical negation."""
    def __init__(self, atom: Atom, tv: Optional[TruthValue] = None):
        super().__init__(AtomType.NOT_LINK, [atom], tv)


class MemberLink(Link):
    """MemberLink(element, set): element belongs to set."""
    def __init__(self, element: Atom, set_atom: Atom,
                 tv: Optional[TruthValue] = None):
        super().__init__(AtomType.MEMBER_LINK, [element, set_atom], tv)


class SimilarityLink(Link):
    """SimilarityLink(A, B): A and B are similar concepts (symmetric)."""
    def __init__(self, atom_a: Atom, atom_b: Atom,
                 tv: Optional[TruthValue] = None):
        super().__init__(AtomType.SIMILARITY_LINK, [atom_a, atom_b], tv)
