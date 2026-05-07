"""
run_demo.py
===========
Interactive command-line demonstration of the OpenCog Medical Reasoning System.
"""

import sys
import time
from typing import List

from ..pln_reasoning.queries import (
    diagnose_patient,
    explain_diagnosis,
    list_all_diseases,
    list_all_symptoms
)


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title:^58} ")
    print("=" * 60 + "\n")


def print_results(results: list):
    if not results:
        print("  No matching diseases found for these symptoms.")
        return

    print(f"  {'Rank':<5} | {'Disease Hypothesis':<20} | {'Confidence Score'}")
    print("  " + "-" * 55)
    for i, res in enumerate(results, 1):
        score_pct = res.score * 100
        print(f"  #{i:<4} | {res.disease:<20} | {score_pct:>5.1f}%  "
              f"(TV: s={res.tv.strength:.2f}, c={res.tv.confidence:.2f})")
    print()


def run_interactive_demo():
    print_header("🧠 OpenCog Medical Reasoning Demo 🧠")
    
    print("Loading Knowledge Base into AtomSpace...")
    time.sleep(0.5)
    
    all_symptoms = list_all_symptoms()
    print(f"Loaded {len(list_all_diseases())} diseases and {len(all_symptoms)} symptoms.\n")
    
    print("Available symptoms (examples):")
    print("  " + ", ".join(all_symptoms[:10]) + ", ...\n")

    while True:
        print("-" * 60)
        user_input = input("Enter symptoms separated by commas (or 'quit' to exit):\n> ")
        
        if user_input.lower().strip() in ['quit', 'exit', 'q']:
            print("Exiting demo. Goodbye!")
            break
            
        if not user_input.strip():
            continue

        symptoms = [s.strip() for s in user_input.split(',')]
        
        print(f"\n🔬 Running PLN Backward Chainer for: {symptoms} ...")
        time.sleep(0.5)  # Simulate reasoning time
        
        results = diagnose_patient(symptoms, top_k=5)
        print_results(results)
        
        if results:
            best_disease = results[0].disease
            explain = input(f"Explain top diagnosis ({best_disease})? (y/n) [y]: ")
            if explain.lower() in ['', 'y', 'yes']:
                details = explain_diagnosis(best_disease, symptoms)
                print(f"\n📖 Explanation for {best_disease}:")
                print(f"  - Symptoms matching patient: {details['matched_symptoms']}")
                print(f"  - Missing typical symptoms : {details['unmatched_symptoms']}")
                print("  - PLN Inference Chain:")
                for rule in details['rule_chain']:
                    print(f"      {rule}")
                print()


if __name__ == "__main__":
    try:
        run_interactive_demo()
    except KeyboardInterrupt:
        print("\nExiting demo. Goodbye!")
        sys.exit(0)
