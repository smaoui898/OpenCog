import pytest
from src.atomspace_setup.knowledge_base import MedicalKnowledgeBase
from src.atomspace_setup.atom_types import TruthValue

def test_kb_initialization():
    kb = MedicalKnowledgeBase().build()
    assert kb.atomspace.size() > 0
    
    diseases = kb.get_diseases()
    assert "Influenza" in diseases
    assert "COVID19" in diseases

def test_symptom_links():
    kb = MedicalKnowledgeBase().build()
    links = kb.get_symptom_links_for_disease("Influenza")
    
    symptoms = [lnk.arguments.outgoing[1].name for lnk in links]
    assert "Fever" in symptoms
    assert "Cough" in symptoms

def test_atomspace_retrieval():
    kb = MedicalKnowledgeBase().build()
    node = kb.atomspace.get_node("ConceptNode", "Fever")
    assert node is not None
    assert node.name == "Fever"
    assert isinstance(node.tv, TruthValue)
