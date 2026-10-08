"""
AMRG-GraphSAGE Controlled Ablation Study Execution Script.

Conducts controlled single-component removal experiments under identical:
- Dataset and preprocessed features (82-dim, fitted strictly on 2023-2024)
- Global graph structure (5,977 nodes, 43,044 edges, 12 relations)
- Temporal evaluation split (Train: 2023-2024, Val: 2025, Test: 2026)
- Optimization hyperparameters (Adam, lr=1e-3, weight_decay=1e-4, pos_weight=1.12, seed=42)

Evaluates:
- Variant A: Standard GraphSAGE (Baseline)
- Variant B: Full AMRG-GraphSAGE (Proposed)
- Variant C: AMRG Without Relation-Aware Aggregation
- Variant D: AMRG Without Adaptive Neighbor Weighting
- Variant E: AMRG Without Feature-Confidence Gating
- Variant F: AMRG Without Adaptive Multi-Scale Fusion
- Variant G: AMRG Without Ranking Loss
"""

import os
import sys
import time
import shutil

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

import pandas as pd
import numpy as np
import torch

from Codebase.research_validation.data_loader import load_dataset_and_graph
from Codebase.research_validation.models import (
    BaselineGraphSAGE,
    AMRGGraphSAGE,
    AMRGNoRelationGraphSAGE,
    AMRGNoAdaptiveWeightingGraphSAGE,
    AMRGNoGatingGraphSAGE,
    AMRGNoMultiScaleGraphSAGE
)
from Codebase.research_validation.train_utils import set_seed, train_model, evaluate_model
from Codebase.research_validation.evaluate_results import plot_ablation_figures, generate_experiment_metadata

RESULTS_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\results"
FIGURES_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\figures"
MODELS_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\ablation_models"
CODEBASE_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase"

FROZEN_AMRG_PT = os.path.join(CODEBASE_DIR, "AMRG_GraphSAGE_model.pt")
FROZEN_BASE_PT = os.path.join(CODEBASE_DIR, "Baseline_GraphSAGE_model.pt")


