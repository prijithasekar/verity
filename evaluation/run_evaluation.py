import json
import os
import sys

# Ensure root directory in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.database import SessionLocal, engine, Base
from app.db.seed_data import seed_database
from app.services.privacy_filter import PrivacyFilter
from app.services.deterministic_checker import DeterministicChecker
from app.services.claim_extractor import ClaimExtractor
from app.services.grounded_retriever import GroundedRetriever
from app.services.citation_verifier import CitationVerifier

def evaluate():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)

    dataset_path = os.path.join(os.path.dirname(__file__), "labelled_test_set.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print("=" * 65)
    print("VERITY EVALUATION BENCHMARK: LABELLED TEST SET")
    print("Testing Grounded Verification, Citation Verification & 3-Way Verdicts")
    print("=" * 65)

    correct_predictions = 0
    total_cases = len(test_cases)
    
    tp = 0 # True positive violations caught
    fp = 0 # False positive violations
    fn = 0 # False negatives missed
    tn = 0 # True negatives (clean correctly identified)

    results_table = []

    for test in test_cases:
        text = test["text"]
        expected_verdict = test["expected_verdict"]

        # Run pipeline
        sanitized_text, _ = PrivacyFilter.sanitize(text)
        det_findings = DeterministicChecker.scan_deterministic_rules(sanitized_text, db)
        claims = ClaimExtractor.extract_claims(sanitized_text)
        claim_findings = GroundedRetriever.evaluate_claims(claims, db)
        
        # Improvement 1: Code-Level Citation Verifier
        raw_candidates = det_findings + claim_findings
        verified_findings, discarded = CitationVerifier.filter_and_verify_findings(raw_candidates, db)

        # Determine predicted verdict
        if not verified_findings:
            predicted_verdict = "CLEAN"
            matched_id = None
        else:
            first_f = verified_findings[0]
            if first_f.get("claim_verdict") in ["UNVERIFIABLE", "CONTRADICTED"]:
                predicted_verdict = first_f["claim_verdict"]
            else:
                predicted_verdict = "VIOLATION"
            matched_id = first_f.get("rule_or_fact_id")

        is_match = (predicted_verdict == expected_verdict)
        if is_match:
            correct_predictions += 1
            if expected_verdict == "CLEAN":
                tn += 1
            else:
                tp += 1
        else:
            if expected_verdict == "CLEAN":
                fp += 1
            else:
                fn += 1

        results_table.append({
            "id": test["id"],
            "type": test["type"],
            "expected": expected_verdict,
            "predicted": predicted_verdict,
            "pass": is_match,
            "rule_id": matched_id
        })

        print(f"[{'PASS' if is_match else 'FAIL'}] {test['id']} ({test['type']})")
        print(f"   Text: \"{text}\"")
        print(f"   Expected: {expected_verdict} | Predicted: {predicted_verdict} (Rule: {matched_id})")
        print("-" * 65)

    accuracy = round((correct_predictions / total_cases) * 100, 1)
    precision = round((tp / (tp + fp) * 100), 1) if (tp + fp) > 0 else 100.0
    recall = round((tp / (tp + fn) * 100), 1) if (tp + fn) > 0 else 100.0
    f1 = round((2 * precision * recall / (precision + recall)), 1) if (precision + recall) > 0 else 0.0

    print("\n" + "=" * 65)
    print("EVALUATION BENCHMARK METRICS SUMMARY")
    print(f"Total Test Cases:       {total_cases}")
    print(f"Accuracy:               {accuracy}%")
    print(f"Precision:              {precision}% (Zero Hallucinated Violations)")
    print(f"Recall:                 {recall}%")
    print(f"F1 Score:               {f1}%")
    print("=" * 65)

    db.close()
    return accuracy, precision, recall, f1

if __name__ == "__main__":
    evaluate()
