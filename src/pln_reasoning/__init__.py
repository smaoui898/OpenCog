"""
PLN Reasoning Package
=====================
Implements Probabilistic Logic Networks (PLN) reasoning over the medical
AtomSpace, including backward chaining, inference rules, and diagnostic queries.
"""

from .rules import PLNRules, DeductionRule, AbductionRule, ModusPonensRule
from .backward_chainer import BackwardChainer
from .queries import diagnose_patient, find_symptoms_for_disease, list_all_diseases

__all__ = [
    "PLNRules",
    "DeductionRule",
    "AbductionRule",
    "ModusPonensRule",
    "BackwardChainer",
    "diagnose_patient",
    "find_symptoms_for_disease",
    "list_all_diseases",
]
