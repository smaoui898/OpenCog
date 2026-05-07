"""
rules.py
========
PLN (Probabilistic Logic Networks) inference rules for the medical demo.

Rules implemented:
  - DeductionRule    : A→B, B→C ⊢ A→C
  - AbductionRule    : A→C, B→C ⊢ A→B  (symptom → disease abduction)
  - ModusPonensRule  : A, A→B ⊢ B
  - RevisionRule     : Combines two TVs for the same proposition
  - ConjunctionRule  : TV(A ∧ B) from TV(A) and TV(B)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
from ..atomspace_setup.atom_types import TruthValue


# ── TV combinators ────────────────────────────────────────────────────────────

def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def revision(tv1: TruthValue, tv2: TruthValue) -> TruthValue:
    """
    Revision rule: merge two TVs for the same proposition.
    Uses weighted average by confidence.

      s = (s1*c1 + s2*c2) / (c1 + c2 - c1*c2)
      c = (c1 + c2 - 2*c1*c2) / (1 - c1*c2)   [simplified]
    """
    c1, c2 = tv1.confidence, tv2.confidence
    if c1 + c2 == 0:
        return TruthValue(0.5, 0.0)
    denom = c1 + c2 - c1 * c2
    s = _clamp((tv1.strength * c1 + tv2.strength * c2) / denom)
    c_denom = 1 - c1 * c2
    c = _clamp((c1 + c2 - 2 * c1 * c2) / c_denom) if c_denom > 0 else 0.0
    return TruthValue(s, c)


def conjunction_tv(tv1: TruthValue, tv2: TruthValue) -> TruthValue:
    """
    TV of (A ∧ B): assumes independence.
      s = s1 * s2
      c = c1 * c2
    """
    return TruthValue(tv1.strength * tv2.strength,
                      tv1.confidence * tv2.confidence)


# ── Rule base dataclass ───────────────────────────────────────────────────────

@dataclass
class RuleResult:
    """Encapsulates a single rule application result."""
    rule_name: str
    consequent_name: str
    tv: TruthValue
    evidence: List[str]  # human-readable evidence trail

    @property
    def score(self) -> float:
        return self.tv.score

    def __repr__(self) -> str:
        return (f"RuleResult(rule={self.rule_name}, "
                f"disease={self.consequent_name}, {self.tv})")


# ── Individual rules ──────────────────────────────────────────────────────────

class DeductionRule:
    """
    Deduction: A→B and B→C ⊢ A→C

    TV propagation:
      s_AC = s_AB * s_BC + (1-s_AB) * (s_C - s_BC*s_B) / (1-s_B)
      c_AC = k * c_AB * c_BC       (k = 0.9 confidence discount)
    """

    NAME = "DeductionRule"
    K = 0.9  # confidence discount factor

    @classmethod
    def apply(cls,
              tv_ab: TruthValue,
              tv_bc: TruthValue,
              tv_b: Optional[TruthValue] = None,
              tv_c: Optional[TruthValue] = None) -> TruthValue:
        s_ab, s_bc = tv_ab.strength, tv_bc.strength
        # Simplified formula (assumes uniform prior on B and C)
        s_b = tv_b.strength if tv_b else 0.5
        s_c = tv_c.strength if tv_c else 0.5

        if abs(1 - s_b) < 1e-9:
            s_ac = s_ab * s_bc
        else:
            s_ac = s_ab * s_bc + (1 - s_ab) * (s_c - s_bc * s_b) / (1 - s_b)

        c_ac = cls.K * tv_ab.confidence * tv_bc.confidence
        return TruthValue(_clamp(s_ac), _clamp(c_ac))


class AbductionRule:
    """
    Abduction: A→C and B→C ⊢ A→B  (reverse inference for diagnosis)

    Given symptoms A, and implication A→Disease, infer Disease likelihood.
    TV formula (simplified Bayesian):
      s = s_AC * P(A) / P(C)    [Bayes inversion]
      c = k * c_AC
    """

    NAME = "AbductionRule"
    K = 0.85

    @classmethod
    def apply(cls,
              tv_symptom: TruthValue,
              tv_implication: TruthValue,
              prior_disease: float = 0.1) -> TruthValue:
        """
        Parameters
        ----------
        tv_symptom    : TV of the symptom being present
        tv_implication: TV of symptom → disease link
        prior_disease : prior probability of the disease
        """
        s_sym = tv_symptom.strength
        s_impl = tv_implication.strength
        # P(disease | symptom) ∝ P(symptom | disease) * P(disease)
        numerator = s_impl * prior_disease
        # Normalize (rough approximation)
        s = _clamp(numerator / (prior_disease + (1 - prior_disease) * (1 - s_impl) + 1e-9))
        c = _clamp(cls.K * tv_implication.confidence * tv_symptom.confidence)
        return TruthValue(s, c)


class ModusPonensRule:
    """
    Modus Ponens: A (true), A→B ⊢ B

    TV formula:
      s_B = s_A * s_AB + (1 - s_A) * (1 - s_AB) * 0.05   [small noise term]
      c_B = c_A * c_AB * k
    """

    NAME = "ModusPonensRule"
    K = 0.9

    @classmethod
    def apply(cls, tv_a: TruthValue, tv_ab: TruthValue) -> TruthValue:
        s_a, s_ab = tv_a.strength, tv_ab.strength
        s_b = s_a * s_ab + (1 - s_a) * (1 - s_ab) * 0.05
        c_b = tv_a.confidence * tv_ab.confidence * cls.K
        return TruthValue(_clamp(s_b), _clamp(c_b))


class RevisionRule:
    """
    Revision: merge two TVs for the same proposition.
    Delegates to the module-level revision() combinator.
    """

    NAME = "RevisionRule"

    @classmethod
    def apply(cls, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        return revision(tv1, tv2)


# ── Rule registry ─────────────────────────────────────────────────────────────

class PLNRules:
    """
    Registry of all available PLN rules.

    Usage:
        rules = PLNRules()
        tv = rules.deduction.apply(tv_ab, tv_bc)
        tv = rules.modus_ponens.apply(tv_a, tv_ab)
        tv = rules.abduction.apply(tv_symptom, tv_impl)
    """

    def __init__(self):
        self.deduction = DeductionRule()
        self.abduction = AbductionRule()
        self.modus_ponens = ModusPonensRule()
        self.revision = RevisionRule()

    def list_rules(self) -> List[str]:
        return [
            DeductionRule.NAME,
            AbductionRule.NAME,
            ModusPonensRule.NAME,
            RevisionRule.NAME,
        ]

    def combine_symptom_tvs(self, symptom_tvs: List[TruthValue]) -> TruthValue:
        """
        Combine multiple symptom TVs via conjunction + revision.
        Used when a patient has multiple symptoms pointing to one disease.
        """
        if not symptom_tvs:
            return TruthValue.null()
        combined = symptom_tvs[0]
        for tv in symptom_tvs[1:]:
            combined = revision(combined, tv)
        return combined

    def score_diagnosis(self,
                        symptom_tvs: List[TruthValue],
                        disease_prior: float = 0.1) -> TruthValue:
        """
        Compute a final diagnostic TV from a list of supporting symptom TVs.

        Uses AbductionRule for each symptom, then combines via RevisionRule.
        """
        result_tvs = []
        for s_tv in symptom_tvs:
            inferred = AbductionRule.apply(
                TruthValue(1.0, s_tv.confidence),  # symptom is observed
                s_tv,
                prior_disease=disease_prior
            )
            result_tvs.append(inferred)

        if not result_tvs:
            return TruthValue.null()

        combined = result_tvs[0]
        for tv in result_tvs[1:]:
            combined = revision(combined, tv)
        return combined
