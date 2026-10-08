"""
Plotting and Evaluation Utilities for HireGraph AI Research Validation.
Produces publication-quality, IEEE-compliant figures for:
1. Ablation F1 comparison (ablation_f1_comparison.png)
2. Ablation ROC-AUC comparison (ablation_roc_auc_comparison.png)
3. Experiment metadata export (experiment_metadata.json)
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\results"
FIGURES_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\figures"
CODEBASE_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase"
METADATA_PATH = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\experiment_metadata.json"


def plot_ablation_figures():
    """Generates IEEE-format figures for ablation results."""
    ablation_csv = os.path.join(RESULTS_DIR, "ablation_results.csv")
    if not os.path.exists(ablation_csv):
        print(f"File {ablation_csv} does not exist yet.")
        return

    df = pd.read_csv(ablation_csv)

    # Set publication aesthetic (IEEE Transactions style)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10.5,
        "axes.labelsize": 11.5,
        "axes.titlesize": 12.5,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 13,
        "figure.dpi": 300
    })

    # Color palette
    colors = []
    for m in df["model"]:
        if "Full AMRG" in m or m == "AMRG-GraphSAGE":
            colors.append("#1f77b4")  # primary deep blue
        elif "Baseline" in m or m == "GraphSAGE":
            colors.append("#7f7f7f")  # neutral grey
        else:
            colors.append("#aec7e8")  # lighter blue for ablated variants

    # 1. Ablation F1 Comparison Plot
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.barh(df["model"], df["f1"], color=colors, height=0.55, edgecolor="black", linewidth=0.8)
    
    # Reference line at Full AMRG
    full_f1 = df[df["model"].str.contains("Full AMRG|AMRG-GraphSAGE")]["f1"].values[0]
    ax.axvline(full_f1, color="#d62728", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Full AMRG ({full_f1:.4f})")
    
    # Baseline reference line
    base_f1 = df[df["model"].str.contains("Baseline|GraphSAGE")]["f1"].values[0]
    ax.axvline(base_f1, color="#7f7f7f", linestyle=":", linewidth=1.5, alpha=0.8, label=f"Baseline ({base_f1:.4f})")

    for bar, val in zip(bars, df["f1"]):
        ax.text(val + 0.0005, bar.get_y() + bar.get_height()/2.0, f"{val:.4f}", ha="left", va="center", fontsize=9, fontweight="bold")

    min_f1 = min(df["f1"].min(), base_f1) - 0.008
    max_f1 = max(df["f1"].max(), full_f1) + 0.008
    ax.set_xlim(min_f1, max_f1)
    ax.set_xlabel("Test F1-Score (Recruitment Cycle 2026)", labelpad=8)
    ax.set_title("AMRG-GraphSAGE Architectural Component Ablation: F1-Score", pad=12, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_f1_1 = os.path.join(FIGURES_DIR, "ablation_f1_comparison.png")
    out_f1_2 = os.path.join(CODEBASE_DIR, "ablation_f1_comparison.png")
    fig.savefig(out_f1_1, dpi=300)
    fig.savefig(out_f1_2, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_f1_1}")

    # 2. Ablation ROC-AUC Comparison Plot
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bars = ax.barh(df["model"], df["roc_auc"], color=colors, height=0.55, edgecolor="black", linewidth=0.8)
    
    full_auc = df[df["model"].str.contains("Full AMRG|AMRG-GraphSAGE")]["roc_auc"].values[0]
    ax.axvline(full_auc, color="#d62728", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Full AMRG ({full_auc:.4f})")

    base_auc = df[df["model"].str.contains("Baseline|GraphSAGE")]["roc_auc"].values[0]
    ax.axvline(base_auc, color="#7f7f7f", linestyle=":", linewidth=1.5, alpha=0.8, label=f"Baseline ({base_auc:.4f})")

    for bar, val in zip(bars, df["roc_auc"]):
        ax.text(val + 0.0003, bar.get_y() + bar.get_height()/2.0, f"{val:.4f}", ha="left", va="center", fontsize=9, fontweight="bold")

    min_auc = min(df["roc_auc"].min(), base_auc) - 0.004
    max_auc = max(df["roc_auc"].max(), full_auc) + 0.004
    ax.set_xlim(min_auc, max_auc)
    ax.set_xlabel("Test ROC-AUC (Recruitment Cycle 2026)", labelpad=8)
    ax.set_title("AMRG-GraphSAGE Architectural Component Ablation: ROC-AUC", pad=12, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()

    out_auc_1 = os.path.join(FIGURES_DIR, "ablation_roc_auc_comparison.png")
    out_auc_2 = os.path.join(CODEBASE_DIR, "ablation_roc_auc_comparison.png")
    fig.savefig(out_auc_1, dpi=300)
    fig.savefig(out_auc_2, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_auc_1}")


def generate_experiment_metadata(extra_info=None):
    """Generates comprehensive JSON metadata for reproducibility."""
    metadata = {
        "project": "HireGraph AI",
        "title": "An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements",
        "timestamp": "2026-10-08",
        "environment": {
            "os": "Windows",
            "compute_device": "CPU",
            "python_version": "3.12",
            "pytorch_version": "2.2.0+cpu",
            "torch_geometric_version": "2.8.0.post1"
        },
        "dataset_configuration": {
            "source_file": "Dataset/GNN_Placement_Dataset.xlsx",
            "total_applications": 4000,
            "target_distribution": {
                "Selected (1)": 2200,
                "Rejected (0)": 1800
            },
            "nodes": {
                "application": 4000,
                "student": 1534,
                "company": 125,
                "job": 300,
                "skill": 18,
                "total": 5977
            },
            "edges": {
                "total": 43044,
                "relation_types_count": 12
            },
            "features": {
                "base_application_features": 77,
                "node_type_one_hot": 5,
                "total_node_features": 82
            },
            "temporal_splits": {
                "training_cycles": [2023, 2024],
                "training_size": 1594,
                "validation_cycle": [2025],
                "validation_size": 1160,
                "testing_cycle": [2026],
                "testing_size": 1246
            },
            "preprocessing": {
                "numeric_scaler": "StandardScaler (fitted strictly on 2023-2024)",
                "categorical_encoder": "OneHotEncoder(handle_unknown='ignore') (fitted strictly on 2023-2024)",
                "data_leakage_prevented": True
            }
        },
        "training_hyperparameters": {
            "optimizer": "Adam",
            "learning_rate": 0.001,
            "weight_decay": 0.0001,
            "gradient_clipping_max_norm": 2.0,
            "early_stopping_metric": "val_f1",
            "primary_seed": 42,
            "repeated_seeds": [42, 123, 456, 789, 2026],
            "baseline_graphsage": {
                "hidden_channels": 64,
                "num_layers": 2,
                "dropout": 0.30,
                "epochs": 120,
                "patience": 15,
                "pos_weight": 1.0,
                "ranking_lambda": 0.0
            },
            "amrg_graphsage": {
                "hidden_channels": 128,
                "num_layers": 2,
                "relation_dim": 16,
                "dropout": 0.20,
                "epochs": 400,
                "patience": 50,
                "pos_weight": 1.12,
                "ranking_lambda": 0.08
            }
        }
    }

    if extra_info:
        metadata.update(extra_info)

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Saved experiment metadata to {METADATA_PATH}")

    # Also save to Codebase/
    root_meta = os.path.join(CODEBASE_DIR, "experiment_metadata.json")
    with open(root_meta, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Saved experiment metadata to {root_meta}")


if __name__ == "__main__":
    plot_ablation_figures()
    generate_experiment_metadata()
