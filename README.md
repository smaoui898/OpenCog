# OpenCog Medical Demo

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCog](https://img.shields.io/badge/OpenCog-AtomSpace%20%2B%20PLN-green.svg)](https://opencog.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/smaoui898/OpenCog/blob/main/notebooks/opencog_medical_walkthrough.ipynb)

A demonstration of symbolic AI reasoning with OpenCog's AtomSpace and PLN (Probabilistic Logic Networks) applied to a medical diagnostic knowledge base.

---

## What This Demo Shows

This project demonstrates how OpenCog's AtomSpace (hypergraph knowledge base) and PLN (Probabilistic Logic Networks) are used to:

* Represent medical knowledge as typed atoms and links
* Encode probabilistic inference rules for diagnosis
* Execute backward chaining to answer diagnostic queries
* Perform uncertainty-aware reasoning over symptom-disease relationships
* Integrate a dynamic web visualizer with a live reasoning backend API

---

## Project Structure

```
opencog-medical-demo/
├── README.md
├── requirements.txt
├── server.py                    ← Custom web server and dynamic API
├── demo.html                    ← Interactive web visualizer UI
├── docs/
│   ├── architecture.md          ← AtomSpace + PLN explanation
│   └── slides_reference.md      ← Key concepts
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   ├── atomspace_setup/
│   │   ├── knowledge_base.py    ← Medical KB construction
│   │   └── atom_types.py        ← Atom type definitions
│   ├── pln_reasoning/
│   │   ├── backward_chainer.py  ← PLN queries
│   │   ├── rules.py             ← Inference rules
│   │   └── queries.py           ← Example queries
│   └── demo/
│       └── run_demo.py          ← Interactive CLI entry point
├── notebooks/
│   └── opencog_medical_walkthrough.ipynb
└── tests/
    ├── test_knowledge_base.py
    └── test_pln_queries.py
```

---

## Quick Start

The demo can be run using either a dynamic web interface or an interactive command-line interface.

### Option 1: Dynamic Web Interface (Recommended)

This option launches a custom backend HTTP server that hosts the interactive visualizer and runs real-time PLN inference queries:

1. Start the server:
   ```bash
   py server.py
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:8000/demo.html
   ```
3. Enter patient symptoms (e.g., "ExcessiveThirst, FrequentUrination, Fatigue") and click "Run PLN Inference". Select "Explain Top Diagnosis" to view the live logical abduction chains.

### Option 2: Interactive CLI Demo

This option runs a text-based diagnostic interface inside your terminal:

1. Run the script:
   ```bash
   py -m src.demo.run_demo
   ```
2. Follow the on-screen prompts to input symptoms and view ranked hypotheses and rule explanations.

### Option 3: Google Colab

Run the interactive notebook walkthrough directly in your browser:
[Open in Google Colab](https://colab.research.google.com/github/smaoui898/OpenCog/blob/main/notebooks/opencog_medical_walkthrough.ipynb)

---

## Core Concepts

### AtomSpace
The AtomSpace is OpenCog's hypergraph knowledge store. Nodes and Links represent concepts and relationships. Each atom carries a Truth Value (TV) consisting of a strength and a confidence pair:

```
ConceptNode "Fever"              (strength=0.9, confidence=0.8)
ConceptNode "Influenza"          (strength=0.85, confidence=0.9)
InheritanceLink "Fever" -> "Influenza"  (TV: 0.78, 0.75)
```

### PLN (Probabilistic Logic Networks)
PLN is a formal system for uncertain inference. It combines first-order logic rules with probabilistic truth values using forward and backward chaining. Rules implemented include:
* Abduction (for mapping symptoms back to likely diseases)
* Revision (for combining multiple different symptom observations)
* Deduction
* Modus Ponens

---

## Medical Knowledge Base

The demo includes a curated medical knowledge base with:
* 15+ diseases (Influenza, Common Cold, Pneumonia, Tuberculosis, COVID-19, Diabetes, Hypertension, Heart Disease, Asthma, Migraine, Gastritis, Liver Cirrhosis, Kidney Failure, Anemia, Malaria)
* 20+ symptoms (Fever, Cough, Fatigue, Headache, Sore Throat, Chills, Shortness of Breath, Chest Pain, Night Sweats, Weight Loss, Nausea, Vomiting, Diarrhea, Joint Pain, Muscle Pain, Skin Rash, Blurred Vision, Excessive Thirst, Frequent Urination, Dizziness)
* Probabilistic inheritance links between symptoms and diseases
* Comorbidity relationships (e.g., Diabetes and Hypertension)

---

## Example Queries and Expected Outputs

The engine supports advanced logical diagnostic operations:

### Querying Symptoms

```python
from src.pln_reasoning.queries import diagnose_patient

# Query symptoms for chronic metabolic symptoms
results = diagnose_patient(["ExcessiveThirst", "FrequentUrination", "Fatigue", "BlurredVision"])
for res in results:
    print(res.disease, res.score)
```

Expected output:
* Diabetes: ~91.6% confidence score
* Migraine: ~69.2% confidence score

### Differential Diagnosis

Identify which symptoms differentiate one candidate disease from another:

```python
from src.pln_reasoning.queries import differential_diagnosis

diff = differential_diagnosis("Pneumonia", "Influenza", ["Fever", "Cough", "Fatigue", "ShortBreath"])
print("Present symptoms that differentiate:", diff["differentiating_present"])
```

Expected output:
* Differentiating symptom: Shortness of Breath

---

## Running Tests

Verify the knowledge base and reasoning rules using pytest:

```bash
py -m pytest tests/ -v
```

---

## License

MIT License. See LICENSE for details.