def run_ablation_study(seed: int = 42):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    print("=" * 76, flush=True)
    print("STARTING CONTROLLED ABLATION STUDY (SEED = 42)", flush=True)
    print("=" * 76, flush=True)

    data, relation_to_id, _ = load_dataset_and_graph(use_cache=True)
    in_channels = data.num_node_features  # 82
    num_relations = len(relation_to_id)   # 12

    # Verify frozen checkpoints first
    print("\n--- Verifying Golden Frozen Checkpoints ---", flush=True)
    golden_amrg = AMRGGraphSAGE(in_channels, hidden_channels=128, num_relations=num_relations, num_layers=2, dropout=0.20)
    golden_amrg.load_state_dict(torch.load(FROZEN_AMRG_PT, map_location="cpu"))
    golden_amrg_res, _, _, _ = evaluate_model(golden_amrg, data, data.test_mask)
    print(f"Golden AMRG Checkpoint: Acc={golden_amrg_res['Accuracy']:.4f}, Prec={golden_amrg_res['Precision']:.4f}, Rec={golden_amrg_res['Recall']:.4f}, F1={golden_amrg_res['F1']:.4f}, ROC-AUC={golden_amrg_res['ROC-AUC']:.4f}", flush=True)

    golden_base = BaselineGraphSAGE(in_channels, hidden_channels=64, num_layers=2, dropout=0.30)
    golden_base.load_state_dict(torch.load(FROZEN_BASE_PT, map_location="cpu"))
    golden_base_res, _, _, _ = evaluate_model(golden_base, data, data.test_mask)
    print(f"Golden Baseline Checkpoint: Acc={golden_base_res['Accuracy']:.4f}, Prec={golden_base_res['Precision']:.4f}, Rec={golden_base_res['Recall']:.4f}, F1={golden_base_res['F1']:.4f}, ROC-AUC={golden_base_res['ROC-AUC']:.4f}", flush=True)

    # Define ablation variants
    variants = [
        {
            "name": "Standard GraphSAGE",
            "removed_component": "None (Baseline)",
            "model_cls": BaselineGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 64, "num_layers": 2, "dropout": 0.30},
            "train_kwargs": {"epochs": 120, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.0, "patience": 15, "pos_weight": 1.0},
            "ckpt_name": "baseline_graphsage_seed42.pt",
            "is_golden_fallback": False
        },
        {
            "name": "Full AMRG-GraphSAGE",
            "removed_component": "None (Full Architecture)",
            "model_cls": AMRGGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 128, "num_relations": num_relations, "num_layers": 2, "dropout": 0.20},
            "train_kwargs": {"epochs": 400, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.08, "patience": 50, "pos_weight": 1.12},
            "ckpt_name": "amrg_full_seed42.pt",
            "is_golden_fallback": False
        },
        {
            "name": "AMRG-No-Relation",
            "removed_component": "Relation-Aware Aggregation",
            "model_cls": AMRGNoRelationGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 128, "num_relations": num_relations, "num_layers": 2, "dropout": 0.20},
            "train_kwargs": {"epochs": 400, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.08, "patience": 50, "pos_weight": 1.12},
            "ckpt_name": "amrg_no_relation_seed42.pt",
            "is_golden_fallback": False
        },
        {
            "name": "AMRG-No-Adaptive-Weighting",
            "removed_component": "Adaptive Neighbor Weighting",
            "model_cls": AMRGNoAdaptiveWeightingGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 128, "num_relations": num_relations, "num_layers": 2, "dropout": 0.20},
            "train_kwargs": {"epochs": 400, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.08, "patience": 50, "pos_weight": 1.12},
            "ckpt_name": "amrg_no_adaptive_weighting_seed42.pt",
            "is_golden_fallback": False
        },
        {
            "name": "AMRG-No-Gating",
            "removed_component": "Feature-Confidence Gating",
            "model_cls": AMRGNoGatingGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 128, "num_relations": num_relations, "num_layers": 2, "dropout": 0.20},
            "train_kwargs": {"epochs": 400, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.08, "patience": 50, "pos_weight": 1.12},
            "ckpt_name": "amrg_no_gating_seed42.pt",
            "is_golden_fallback": False
        },
        {
            "name": "AMRG-No-MultiScale",
            "removed_component": "Adaptive Multi-Scale Fusion",
            "model_cls": AMRGNoMultiScaleGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 128, "num_relations": num_relations, "num_layers": 2, "dropout": 0.20},
            "train_kwargs": {"epochs": 400, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.08, "patience": 50, "pos_weight": 1.12},
            "ckpt_name": "amrg_no_multiscale_seed42.pt",
            "is_golden_fallback": False
        },
        {
            "name": "AMRG-No-Ranking",
            "removed_component": "Pairwise Ranking Loss",
            "model_cls": AMRGGraphSAGE,
            "model_kwargs": {"in_channels": in_channels, "hidden_channels": 128, "num_relations": num_relations, "num_layers": 2, "dropout": 0.20},
            "train_kwargs": {"epochs": 400, "lr": 1e-3, "weight_decay": 1e-4, "ranking_lambda": 0.00, "patience": 50, "pos_weight": 1.12},
            "ckpt_name": "amrg_no_ranking_seed42.pt",
            "is_golden_fallback": False
        }
    ]

    results_rows = []

    for idx, v in enumerate(variants, 1):
        print("\n" + "=" * 76, flush=True)
        print(f"[{idx}/{len(variants)}] TRAINING VARIANT: {v['name']}", flush=True)
        print(f"Removed Component: {v['removed_component']}", flush=True)
        print("=" * 76, flush=True)

        set_seed(seed)
        model = v["model_cls"](**v["model_kwargs"])

        t0 = time.time()
        trained_model, history, best_val_f1, best_epoch, total_epochs = train_model(
            model=model,
            graph=data,
            seed=seed,
            verbose=True,
            **v["train_kwargs"]
        )
        elapsed = time.time() - t0

        ckpt_path = os.path.join(MODELS_DIR, v["ckpt_name"])
        torch.save(trained_model.state_dict(), ckpt_path)
        print(f"Saved ablated checkpoint to: {ckpt_path} (Training time: {elapsed:.1f}s, Best epoch: {best_epoch})", flush=True)

        # Evaluate on test set (2026 split, 1246 applications)
        test_res, _, _, _ = evaluate_model(trained_model, data, data.test_mask)

        print(f"Test Evaluation Results for {v['name']}:", flush=True)
        print(f"  Accuracy : {test_res['Accuracy']:.4f}", flush=True)
        print(f"  Precision: {test_res['Precision']:.4f}", flush=True)
        print(f"  Recall   : {test_res['Recall']:.4f}", flush=True)
        print(f"  F1-Score : {test_res['F1']:.4f}", flush=True)
        print(f"  ROC-AUC  : {test_res['ROC-AUC']:.4f}", flush=True)

        results_rows.append({
            "model": v["name"],
            "removed_component": v["removed_component"],
            "accuracy": round(test_res["Accuracy"], 6),
            "precision": round(test_res["Precision"], 6),
            "recall": round(test_res["Recall"], 6),
            "f1": round(test_res["F1"], 6),
            "roc_auc": round(test_res["ROC-AUC"], 6),
            "seed": seed,
            "train_epochs": total_epochs,
            "best_validation_f1": round(best_val_f1, 6),
            "training_time_seconds": round(elapsed, 2)
        })

    # Save ablation_results.csv
    results_df = pd.DataFrame(results_rows)
    ablation_res_path = os.path.join(RESULTS_DIR, "ablation_results.csv")
    results_df.to_csv(ablation_res_path, index=False)
    results_df.to_csv(os.path.join(CODEBASE_DIR, "ablation_results.csv"), index=False)
    print(f"\nSaved primary ablation table to: {ablation_res_path}", flush=True)

    # Component contribution analysis (Section 15)
    # Full AMRG F1 minus Ablated model F1
    full_row = results_df[results_df["model"] == "Full AMRG-GraphSAGE"].iloc[0]
    full_f1 = full_row["f1"]
    full_auc = full_row["roc_auc"]

    effects_rows = []
    for _, row in results_df.iterrows():
        if row["model"] in ["Full AMRG-GraphSAGE", "Standard GraphSAGE"]:
            continue
        
        f1_change = full_f1 - row["f1"]
        auc_change = full_auc - row["roc_auc"]

        effects_rows.append({
            "component": row["removed_component"],
            "ablated_model": row["model"],
            "full_model_f1": round(full_f1, 6),
            "ablated_model_f1": round(row["f1"], 6),
            "f1_change": round(f1_change, 6),
            "full_model_roc_auc": round(full_auc, 6),
            "ablated_model_roc_auc": round(row["roc_auc"], 6),
            "roc_auc_change": round(auc_change, 6),
            "interpretation": "Full model performed better" if f1_change > 0 else "Ablated model performed better" if f1_change < 0 else "Neutral effect"
        })

    effects_df = pd.DataFrame(effects_rows)
    effects_path = os.path.join(RESULTS_DIR, "ablation_component_effects.csv")
    effects_df.to_csv(effects_path, index=False)
    effects_df.to_csv(os.path.join(CODEBASE_DIR, "ablation_component_effects.csv"), index=False)
    print(f"Saved component contribution table to: {effects_path}", flush=True)

    print("\n--- ABLATION RESULTS TABLE ---", flush=True)
    print(results_df[["model", "removed_component", "accuracy", "f1", "roc_auc", "train_epochs"]].to_string(index=False), flush=True)

    print("\n--- COMPONENT CONTRIBUTION EFFECTS ---", flush=True)
    print(effects_df[["component", "full_model_f1", "ablated_model_f1", "f1_change", "roc_auc_change", "interpretation"]].to_string(index=False), flush=True)

    # Generate charts and metadata
    plot_ablation_figures()
    generate_experiment_metadata({
        "ablation_study_summary": {
            "evaluated_models_count": len(results_df),
            "primary_seed": seed,
            "full_amrg_f1": full_f1,
            "full_amrg_roc_auc": full_auc
        }
    })

    print("\n" + "=" * 76, flush=True)
    print("ABLATION STUDY COMPLETED SUCCESSFULLY", flush=True)
    print("=" * 76, flush=True)

    return results_df, effects_df


if __name__ == "__main__":
    run_ablation_study(seed=42)
