import pytest
from src.pln_reasoning.queries import diagnose_patient, explain_diagnosis
from src.pln_reasoning.rules import AbductionRule, TruthValue

def test_abduction_rule():
    tv_symptom = TruthValue(1.0, 0.9)
    tv_implication = TruthValue(0.8, 0.8)
    
    result = AbductionRule.apply(tv_symptom, tv_implication, prior_disease=0.1)
    assert result.strength > 0
    assert result.confidence > 0
    assert result.confidence <= 1.0

def test_diagnose_patient():
    # Fever and Cough strongly suggest Influenza or Pneumonia or COVID19
    results = diagnose_patient(["Fever", "Cough"])
    assert len(results) > 0
    
    top_diseases = [r.disease for r in results[:3]]
    assert "Influenza" in top_diseases or "Pneumonia" in top_diseases

def test_explain_diagnosis():
    explanation = explain_diagnosis("Influenza", ["Fever", "Cough"])
    assert explanation["disease"] == "Influenza"
    assert "Fever" in explanation["matched_symptoms"]
    assert "Cough" in explanation["matched_symptoms"]
    assert len(explanation["rule_chain"]) == 2
