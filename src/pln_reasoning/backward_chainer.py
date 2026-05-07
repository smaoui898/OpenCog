"""
backward_chainer.py
===================
PLN Backward Chainer for the medical diagnostic demo.

The backward chainer starts from a GOAL (e.g., "What disease does Patient X have?")
and works backward through the AtomSpace to find supporting evidence,
applying PLN rules to compute final truth values.

Algorithm:
  1. For each disease in the KB:
     a. Find all has_symptom EvaluationLinks for that disease
     b. Filter: which symptoms does the patient present?
     c. Collect their TV scores
     d. Apply PLN rules to get a diagnosis TV
  2. Sort results by TV score (strength × confidence)
  3. Return ranked list of (disease_name, TruthValue) pairs
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from ..atomspace_setup.atom_types import TruthValue, EvaluationLink
from ..atomspace_setup.knowledge_base import AtomSpace, MedicalKnowledgeBase
from .rules import PLNRules, RuleResult


# ── Diagnostic result ─────────────────────────────────────────────────────────

class DiagnosticResult:
    """Single disease hypothesis with its PLN-derived truth value."""

    def __init__(self, disease: str, tv: TruthValue,
                 matched_symptoms: List[str],
                 total_symptoms: int):
        self.disease = disease
        self.tv = tv
        self.matched_symptoms = matched_symptoms
        self.total_symptoms = total_symptoms

    @property
    def coverage(self) -> float:
        """Fraction of known symptoms matched."""
        if self.total_symptoms == 0:
            return 0.0
        return len(self.matched_symptoms) / self.total_symptoms

    @property
    def score(self) -> float:
        return self.tv.score

    def __repr__(self) -> str:
        return (f"DiagnosticResult(disease={self.disease!r}, "
                f"{self.tv}, coverage={self.coverage:.0%}, "
                f"symptoms={self.matched_symptoms})")


# ── Backward Chainer ──────────────────────────────────────────────────────────

class BackwardChainer:
    """
    PLN Backward Chainer for symptom-based disease diagnosis.

    Usage:
        kb = MedicalKnowledgeBase().build()
        chainer = BackwardChainer(kb)
        results = chainer.diagnose(["Fever", "Cough", "Fatigue"])
    """

    def __init__(self, kb: MedicalKnowledgeBase,
                 rules: Optional[PLNRules] = None):
        self.kb = kb
        self.space: AtomSpace = kb.atomspace
        self.rules = rules or PLNRules()
        self._cache: Dict[str, List[EvaluationLink]] = {}

    # ── Public API ─────────────────────────────────────────────────────────

    def diagnose(self,
                 patient_symptoms: List[str],
                 top_k: int = 5,
                 min_score: float = 0.05) -> List[DiagnosticResult]:
        """
        Run backward chaining to infer the most likely diagnoses.

        Parameters
        ----------
        patient_symptoms : list of symptom names the patient presents
        top_k            : return at most this many results
        min_score        : minimum TV score to include in results

        Returns
        -------
        List of DiagnosticResult sorted by score descending
        """
        patient_symptoms_lower = {s.lower(): s for s in patient_symptoms}
        results = []

        for disease in self.kb.get_diseases():
            result = self._evaluate_disease(disease, patient_symptoms_lower)
            if result and result.score >= min_score:
                results.append(result)

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def explain(self, disease: str,
                patient_symptoms: List[str]) -> Dict:
        """
        Return a full explanation of why (or why not) a disease was inferred.

        Parameters
        ----------
        disease          : disease name to explain
        patient_symptoms : symptom list

        Returns
        -------
        dict with keys: disease, matched, unmatched, tv, rule_chain
        """
        patient_lower = {s.lower(): s for s in patient_symptoms}
        all_symptom_links = self._get_symptom_links(disease)

        matched = []
        unmatched = []
        matched_tvs = []

        for link in all_symptom_links:
            symptom_name = link.arguments.outgoing[1].name
            if symptom_name.lower() in patient_lower:
                matched.append(symptom_name)
                matched_tvs.append(link.tv)
            else:
                unmatched.append(symptom_name)

        if matched_tvs:
            final_tv = self.rules.score_diagnosis(matched_tvs)
        else:
            final_tv = TruthValue.null()

        return {
            "disease": disease,
            "matched_symptoms": matched,
            "unmatched_symptoms": unmatched,
            "matched_count": len(matched),
            "total_symptoms": len(all_symptom_links),
            "coverage": len(matched) / max(len(all_symptom_links), 1),
            "tv": final_tv,
            "score": final_tv.score,
            "rule_chain": [
                f"AbductionRule({sym}) → TV({tv})"
                for sym, tv in zip(matched, matched_tvs)
            ],
        }

    def find_differentials(self,
                           disease_a: str,
                           disease_b: str,
                           patient_symptoms: List[str]) -> Dict:
        """
        Compare two diseases for differential diagnosis.
        Returns which symptoms distinguish them.
        """
        syms_a = {lnk.arguments.outgoing[1].name
                  for lnk in self._get_symptom_links(disease_a)}
        syms_b = {lnk.arguments.outgoing[1].name
                  for lnk in self._get_symptom_links(disease_b)}

        common = syms_a & syms_b
        only_a = syms_a - syms_b
        only_b = syms_b - syms_a
        patient_set = {s.lower() for s in patient_symptoms}

        return {
            "disease_a": disease_a,
            "disease_b": disease_b,
            "common_symptoms": sorted(common),
            "only_in_a": sorted(only_a),
            "only_in_b": sorted(only_b),
            "differentiating_present": sorted(
                s for s in (only_a | only_b) if s.lower() in patient_set
            ),
        }

    # ── Internal helpers ───────────────────────────────────────────────────

    def _get_symptom_links(self, disease: str) -> List:
        """Cached lookup of all has_symptom EvaluationLinks for a disease."""
        if disease in self._cache:
            return self._cache[disease]
        links = self.kb.get_symptom_links_for_disease(disease)
        self._cache[disease] = links
        return links

    def _evaluate_disease(self,
                          disease: str,
                          patient_symptoms_lower: Dict[str, str]
                          ) -> Optional[DiagnosticResult]:
        """
        Apply PLN rules to compute how likely `disease` is given patient symptoms.
        """
        all_links = self._get_symptom_links(disease)
        if not all_links:
            return None

        matched_symptoms = []
        matched_tvs = []

        for link in all_links:
            symptom_name = link.arguments.outgoing[1].name
            if symptom_name.lower() in patient_symptoms_lower:
                matched_symptoms.append(symptom_name)
                matched_tvs.append(link.tv)

        if not matched_tvs:
            return DiagnosticResult(
                disease=disease,
                tv=TruthValue(0.0, 0.0),
                matched_symptoms=[],
                total_symptoms=len(all_links)
            )

        # Apply PLN scoring
        final_tv = self.rules.score_diagnosis(matched_tvs)

        # Boost confidence if many symptoms match
        coverage_boost = len(matched_symptoms) / len(all_links)
        boosted_confidence = min(1.0, final_tv.confidence * (1 + 0.3 * coverage_boost))
        final_tv = TruthValue(final_tv.strength, boosted_confidence)

        return DiagnosticResult(
            disease=disease,
            tv=final_tv,
            matched_symptoms=matched_symptoms,
            total_symptoms=len(all_links)
        )
