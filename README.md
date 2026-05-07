<<<<<<< HEAD
# 🧠 OpenCog Medical Demo

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenCog](https://img.shields.io/badge/OpenCog-AtomSpace%20%2B%20PLN-green.svg)](https://opencog.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/your-username/opencog-medical-demo/blob/main/notebooks/opencog_medical_walkthrough.ipynb)

> **A full demonstration of symbolic AI reasoning with OpenCog's AtomSpace and PLN (Probabilistic Logic Networks) applied to a medical diagnostic knowledge base.**

---

## 🎯 What This Demo Shows

This project demonstrates how OpenCog's **AtomSpace** (hypergraph knowledge base) and **PLN** (Probabilistic Logic Networks) can be used to:

- Represent medical knowledge as typed atoms and links
- Encode probabilistic inference rules for diagnosis
- Execute backward chaining to answer diagnostic queries
- Perform uncertainty-aware reasoning over symptom-disease relationships

---

## 🗂 Project Structure

```
opencog-medical-demo/
├── README.md
├── requirements.txt
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
│       └── run_demo.py          ← Main entry point
├── notebooks/
│   └── opencog_medical_walkthrough.ipynb
└── tests/
    ├── test_knowledge_base.py
    └── test_pln_queries.py
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/your-username/opencog-medical-demo.git
cd opencog-medical-demo
docker-compose -f docker/docker-compose.yml up
```

### Option 2: Local Installation

```bash
# Clone the repo
git clone https://github.com/your-username/opencog-medical-demo.git
cd opencog-medical-demo

# Install dependencies
pip install -r requirements.txt

# Run the demo
python -m src.demo.run_demo
```

### Option 3: Google Colab

Click the Colab badge above to run the interactive walkthrough directly in your browser — no setup required.

---

## 🧠 Core Concepts

### AtomSpace
The **AtomSpace** is OpenCog's hypergraph knowledge store. Nodes and Links represent concepts and relationships. Each atom carries a **Truth Value (TV)** — a strength and confidence pair.

```
ConceptNode "Fever"              (strength=0.9, confidence=0.8)
ConceptNode "Influenza"          (strength=0.85, confidence=0.9)
InheritanceLink "Fever" → "Influenza"  (TV: 0.78, 0.75)
```

### PLN (Probabilistic Logic Networks)
**PLN** is a formal system for uncertain inference. It combines:
- First-order logic rules
- Probabilistic truth values
- Backward/forward chaining

---

## 📊 Medical Knowledge Base

The demo includes a curated medical KB with:
- **20+ diseases** (Influenza, Pneumonia, Diabetes, etc.)
- **30+ symptoms** (Fever, Cough, Fatigue, etc.)
- **Probabilistic inheritance links** between symptoms and diseases
- **Comorbidity relationships**

---

## 🔬 Example Query

```python
from src.pln_reasoning.queries import diagnose_patient

# Patient presents with: Fever, Cough, Fatigue
results = diagnose_patient(symptoms=["Fever", "Cough", "Fatigue"])
# Returns ranked list of probable diagnoses with confidence scores
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📚 Documentation

- [Architecture Overview](docs/architecture.md)
- [Slides & References](docs/slides_reference.md)

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

[MIT](LICENSE) © 2024
=======
# OpenCog
OpenCog Towards Artificial General Intelligence
>>>>>>> 2c878397a631db9c31022af3607a6be0cecb4973
