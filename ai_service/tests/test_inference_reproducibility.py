import pytest
import pandas as pd
import numpy as np
from ai_service.app.core.config import settings
from ai_service.app.services.inference_service import inference_service

@pytest.fixture(scope="module")
def initialized_inference_service():
    """Ensure the inference service is initialized once for tests."""
    if not inference_service.is_initialized:
        inference_service.initialize()
    return inference_service

def test_inference_initialization(initialized_inference_service):
    """Verifies that the inference service initializes with the exact research dimensions."""
    svc = initialized_inference_service
    assert svc.is_initialized is True
    assert svc.graph_data is not None
    assert svc.graph_data.num_nodes == 5977
    assert svc.graph_data.num_edges == 43044
    assert len(svc.relation_to_id) == 12
    assert svc.graph_data.num_node_features == 82
    assert len(svc.node_maps["application"]) == 4000
    assert len(svc.node_maps["student"]) == 1534
    assert len(svc.node_maps["company"]) == 125
    assert len(svc.node_maps["job"]) == 300
    assert len(svc.node_maps["skill"]) == 18

def test_all_4000_applications_bit_parity(initialized_inference_service):
    """
    Core regression test:
    Loads all 4,000 historical applications from Codebase/AMRG_GraphSAGE_predictions.csv
    and verifies that the AI inference service reproduces each prediction with
    max_absolute_difference < 1e-6.
    """
    svc = initialized_inference_service

    # Load frozen predictions from research CSV
    predictions_csv_path = settings.PREDICTIONS_CSV_PATH
    assert predictions_csv_path.exists(), f"Ground truth CSV not found: {predictions_csv_path}"
    df_expected = pd.read_csv(predictions_csv_path)
    assert len(df_expected) == 4000, f"Expected 4000 rows, found {len(df_expected)}"

    # Run inference across all applications via inference service
    all_actual_probs = svc.get_all_application_predictions()
    assert len(all_actual_probs) == 4000

    differences = []
    status_mismatches = 0

    for row in df_expected.itertuples(index=False):
        app_id = str(row.application_id)
        expected_prob = float(row.predicted_probability)
        expected_status = int(row.predicted_status)

        assert app_id in all_actual_probs, f"Application {app_id} missing from model predictions."
        actual_prob = all_actual_probs[app_id]
        actual_status = 1 if actual_prob >= 0.5 else 0

        diff = abs(expected_prob - actual_prob)
        differences.append(diff)

        if expected_status != actual_status:
            status_mismatches += 1

    max_diff = max(differences)
    mean_diff = float(np.mean(differences))

    print(f"\n[PARITY VERIFICATION] Total applications: {len(differences)}")
    print(f"[PARITY VERIFICATION] Status mismatches: {status_mismatches}")
    print(f"[PARITY VERIFICATION] Maximum absolute difference: {max_diff:.16e}")
    print(f"[PARITY VERIFICATION] Mean absolute difference: {mean_diff:.16e}")

    # Enforce strict tolerance
    assert status_mismatches == 0, f"Found {status_mismatches} predicted status mismatches!"
    assert max_diff < 1e-6, f"Max difference {max_diff:.16e} exceeds tolerance 1e-6!"

def test_known_research_benchmarks():
    """
    Verifies that the research comparison table preserved in Codebase/GraphSAGE_model_comparison.csv
    matches the verified research values.
    """
    comparison_csv_path = settings.COMPARISON_CSV_PATH
    assert comparison_csv_path.exists(), f"Comparison CSV not found: {comparison_csv_path}"
    df_comp = pd.read_csv(comparison_csv_path).set_index("Metric")

    expected_baseline = {
        "Accuracy": 0.8387,
        "Precision": 0.8443,
        "Recall": 0.8699,
        "F1": 0.8569,
        "ROC-AUC": 0.9140
    }

    expected_amrg = {
        "Accuracy": 0.8427,
        "Precision": 0.8493,
        "Recall": 0.8714,
        "F1": 0.8602,
        "ROC-AUC": 0.9142
    }

    for metric, exp_val in expected_baseline.items():
        val = df_comp.loc[metric, "Standard_GraphSAGE"]
        assert abs(val - exp_val) < 1e-3, f"Baseline {metric} mismatch: {val} vs {exp_val}"

    for metric, exp_val in expected_amrg.items():
        val = df_comp.loc[metric, "AMRG_GraphSAGE"]
        assert abs(val - exp_val) < 1e-3, f"AMRG {metric} mismatch: {val} vs {exp_val}"
