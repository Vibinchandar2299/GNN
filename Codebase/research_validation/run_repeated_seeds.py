"""
Multiple-Seed Research Validation Script for HireGraph AI.

Performs rigorous repeated-seed evaluation across 5 random seeds:
[42, 123, 456, 789, 2026]
for:
1. Standard GraphSAGE (Baseline)
2. Full AMRG-GraphSAGE (Proposed)

Strictly uses identical:
- Dataset and preprocessed features (82-dim, fitted strictly on 2023-2024)
- Global graph structure (5,977 nodes, 43,044 edges, 12 relations)
- Temporal evaluation split (Train: 2023-2024, Val: 2025, Test: 2026)
- Training protocol and hyperparameters

Outputs:
- repeated_seed_results.csv (detailed results per seed)
- repeated_seed_summary.csv (mean and standard deviation per metric)
"""

import os
import sys
import time

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import pandas as pd
import numpy as np
import torch

from Codebase.research_validation.data_loader import load_dataset_and_graph
from Codebase.research_validation.models import BaselineGraphSAGE, AMRGGraphSAGE
from Codebase.research_validation.train_utils import set_seed, train_model, evaluate_model

RESULTS_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\results"
CODEBASE_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase"
SEEDS = [42, 123, 456, 789, 2026]


def run_repeated_seeds_validation():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 76, flush=True)
    print("STARTING MULTIPLE-SEED VALIDATION", flush=True)
    print(f"Seeds to evaluate: {SEEDS}", flush=True)
    print("=" * 76, flush=True)

    data, relation_to_id, _ = load_dataset_and_graph(use_cache=True)
    in_channels = data.num_node_features
    num_relations = len(relation_to_id)

    seed_results = []

    for seed in SEEDS:
        print(f"\n>>> EXECUTING SEED {seed} <<<", flush=True)

        # 1. Standard GraphSAGE Baseline
        print(f"\n[Seed {seed}] Training Standard GraphSAGE Baseline...", flush=True)
        set_seed(seed)
        base_model = BaselineGraphSAGE(
            in_channels=in_channels,
            hidden_channels=64,
            num_layers=2,
            dropout=0.30
        )
        t0 = time.time()
        base_model, _, _, best_epoch, total_epochs = train_model(
            model=base_model,
            graph=data,
            epochs=120,
            lr=1e-3,
            weight_decay=1e-4,
            ranking_lambda=0.0,
            patience=15,
            pos_weight=1.0,
            seed=seed,
            verbose=False
        )
        base_elapsed = time.time() - t0
        base_test_res, _, _, _ = evaluate_model(base_model, data, data.test_mask)
        print(f"  Standard GraphSAGE [Seed {seed}] (Time: {base_elapsed:.1f}s, Epochs: {total_epochs}, Best: {best_epoch}): "
              f"Acc={base_test_res['Accuracy']:.4f}, Prec={base_test_res['Precision']:.4f}, "
              f"Rec={base_test_res['Recall']:.4f}, F1={base_test_res['F1']:.4f}, ROC-AUC={base_test_res['ROC-AUC']:.4f}", flush=True)

        seed_results.append({
            "model": "Standard GraphSAGE",
            "seed": seed,
            "accuracy": round(base_test_res["Accuracy"], 6),
            "precision": round(base_test_res["Precision"], 6),
            "recall": round(base_test_res["Recall"], 6),
            "f1": round(base_test_res["F1"], 6),
            "roc_auc": round(base_test_res["ROC-AUC"], 6)
        })

        # 2. Full AMRG-GraphSAGE
        print(f"\n[Seed {seed}] Training Full AMRG-GraphSAGE...", flush=True)
        set_seed(seed)
        amrg_model = AMRGGraphSAGE(
            in_channels=in_channels,
            hidden_channels=128,
            num_relations=num_relations,
            num_layers=2,
            dropout=0.20
        )
        t0 = time.time()
        amrg_model, _, _, best_epoch, total_epochs = train_model(
            model=amrg_model,
            graph=data,
            epochs=400,
            lr=1e-3,
            weight_decay=1e-4,
            ranking_lambda=0.08,
            patience=50,
            pos_weight=1.12,
            seed=seed,
            verbose=False
        )
        amrg_elapsed = time.time() - t0
        amrg_test_res, _, _, _ = evaluate_model(amrg_model, data, data.test_mask)
        print(f"  Full AMRG-GraphSAGE [Seed {seed}] (Time: {amrg_elapsed:.1f}s, Epochs: {total_epochs}, Best: {best_epoch}): "
              f"Acc={amrg_test_res['Accuracy']:.4f}, Prec={amrg_test_res['Precision']:.4f}, "
              f"Rec={amrg_test_res['Recall']:.4f}, F1={amrg_test_res['F1']:.4f}, ROC-AUC={amrg_test_res['ROC-AUC']:.4f}", flush=True)

        seed_results.append({
            "model": "AMRG-GraphSAGE",
            "seed": seed,
            "accuracy": round(amrg_test_res["Accuracy"], 6),
            "precision": round(amrg_test_res["Precision"], 6),
            "recall": round(amrg_test_res["Recall"], 6),
            "f1": round(amrg_test_res["F1"], 6),
            "roc_auc": round(amrg_test_res["ROC-AUC"], 6)
        })

    # Save detailed repeated seed results
    results_df = pd.DataFrame(seed_results)
    res_path = os.path.join(RESULTS_DIR, "repeated_seed_results.csv")
    results_df.to_csv(res_path, index=False)
    results_df.to_csv(os.path.join(CODEBASE_DIR, "repeated_seed_results.csv"), index=False)
    print(f"\nSaved detailed seed results to: {res_path}", flush=True)

    # Compute summary (mean and std per metric)
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    summary_rows = []

    for model_name in ["Standard GraphSAGE", "AMRG-GraphSAGE"]:
        sub = results_df[results_df["model"] == model_name]
        for m in metrics:
            mean_val = float(sub[m].mean())
            std_val = float(sub[m].std())
            summary_rows.append({
                "model": model_name,
                "metric": m,
                "mean": round(mean_val, 6),
                "std": round(std_val, 6)
            })

    summary_df = pd.DataFrame(summary_rows)
    sum_path = os.path.join(RESULTS_DIR, "repeated_seed_summary.csv")
    summary_df.to_csv(sum_path, index=False)
    summary_df.to_csv(os.path.join(CODEBASE_DIR, "repeated_seed_summary.csv"), index=False)
    print(f"Saved summary statistics to: {sum_path}", flush=True)

    print("\n--- REPEATED SEED SUMMARY (MEAN ± STD) ---", flush=True)
    pivot_summary = summary_df.pivot(index="model", columns="metric", values=["mean", "std"])
    print(summary_df.to_string(index=False), flush=True)

    print("\n" + "=" * 76, flush=True)
    print("REPEATED-SEED VALIDATION COMPLETED SUCCESSFULLY", flush=True)
    print("=" * 76, flush=True)

    return results_df, summary_df


if __name__ == "__main__":
    run_repeated_seeds_validation()
