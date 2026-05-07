"""
queries.py
==========
High-level query functions for the medical diagnostic demo.
These provide a simple, user-facing API over the BackwardChainer.
"""

from __future__ import annotations
from typing import List, Optional, Dict
from ..atomspace_setup.knowledge_base import MedicalKnowledgeBase
from .backward_chainer import BackwardChainer, DiagnosticResult

# ── Shared KB singleton (lazy init) ──────────────────────────────────────────

_kb: Optional[MedicalKnowledgeBase] = None
_chainer: Optional[BackwardChainer] = None


def _get_chainer() -> BackwardChainer:
    global _kb, _chainer
    if _chainer is None:
        _kb = MedicalKnowledgeBase().build()
        _chainer = BackwardChainer(_kb)
    return _chainer


# ── Public query functions ────────────────────────────────────────────────────

def diagnose_patient(symptoms: List[str],
                     top_k: int = 5,
                     min_score: float = 0.05) -> List[DiagnosticResult]:
    """
    Run a PLN diagnostic query for a patient presenting with given symptoms.

    Parameters
    ----------
    symptoms  : list of symptom names (case-insensitive)
    top_k     : max results to return
    min_score : minimum TV score threshold

    Returns
    -------
    Ranked list of DiagnosticResult (best first)

    Example
    -------
    >>> results = diagnose_patient(["Fever", "Cough", "Fatigue"])
    >>> for r in results:
    ...     print(r.disease, r.tv)
    """
    chainer = _get_chainer()
    return chainer.diagnose(symptoms, top_k=top_k, min_score=min_score)


def explain_diagnosis(disease: str,
                      symptoms: List[str]) -> Dict:
    """
    Return a detailed explanation of a diagnosis.

    Parameters
    ----------
    disease  : disease name to explain
    symptoms : patient's symptoms

    Returns
    -------
    dict with matched/unmatched symptoms, TV, and rule chain
    """
    chainer = _get_chainer()
    return chainer.explain(disease, symptoms)


def differential_diagnosis(disease_a: str,
                           disease_b: str,
                           symptoms: List[str]) -> Dict:
    """
    Compare two candidate diagnoses for differential analysis.

    Returns which symptoms distinguish disease_a from disease_b.
    """
    chainer = _get_chainer()
    return chainer.find_differentials(disease_a, disease_b, symptoms)


def find_symptoms_for_disease(disease: str) -> List[str]:
    """
    List all known symptoms for a given disease.

    Example
    -------
    >>> find_symptoms_for_disease("Influenza")
    ['Fever', 'Cough', 'Fatigue', 'MusclePain', 'Headache', 'Chills', 'SoreThroat']
    """
    chainer = _get_chainer()
    links = chainer.kb.get_symptom_links_for_disease(disease)
    return [lnk.arguments.outgoing[1].name for lnk in links]


def list_all_diseases() -> List[str]:
    """Return all diseases in the knowledge base."""
    chainer = _get_chainer()
    return chainer.kb.get_diseases()


def list_all_symptoms() -> List[str]:
    """Return all symptoms in the knowledge base."""
    chainer = _get_chainer()
    return chainer.kb.get_symptoms()


def symptom_overlap_analysis(symptoms: List[str]) -> Dict[str, float]:
    """
    For each disease, compute what fraction of its symptoms appear
    in the provided list (coverage score, independent of PLN TVs).

    Returns a dict {disease_name: coverage_ratio} sorted by coverage.
    """
    chainer = _get_chainer()
    symptom_set = {s.lower() for s in symptoms}
    coverage = {}

    for disease in chainer.kb.get_diseases():
        links = chainer.kb.get_symptom_links_for_disease(disease)
        if not links:
            continue
        matched = sum(
            1 for lnk in links
            if lnk.arguments.outgoing[1].name.lower() in symptom_set
        )
        coverage[disease] = matched / len(links)

    return dict(sorted(coverage.items(), key=lambda x: x[1], reverse=True))


def query_comorbidities(disease: str) -> List[str]:
    """
    Find diseases that frequently co-occur with the given disease.
    Uses comorbid_with EvaluationLinks from the KB.
    """
    chainer = _get_chainer()
    space = chainer.kb.atomspace
    results = []

    for link in space.get_all_links("EvaluationLink"):
        if not hasattr(link, 'predicate'):
            continue
        if link.predicate.name != "comorbid_with":
            continue
        args = link.arguments.outgoing
        if len(args) < 2:
            continue
        if args[0].name == disease:
            results.append(args[1].name)
        elif args[1].name == disease:
            results.append(args[0].name)

    return results
