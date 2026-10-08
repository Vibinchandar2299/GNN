# Phase 4: AMRG-GraphSAGE Research Validation & Ablation Study

## Project
**HireGraph AI**  
**Paper Title:** *"An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements"*

---

## Overview
This directory contains the complete, self-contained research validation codebase for Phase 4. The primary objective is to evaluate the individual architectural components of the **Adaptive Multi-Scale Relation-Gated GraphSAGE (AMRG-GraphSAGE)** model through controlled ablations, multi-seed statistical testing, and temporal hiring requirement dynamics.

---

## Directory Structure
```
Codebase/research_validation/
├── data_loader.py               # Dataset loading, temporal split, graph construction, leakage verification
├── models.py                    # Neural architectures (Baseline GraphSAGE, Full AMRG, and 5 ablation variants)
├── train_utils.py               # Pairwise ranking loss, training loop with early stopping, evaluation metrics
├── run_ablation.py              # Execution of primary 7-variant ablation study (Seed 42)
├── run_repeated_seeds.py        # 5-seed repeated validation (Seeds 42, 123, 456, 789, 2026)
├── temporal_analysis.py         # Descriptive analysis of evolving requirements across 2023–2026
├── evaluate_results.py          # Figure generator (IEEE Transactions publication format) & metadata exporter
├── experiment_metadata.json     # Machine-readable experiment parameters and environment specifications
├── README.md                    # Research documentation and reproducibility guide
│
├── results/
│   ├── ablation_results.csv              # Full test metrics for all 7 variants
│   ├── ablation_component_effects.csv    # Isolated Delta-F1 and Delta-ROC-AUC per component
│   ├── repeated_seed_results.csv         # Detailed per-seed metrics
│   ├── repeated_seed_summary.csv         # Mean +/- Std across seeds
│   └── temporal_hiring_analysis.csv      # Empirical metrics per recruitment cycle
│
├── figures/
│   ├── ablation_f1_comparison.png        # Bar chart of test F1 across ablation variants
│   ├── ablation_roc_auc_comparison.png   # Bar chart of test ROC-AUC across ablation variants
│   ├── temporal_selection_rate.png       # Selection rate trajectory across cycles (2023-2026)
│   ├── temporal_skill_requirements.png   # Job skill requirement evolution with standard deviation bars
│   └── temporal_skill_match.png          # Applicant skill match ratio vs. skill level gap evolution
│
└── report/
    └── research_validation_report.md     # Comprehensive academic validation report
```

---

## Architectural Variants Evaluated

| Variant | Model Identifier | Ablated Mechanism | Architectural Description |
|---|---|---|---|
| **A** | `Standard GraphSAGE` | None (Baseline) | Standard 2-layer GraphSAGE (`hidden=64`, PyG `SAGEConv`, unweighted mean neighbor aggregation, no relation embeddings, no gating, single scale). |
| **B** | `Full AMRG-GraphSAGE` | None (Full Model) | Complete proposed architecture (`hidden=128`, 12 relation embeddings, score MLP attention, confidence gating, LayerNorm, multi-scale fusion, ranking loss). |
| **C** | `AMRG-No-Relation` | Relation-Aware Aggregation | Relation embeddings zeroed; score MLP operates without edge type semantics. |
| **D** | `AMRG-No-Adaptive-Weighting` | Adaptive Neighbor Weighting | Softmax attention replaced by uniform degree normalization ($1/\text{deg}(v)$). |
| **E** | `AMRG-No-Gating` | Feature-Confidence Gating | Sigmoid gating replaced by standard additive combination ($h_{self} + h_{neigh}$). |
| **F** | `AMRG-No-MultiScale` | Adaptive Multi-Scale Fusion | Multi-depth gating bypassed; only final Layer 1 output is fed to classifier. |
| **G** | `AMRG-No-Ranking` | Pairwise Ranking Loss | Total loss equals weighted BCE ($\lambda_{rank} = 0.0, pos\_weight = 1.12$). |

---

## Strict Research Integrity Safeguards
1. **No Data Leakage**: `StandardScaler` and `OneHotEncoder` are fitted **strictly** on the training split (Cycles 2023–2024). Validation (2025) and Testing (2026) applications are purely transformed.
2. **Identical Graph Representation**: Global graph structure ($N=5,977$, $E=43,044$) and node ID ordering are preserved identically without entity reordering or artificial pruning.
3. **Frozen Golden Artifacts**: Production checkpoints (`AMRG_GraphSAGE_model.pt`, `Baseline_GraphSAGE_model.pt`), predictions, and dataset are completely protected from overwrite.

---

## How to Reproduce
Run the scripts from the workspace root:
```bash
# 1. Run controlled ablation study
python Codebase/research_validation/run_ablation.py

# 2. Run multi-seed validation
python Codebase/research_validation/run_repeated_seeds.py

# 3. Run temporal hiring requirement analysis
python Codebase/research_validation/temporal_analysis.py

# 4. Generate IEEE figures and metadata
python Codebase/research_validation/evaluate_results.py
```
