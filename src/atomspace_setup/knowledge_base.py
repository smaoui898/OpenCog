"""
knowledge_base.py
=================
Constructs the medical knowledge base in the AtomSpace.

Diseases covered:
  Influenza, CommonCold, Pneumonia, Tuberculosis, COVID19,
  Diabetes, Hypertension, HeartDisease, Asthma, Migraine,
  Gastritis, LiverCirrhosis, KidneyFailure, Anemia, Malaria

Symptoms covered:
  Fever, Cough, Fatigue, Headache, SoreThroat, Chills,
  ShortBreath, ChestPain, NightSweats, WeightLoss, Nausea,
  Vomiting, Diarrhea, JointPain, MusclePain, SkinRash,
  BlurredVision, ExcessiveThirst, FrequentUrination, Dizziness
"""

from typing import Dict, List, Optional, Tuple
from .atom_types import (
    TruthValue, ConceptNode, PredicateNode,
    InheritanceLink, EvaluationLink, ImplicationLink,
    ListLink, MemberLink, AndLink
)


# ── Lightweight AtomSpace container (pure Python) ─────────────────────────────

class AtomSpace:
    """Minimal AtomSpace: stores atoms and provides lookup utilities."""

    def __init__(self):
        self._atoms: Dict[str, object] = {}
        self._nodes: Dict[Tuple[str, str], object] = {}  # (type_value, name) -> atom
        self._links: List[object] = []

    def add(self, atom):
        """Add an atom to the space; returns the atom."""
        self._atoms[atom.handle] = atom
        if atom.is_node():
            key = (atom.atom_type.value, atom.name)
            self._nodes[key] = atom
        else:
            self._links.append(atom)
        return atom

    def get_node(self, type_name: str, name: str):
        """Retrieve a node by type string and name, or None."""
        return self._nodes.get((type_name, name))

    def get_all_nodes(self, type_name: Optional[str] = None) -> list:
        if type_name is None:
            return [a for a in self._atoms.values() if hasattr(a, 'name')]
        return [a for (t, _), a in self._nodes.items() if t == type_name]

    def get_all_links(self, type_name: Optional[str] = None) -> list:
        if type_name is None:
            return self._links
        return [l for l in self._links if l.atom_type.value == type_name]

    def size(self) -> int:
        return len(self._atoms)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _concept(space: AtomSpace, name: str,
             tv: Optional[TruthValue] = None) -> ConceptNode:
    """Get or create a ConceptNode."""
    existing = space.get_node("ConceptNode", name)
    if existing:
        if tv:
            existing.tv = tv
        return existing
    node = ConceptNode(name, tv or TruthValue(1.0, 0.5))
    space.add(node)
    return node


def _predicate(space: AtomSpace, name: str) -> PredicateNode:
    existing = space.get_node("PredicateNode", name)
    if existing:
        return existing
    node = PredicateNode(name)
    space.add(node)
    return node


def _inheritance(space: AtomSpace, src_name: str, tgt_name: str,
                 strength: float, confidence: float):
    src = _concept(space, src_name)
    tgt = _concept(space, tgt_name)
    link = InheritanceLink(src, tgt, tv=TruthValue(strength, confidence))
    space.add(link)
    return link


def _implication(space: AtomSpace, antecedent, consequent_name: str,
                 strength: float, confidence: float):
    consequent = _concept(space, consequent_name)
    link = ImplicationLink(antecedent, consequent,
                           tv=TruthValue(strength, confidence))
    space.add(link)
    return link


def _has_symptom(space: AtomSpace, disease_name: str, symptom_name: str,
                 strength: float, confidence: float):
    """Add: disease has_symptom symptom (as EvaluationLink)."""
    pred = _predicate(space, "has_symptom")
    disease = _concept(space, disease_name)
    symptom = _concept(space, symptom_name)
    args = ListLink(disease, symptom)
    space.add(args)
    link = EvaluationLink(pred, args, tv=TruthValue(strength, confidence))
    space.add(link)
    return link


# ── Main KB Builder ───────────────────────────────────────────────────────────

