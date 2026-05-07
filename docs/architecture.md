# OpenCog Medical Demo — Architecture Overview

## 🏛 Overview

This document describes the technical architecture of the OpenCog Medical Demo, focusing on two core components:

1. **AtomSpace** — the hypergraph knowledge representation layer
2. **PLN (Probabilistic Logic Networks)** — the inference and reasoning engine

---

## 1. AtomSpace

### What Is AtomSpace?

AtomSpace is OpenCog's **in-memory hypergraph database**. All knowledge is stored as **Atoms**, which are either:

- **Nodes** — represent concepts (e.g., `ConceptNode "Fever"`)
- **Links** — represent relationships between atoms (e.g., `InheritanceLink`)

Each atom carries a **TruthValue (TV)**:
```
TruthValue = (strength s, confidence c)
  s ∈ [0, 1]   ← probability of truth
  c ∈ [0, 1]   ← confidence in that probability
```

### Medical KB Atom Types

| Atom Type        | Example                                  | Meaning                              |
|------------------|------------------------------------------|--------------------------------------|
| `ConceptNode`    | `ConceptNode "Influenza"`                | A medical concept                    |
| `PredicateNode`  | `PredicateNode "has_symptom"`            | A predicate/relation                 |
| `InheritanceLink`| `Inheritance: Fever → Influenza`         | Fever is inherited by Influenza      |
| `EvaluationLink` | `Eval(has_symptom, Patient, Fever)`      | A patient has symptom Fever          |
| `ImplicationLink`| `Fever ∧ Cough → Influenza (TV: 0.78)`  | Probabilistic implication rule       |

### AtomSpace Diagram

```
                    ┌─────────────────────────┐
                    │       AtomSpace          │
                    │                          │
    ConceptNode ────►  "Fever"   TV(0.9, 0.8)  │
                    │      │                   │
                    │      │ InheritanceLink    │
                    │      ▼                   │
    ConceptNode ────►  "Influenza" TV(0.85,0.9)│
                    │      │                   │
                    │      │ ImplicationLink    │
                    │      ▼                   │
    PredicateNode ──►  "diagnose"              │
                    └─────────────────────────┘
```

---

## 2. PLN — Probabilistic Logic Networks

### What Is PLN?

PLN is a **formal system for uncertain inference**. It extends classical logic by attaching probabilities to every logical statement and inference step.

### Core PLN Rules Used

#### 2.1 Deduction Rule
If A → B and B → C, then A → C

```
TV_AC.strength = TV_AB.s * TV_BC.s
TV_AC.confidence = TV_AB.c * TV_BC.c * k
```

#### 2.2 Modus Ponens (with uncertainty)
If P(A) and P(A→B), infer P(B):

```
P(B) = P(A) * P(A→B) + P(¬A) * P(¬A→B)
```

#### 2.3 Abduction Rule (for diagnosis)
If Symptoms → Disease, given Symptoms, infer Disease:

```
P(Disease | Symptoms) ∝ P(Symptoms | Disease) * P(Disease)
```

### Backward Chaining

Backward chaining starts from a **goal** and works backward to find supporting evidence:

```
Goal: diagnose(Patient, ?Disease)
   ↓
Find all ImplicationLinks: Symptom → ?Disease
   ↓
Check if Patient has each Symptom
   ↓
Aggregate truth values using PLN rules
   ↓
Return ranked diagnoses with TV scores
```

### PLN Inference Flow

```
Query: "What disease does Patient X have?"
         │
         ▼
   [Backward Chainer]
         │
    ┌────┴────┐
    │         │
    ▼         ▼
[Rule Base] [AtomSpace]
    │         │
    └────┬────┘
         │
    [TV Combiner]
         │
         ▼
  [Ranked Results]
  Disease A: TV(0.82, 0.75)
  Disease B: TV(0.61, 0.68)
  Disease C: TV(0.43, 0.55)
```

---

## 3. System Architecture

```
┌──────────────────────────────────────────────────────┐
│                   Demo Entry Point                   │
│                   run_demo.py                        │
└──────────────┬───────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌──────────────────┐
│ AtomSpace    │  │  PLN Reasoner    │
│ Setup        │  │                  │
│              │  │ ┌──────────────┐ │
│ knowledge_   │  │ │backward_     │ │
│ base.py      │◄─┼─│chainer.py    │ │
│              │  │ └──────────────┘ │
│ atom_types   │  │ ┌──────────────┐ │
│ .py          │  │ │rules.py      │ │
└──────────────┘  │ └──────────────┘ │
                  │ ┌──────────────┐ │
                  │ │queries.py    │ │
                  │ └──────────────┘ │
                  └──────────────────┘
```

---

## 4. Data Flow

1. **Knowledge Ingestion**: `knowledge_base.py` populates AtomSpace with medical concepts, symptoms, diseases, and their probabilistic relationships.
2. **Rule Loading**: `rules.py` defines PLN inference rules (Deduction, Modus Ponens, Abduction).
3. **Query Execution**: `queries.py` sends diagnostic queries; `backward_chainer.py` resolves them using PLN.
4. **Result Presentation**: Results are ranked by TV strength × confidence and displayed.

---

## 5. Truth Value Semantics in Medicine

| TV Strength Range | Interpretation                    |
|-------------------|-----------------------------------|
| 0.90 – 1.00       | Very strong association           |
| 0.70 – 0.89       | Strong association                |
| 0.50 – 0.69       | Moderate association              |
| 0.30 – 0.49       | Weak association                  |
| 0.00 – 0.29       | Very weak / unlikely              |
