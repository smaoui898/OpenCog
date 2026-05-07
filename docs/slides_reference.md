# Slides & Key Concepts Reference

## 📖 Introduction to OpenCog

### Official Resources
- **OpenCog Wiki**: https://wiki.opencog.org/
- **AtomSpace GitHub**: https://github.com/opencog/atomspace
- **PLN Book**: *Probabilistic Logic Networks* — Ben Goertzel et al.
- **OpenCog Book**: https://opencog.org/doc/

---

## 🎓 Concepts Covered in This Demo

### 1. Symbolic AI vs Connectionist AI

| Feature          | Symbolic (OpenCog)         | Connectionist (Deep Learning) |
|------------------|----------------------------|-------------------------------|
| Representation   | Explicit atoms & links     | Distributed weights           |
| Interpretability | High (readable rules)      | Low (black box)               |
| Sample Efficiency| High (prior knowledge)     | Low (needs big data)          |
| Uncertainty      | Explicit TV scores         | Implicit (softmax)            |
| Reasoning        | Deductive + inductive      | Pattern matching only         |

---

### 2. AtomSpace Concepts

| Concept          | Slide Reference | Description                                      |
|------------------|-----------------|--------------------------------------------------|
| Node             | Slide 3         | Atomic concept (ConceptNode, PredicateNode, etc.)|
| Link             | Slide 4         | Relationship between atoms                        |
| TruthValue       | Slide 5         | (strength, confidence) pair on every atom         |
| SimpleTruthValue | Slide 6         | Most common TV type                               |
| Attention Value  | Slide 7         | Controls working memory allocation (STI/LTI)     |
| Pattern Matcher  | Slide 10        | Query engine for the hypergraph                  |

---

### 3. PLN Concepts

| Concept           | Slide Reference | Description                                         |
|-------------------|-----------------|-----------------------------------------------------|
| Forward Chaining  | Slide 12        | Start from facts, derive conclusions                |
| Backward Chaining | Slide 13        | Start from goal, find supporting facts              |
| Deduction Rule    | Slide 14        | A→B, B→C ⊢ A→C with TV propagation                |
| Induction Rule    | Slide 15        | Generalize from specific observations               |
| Abduction Rule    | Slide 16        | Infer cause from effect (core for diagnosis)       |
| Modus Ponens      | Slide 17        | If A and A→B, then B                               |
| TV Revision       | Slide 18        | Combine multiple evidence sources                   |

---

### 4. Medical AI Application

| Concept           | Slide Reference | Description                                         |
|-------------------|-----------------|-----------------------------------------------------|
| Symptom-Disease   | Slide 20        | Probabilistic mapping of symptoms to diseases       |
| Knowledge Base    | Slide 21        | Structured medical ontology in AtomSpace            |
| Diagnostic Query  | Slide 22        | PLN backward chaining for diagnosis                 |
| Uncertainty       | Slide 23        | Managing diagnostic uncertainty with TV scores      |
| Comorbidity       | Slide 24        | Modeling multiple co-occurring diseases             |

---

## 📚 Further Reading

### OpenCog Papers
1. Goertzel, B. (2014). *Artificial General Intelligence: Concept, State of the Art, and Future Prospects*. Journal of Artificial General Intelligence.
2. Goertzel, B. et al. (2008). *Probabilistic Logic Networks*. Springer.
3. Looks, M. et al. (2004). *Competent Program Evolution*. GECCO.

### Medical AI with Symbolic Systems
1. Shortliffe, E.H. (1976). *MYCIN: Computer-based Medical Consultations*. Elsevier. ← Original expert system
2. Miller, R.A. (1994). *Medical diagnostic decision support systems — past, present, and future*. JAMIA.
3. Szolovits, P. (1982). *Artificial Intelligence in Medicine*. AAAS.

### Related Projects
- **OpenCog AtomSpace**: https://github.com/opencog/atomspace
- **PLN Implementation**: https://github.com/opencog/pln
- **Ure (Unified Rule Engine)**: https://github.com/opencog/ure
- **OpenCog Examples**: https://github.com/opencog/opencog/tree/master/examples

---

## 🔗 Useful Links

| Resource                     | URL                                              |
|------------------------------|--------------------------------------------------|
| OpenCog Official Site        | https://opencog.org/                             |
| AtomSpace Tutorial           | https://wiki.opencog.org/w/AtomSpace             |
| PLN Documentation            | https://wiki.opencog.org/w/PLN                   |
| OpenCog GitHub               | https://github.com/opencog/opencog               |
| Mailing List                 | https://groups.google.com/g/opencog              |
| Ben Goertzel's Blog          | https://multiverseaccordingtoben.blogspot.com/   |

---

## 🎬 Video Resources

- **OpenCog Introduction** (YouTube): Search "OpenCog Ben Goertzel introduction"
- **PLN Tutorial** (YouTube): Search "Probabilistic Logic Networks tutorial"
- **AGI Conference Talks**: https://agi-conf.org/