class MedicalKnowledgeBase:
    """
    Medical knowledge base backed by an AtomSpace.

    Usage:
        kb = MedicalKnowledgeBase()
        kb.build()
        space = kb.atomspace
    """

    def __init__(self):
        self.atomspace = AtomSpace()
        self._built = False

    def build(self) -> "MedicalKnowledgeBase":
        """Populate the AtomSpace with all medical knowledge."""
        if self._built:
            return self
        space = self.atomspace
        self._add_disease_categories(space)
        self._add_symptom_disease_links(space)
        self._add_implication_rules(space)
        self._add_comorbidities(space)
        self._built = True
        print(f"[KB] AtomSpace built — {space.size()} atoms loaded.")
        return self

    # ── Disease categories ────────────────────────────────────────────────────

    def _add_disease_categories(self, space: AtomSpace):
        categories = {
            "InfectiousDisease":  ["Influenza", "CommonCold", "Pneumonia",
                                   "Tuberculosis", "COVID19", "Malaria"],
            "ChronicDisease":     ["Diabetes", "Hypertension", "HeartDisease",
                                   "Asthma", "LiverCirrhosis", "KidneyFailure"],
            "NeurologicalDisease":["Migraine"],
            "GastrointestinalDisease": ["Gastritis"],
            "BloodDisease":       ["Anemia"],
        }
        for category, diseases in categories.items():
            cat_node = _concept(space, category, TruthValue(1.0, 0.9))
            for disease in diseases:
                dis_node = _concept(space, disease, TruthValue(1.0, 0.9))
                link = MemberLink(dis_node, cat_node,
                                  tv=TruthValue(1.0, 0.95))
                space.add(link)

    # ── Symptom → Disease links ───────────────────────────────────────────────

    def _add_symptom_disease_links(self, space: AtomSpace):
        data = [
            # (disease, symptom, strength, confidence)
            # ── Influenza
            ("Influenza",    "Fever",            0.92, 0.90),
            ("Influenza",    "Cough",             0.88, 0.88),
            ("Influenza",    "Fatigue",           0.85, 0.85),
            ("Influenza",    "MusclePain",        0.80, 0.82),
            ("Influenza",    "Headache",          0.75, 0.80),
            ("Influenza",    "Chills",            0.78, 0.83),
            ("Influenza",    "SoreThroat",        0.65, 0.75),
            # ── CommonCold
            ("CommonCold",   "SoreThroat",        0.90, 0.88),
            ("CommonCold",   "Cough",             0.85, 0.86),
            ("CommonCold",   "Headache",          0.60, 0.70),
            ("CommonCold",   "Fatigue",           0.55, 0.65),
            ("CommonCold",   "Fever",             0.35, 0.60),
            # ── Pneumonia
            ("Pneumonia",    "Fever",             0.88, 0.90),
            ("Pneumonia",    "Cough",             0.90, 0.92),
            ("Pneumonia",    "ShortBreath",       0.85, 0.88),
            ("Pneumonia",    "ChestPain",         0.78, 0.82),
            ("Pneumonia",    "Fatigue",           0.80, 0.85),
            ("Pneumonia",    "Chills",            0.72, 0.78),
            # ── Tuberculosis
            ("Tuberculosis", "Cough",             0.95, 0.92),
            ("Tuberculosis", "NightSweats",       0.88, 0.87),
            ("Tuberculosis", "WeightLoss",        0.85, 0.88),
            ("Tuberculosis", "Fever",             0.80, 0.82),
            ("Tuberculosis", "Fatigue",           0.82, 0.85),
            ("Tuberculosis", "ChestPain",         0.70, 0.75),
            # ── COVID19
            ("COVID19",      "Fever",             0.85, 0.90),
            ("COVID19",      "Cough",             0.88, 0.90),
            ("COVID19",      "Fatigue",           0.82, 0.85),
            ("COVID19",      "ShortBreath",       0.78, 0.82),
            ("COVID19",      "HeadAche",          0.70, 0.75),
            ("COVID19",      "Diarrhea",          0.45, 0.60),
            # ── Diabetes
            ("Diabetes",     "ExcessiveThirst",   0.92, 0.90),
            ("Diabetes",     "FrequentUrination", 0.90, 0.90),
            ("Diabetes",     "Fatigue",           0.80, 0.82),
            ("Diabetes",     "BlurredVision",     0.75, 0.78),
            ("Diabetes",     "WeightLoss",        0.65, 0.70),
            # ── Hypertension
            ("Hypertension", "Headache",          0.72, 0.75),
            ("Hypertension", "Dizziness",         0.70, 0.72),
            ("Hypertension", "ChestPain",         0.65, 0.70),
            ("Hypertension", "BlurredVision",     0.60, 0.65),
            # ── HeartDisease
            ("HeartDisease", "ChestPain",         0.90, 0.92),
            ("HeartDisease", "ShortBreath",       0.85, 0.88),
            ("HeartDisease", "Fatigue",           0.80, 0.82),
            ("HeartDisease", "Dizziness",         0.72, 0.75),
            # ── Asthma
            ("Asthma",       "ShortBreath",       0.95, 0.93),
            ("Asthma",       "Cough",             0.85, 0.85),
            ("Asthma",       "ChestPain",         0.70, 0.72),
            # ── Migraine
            ("Migraine",     "Headache",          0.97, 0.95),
            ("Migraine",     "Nausea",            0.75, 0.78),
            ("Migraine",     "BlurredVision",     0.65, 0.68),
            ("Migraine",     "Dizziness",         0.60, 0.65),
            # ── Gastritis
            ("Gastritis",    "Nausea",            0.88, 0.87),
            ("Gastritis",    "Vomiting",          0.82, 0.83),
            ("Gastritis",    "ChestPain",         0.60, 0.65),
            ("Gastritis",    "Fatigue",           0.55, 0.60),
            # ── Malaria
            ("Malaria",      "Fever",             0.95, 0.93),
            ("Malaria",      "Chills",            0.90, 0.90),
            ("Malaria",      "Headache",          0.80, 0.82),
            ("Malaria",      "MusclePain",        0.75, 0.78),
            ("Malaria",      "Fatigue",           0.80, 0.82),
            ("Malaria",      "Nausea",            0.65, 0.68),
            # ── Anemia
            ("Anemia",       "Fatigue",           0.92, 0.90),
            ("Anemia",       "Dizziness",         0.80, 0.82),
            ("Anemia",       "ShortBreath",       0.72, 0.75),
            ("Anemia",       "HeadAche",          0.60, 0.65),
        ]
        for disease, symptom, s, c in data:
            _has_symptom(space, disease, symptom, s, c)
            # Also add InheritanceLink: symptom → disease
            _inheritance(space, symptom, disease, s * 0.85, c * 0.90)

    # ── PLN Implication rules ─────────────────────────────────────────────────

    def _add_implication_rules(self, space: AtomSpace):
        """Add composite ImplicationLinks: symptom combinations → diseases."""
        # Fever + Cough → Influenza
        fever = _concept(space, "Fever")
        cough = _concept(space, "Cough")
        fatigue = _concept(space, "Fatigue")
        night_sweats = _concept(space, "NightSweats")
        weight_loss = _concept(space, "WeightLoss")
        chest_pain = _concept(space, "ChestPain")
        short_breath = _concept(space, "ShortBreath")
        thirst = _concept(space, "ExcessiveThirst")
        urination = _concept(space, "FrequentUrination")

        combos = [
            (AndLink(fever, cough),            "Influenza",    0.82, 0.80),
            (AndLink(fever, cough, fatigue),   "Influenza",    0.88, 0.85),
            (AndLink(cough, night_sweats),     "Tuberculosis", 0.85, 0.82),
            (AndLink(cough, night_sweats,
                     weight_loss),             "Tuberculosis", 0.92, 0.88),
            (AndLink(chest_pain, short_breath),"HeartDisease", 0.88, 0.85),
            (AndLink(thirst, urination),       "Diabetes",     0.90, 0.87),
            (AndLink(fever, cough,
                     short_breath),            "COVID19",      0.80, 0.78),
            (AndLink(fever, cough,
                     short_breath),            "Pneumonia",    0.82, 0.80),
        ]
        for antecedent, disease, s, c in combos:
            space.add(antecedent)
            _implication(space, antecedent, disease, s, c)

    # ── Comorbidities ─────────────────────────────────────────────────────────

    def _add_comorbidities(self, space: AtomSpace):
        """Add comorbidity links using SimilarityLink-style InheritanceLinks."""
        pairs = [
            ("Diabetes",      "Hypertension",  0.65, 0.70),
            ("Diabetes",      "HeartDisease",  0.60, 0.65),
            ("Hypertension",  "HeartDisease",  0.70, 0.72),
            ("Asthma",        "Pneumonia",     0.45, 0.55),
            ("LiverCirrhosis","Anemia",        0.55, 0.60),
        ]
        comorbid = _predicate(self.atomspace, "comorbid_with")
        for d1, d2, s, c in pairs:
            n1 = _concept(self.atomspace, d1)
            n2 = _concept(self.atomspace, d2)
            args = ListLink(n1, n2)
            self.atomspace.add(args)
            link = EvaluationLink(comorbid, args, tv=TruthValue(s, c))
            self.atomspace.add(link)

    # ── Convenience methods ───────────────────────────────────────────────────

    def get_diseases(self) -> List[str]:
        """Return all disease concept names."""
        disease_names = [
            "Influenza", "CommonCold", "Pneumonia", "Tuberculosis", "COVID19",
            "Diabetes", "Hypertension", "HeartDisease", "Asthma", "Migraine",
            "Gastritis", "LiverCirrhosis", "KidneyFailure", "Anemia", "Malaria"
        ]
        return disease_names

    def get_symptoms(self) -> List[str]:
        """Return all symptom concept names."""
        return [
            "Fever", "Cough", "Fatigue", "Headache", "SoreThroat", "Chills",
            "ShortBreath", "ChestPain", "NightSweats", "WeightLoss", "Nausea",
            "Vomiting", "Diarrhea", "JointPain", "MusclePain", "SkinRash",
            "BlurredVision", "ExcessiveThirst", "FrequentUrination", "Dizziness"
        ]

    def get_symptom_links_for_disease(self, disease_name: str) -> list:
        """Return all EvaluationLinks where the disease has a symptom."""
        results = []
        for link in self.atomspace.get_all_links("EvaluationLink"):
            if (hasattr(link, 'predicate') and
                    link.predicate.name == "has_symptom"):
                args = link.arguments.outgoing
                if args and args[0].name == disease_name:
                    results.append(link)
        return results
