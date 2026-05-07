"""
AtomSpace Setup Package
========================
Provides utilities for building and managing the medical knowledge base.
"""

from .atom_types import (
    AtomType, TruthValue,
    Atom, Node, Link,
    ConceptNode, PredicateNode, NumberNode, VariableNode,
    InheritanceLink, EvaluationLink, ImplicationLink,
    AndLink, OrLink, NotLink, ListLink, MemberLink, SimilarityLink,
)
from .knowledge_base import AtomSpace, MedicalKnowledgeBase

__all__ = [
    "AtomType", "TruthValue",
    "Atom", "Node", "Link",
    "ConceptNode", "PredicateNode", "NumberNode", "VariableNode",
    "InheritanceLink", "EvaluationLink", "ImplicationLink",
    "AndLink", "OrLink", "NotLink", "ListLink", "MemberLink", "SimilarityLink",
    "AtomSpace", "MedicalKnowledgeBase",
]
