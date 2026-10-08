# HireGraph AI — Research Validation & AMRG-GraphSAGE Ablation Study Report

**Paper Title:** *"An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements"*  
**Project:** HireGraph AI  
**Validation Phase:** Phase 4 — Rigorous Empirical Validation & Architectural Ablation  
**Date:** October 2026  
**Status:** VALIDATION COMPLETE  

---

## 1. Experimental Objective
The primary objective of this research validation phase is to conduct a rigorous, controlled ablation study of the **Adaptive Multi-Scale Relation-Gated GraphSAGE (AMRG-GraphSAGE)** architecture to determine the exact empirical contribution of each individual novel component to hiring outcome prediction under evolving recruitment cycles.

To adhere to the highest standard of scientific integrity:
- Every variant is benchmarked on the identical preprocessed feature space, global graph structure, temporal split, and loss protocol.
- Only one component is removed or ablated at a time.
- All numbers are strictly empirical (zero fabrication, zero synthetic data).
- The existing production checkpoints, dataset, and application services remain strictly frozen and untouched.

---

## 2. Dataset Configuration
The experiment uses the canonical Excel dataset (`Dataset/GNN_Placement_Dataset.xlsx`):
- **Total Applications:** 4,000
- **Unique Students:** 1,534
- **Unique Companies:** 125
- **Unique Jobs:** 300
- **Unique Skills:** 18
- **Target Distribution:**
  - Selected ($y = 1$): 2,200 ($55.0\%$)
  - Rejected ($y = 0$): 1,800 ($45.0\%$)

### Exact Chronological Temporal Split
To simulate real-world production deployment and eliminate future-to-past data leakage:
- **Training Set (Cycles 2023–2024):** 1,594 applications ($614 \text{ in } 2023 + 980 \text{ in } 2024$)
- **Validation Set (Cycle 2025):** 1,160 applications
- **Testing Set (Cycle 2026):** 1,246 applications
- **Strict Leakage Safeguard:** Feature scaling (`StandardScaler`) and categorical encoding (`OneHotEncoder`) are fitted **strictly on the 2023–2024 training applications**. Validation and test applications are strictly transformed without updating scaler statistics.

---

## 3. Graph Configuration
The multi-relational hiring graph represents interconnected entities across the campus placement ecosystem:
- **Total Nodes:** 5,977 (4,000 application nodes, 1,534 student nodes, 125 company nodes, 300 job nodes, 18 skill nodes)
- **Total Directed Edges:** 43,044
- **Relation Types ($R = 12$):**
  1. `APPLICATION_STUDENT` & `STUDENT_APPLICATION` (Bidirectional)
  2. `APPLICATION_COMPANY` & `COMPANY_APPLICATION` (Bidirectional)
  3. `APPLICATION_JOB` & `JOB_APPLICATION` (Bidirectional)
  4. `HAS_SKILL` & `REV_HAS_SKILL` (Student $\leftrightarrow$ Skill)
  5. `REQUIRES_SKILL` & `REV_REQUIRES_SKILL` (Job $\leftrightarrow$ Skill)
  6. `POSTED_BY` & `REV_POSTED_BY` (Job $\leftrightarrow$ Company)
- **Node Feature Dimension ($d = 82$):**
  - 77 base application attributes (23 numerical + 54 one-hot encoded categorical dimensions)
  - 5 one-hot node-type indicators (`application`, `student`, `company`, `job`, `skill`)

---

## 4. Baseline Configuration (Standard GraphSAGE)
- **Architecture:** 2-layer GraphSAGE using PyG `SAGEConv`
- **Aggregation:** Uniform mean aggregation over unweighted incoming edges
- **Hidden Dimensions:** 64
- **Regularization:** ReLU + Dropout ($p = 0.30$)
- **Classifier:** Single linear projection $\mathbb{R}^{64} \to \mathbb{R}^1$
- **Loss:** Standard Binary Cross-Entropy (BCE) with `pos_weight = 1.0`
- **Optimization:** Adam ($\text{lr} = 10^{-3}$, weight decay $= 10^{-4}$), patience $= 15$, max epochs $= 120$.

---

## 5. AMRG-GraphSAGE Architecture
The proposed AMRG-GraphSAGE model addresses heterogeneity and noise in recruitment graphs through 6 coupled mechanisms:
1. **Relation Embeddings:** 16-dimensional learned vector $r_e \in \mathbb{R}^{16}$ for each of the 12 edge types.
2. **Relation-Aware Transformation & Scoring:** Multi-Layer Perceptron $\text{MLP}([x_{dst} \,\|\, x_{src} \,\|\, r_e])$ computing edge-specific compatibility scores.
3. **Adaptive Neighborhood Weighting:** Graph-wise normalized softmax attention $\alpha_{uv} = \text{softmax}_{v}(s_{uv})$ filtering out irrelevant relational noise.
4. **Feature-Confidence Gating:** Sigmoid gate $g = \sigma(W_g [h_{self} \,\|\, h_{neigh}])$ adaptively balancing an applicant's direct resume credentials against relational graph context:
   $$h_v = g \odot h_{self} + (1 - g) \odot h_{neigh}$$
5. **Adaptive Multi-Scale Fusion:** Stacked layer representations $H = [h^{(1)}, h^{(2)}]$ weighted via learned depth-attention $\beta = \text{softmax}(W_s H)$ to balance direct 1-hop credentials and 2-hop contextual topology.
6. **Class-Weighted Pairwise Ranking Loss:** Joint objective combining weighted BCE ($\text{pos\_weight} = 1.12$) with margin-based pairwise ranking loss ($\lambda_{rank} = 0.08, \text{margin} = 0.20$):
   $$\mathcal{L}_{total} = (1 - \lambda) \mathcal{L}_{BCE} + \lambda \mathcal{L}_{rank}$$

---

## 6. Ablation Methodology
To evaluate the contribution of each mechanism, 7 controlled variants are evaluated under identical conditions (Seed 42):
- **Variant A (Standard GraphSAGE):** Baseline reference model without AMRG mechanisms.
- **Variant B (Full AMRG-GraphSAGE):** Complete proposed architecture.
- **Variant C (Without Relation-Aware Aggregation):** Relation embeddings zeroed ($r_e = \mathbf{0}$); attention operates without edge semantics.
- **Variant D (Without Adaptive Neighbor Weighting):** Attention replaced with uniform degree normalization ($1/\text{deg}(v)$).
- **Variant E (Without Feature-Confidence Gating):** Gating replaced with standard additive combination ($h_{self} + h_{neigh}$).
- **Variant F (Without Adaptive Multi-Scale Fusion):** Only final Layer 1 output is fed to the classifier.
- **Variant G (Without Ranking Loss):** Classification BCE only ($\lambda_{rank} = 0.0, \text{pos\_weight} = 1.12$).
