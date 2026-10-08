"""
Data loading and graph construction pipeline for Phase 4 Research Validation.
Strictly preserves the original graph structure, temporal split, and preprocessing:
- 5,977 total nodes (4,000 application, 1,534 student, 125 company, 300 job, 18 skill)
- 43,044 edges across 12 relation types
- Feature dimension: 82 (77 base application features + 5 node-type one-hot indicators)
- Temporal split: Train 2023-2024 (1,594), Val 2025 (1,160), Test 2026 (1,246)
- Preprocessing: StandardScaler and OneHotEncoder fitted STRICTLY on training split (no leakage)
"""

import os
from typing import Tuple, Dict, Any, List
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from torch_geometric.data import Data

EXCEL_PATH = r"c:\Users\VIBIN\Vibin Projects\GNN\Dataset\GNN_Placement_Dataset.xlsx"

NUMERIC_FEATURES = [
    "cgpa", "backlogs", "aptitude_score_pre", "coding_score_pre", "communication_score_pre",
    "projects_count", "internships_count", "certifications_count", "resume_score",
    "expected_hiring_count", "minimum_cgpa", "experience_required_months", "salary_lpa",
    "relevant_experience_months", "total_skill_count", "average_skill_proficiency",
    "required_skill_count", "historical_selection_rate", "historical_average_selected_cgpa",
    "role_shift_score", "skill_match_ratio", "required_skill_level_gap", "role_experience_match"
]

CATEGORICAL_FEATURES = [
    "department", "industry", "company_size", "job_title", "job_domain"
]

NODE_TYPE_NAMES = ["application", "student", "company", "job", "skill"]

POST_INTERVIEW_LEAKAGE_COLUMNS = [
    "technical_score", "round_score", "interviewer_rating", "round_result",
    "final_interview_score", "rejection_stage", "offer_status", "joining_status",
    "final_comments", "decision_comment", "hr_feedback"
]


CACHE_PATH = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\data_cache.pt"


def load_dataset_and_graph(excel_path: str = EXCEL_PATH, use_cache: bool = True) -> Tuple[Data, Dict[str, int], pd.DataFrame]:
    """
    Loads Excel dataset and builds graph Data object exactly matching Python.py.
    Optionally caches preprocessed data object to disk to avoid repeated 20-second Excel parses.
    """
    if use_cache and os.path.exists(CACHE_PATH):
        cached = torch.load(CACHE_PATH)
        return cached["data"], cached["relation_to_id"], cached["df"]

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Dataset not found at {excel_path}")

    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name="unified_dataset")
    edges_df = pd.read_excel(xls, sheet_name="graph_edges") if "graph_edges" in xls.sheet_names else None

    # Verify no post-interview leakage columns exist
    detected_leakage = [col for col in POST_INTERVIEW_LEAKAGE_COLUMNS if col in df.columns]
    if detected_leakage:
        raise ValueError(f"CRITICAL: Post-interview leakage columns detected: {detected_leakage}")

    # Deduplication and null cleaning (identical to Python.py)
    df = df.drop_duplicates().copy()
    df = df.drop_duplicates(subset=["application_id"], keep="first").copy()
    df = df.dropna().reset_index(drop=True)

    # Temporal split
    cycles = sorted(df["recruitment_cycle"].unique())
    train_cycles = cycles[:-2]  # [2023, 2024]
    val_cycles = [cycles[-2]]   # [2025]
    test_cycles = [cycles[-1]]  # [2026]

    train_df = df[df["recruitment_cycle"].isin(train_cycles)].copy()
    val_df = df[df["recruitment_cycle"].isin(val_cycles)].copy()
    test_df = df[df["recruitment_cycle"].isin(test_cycles)].copy()

    # Preprocessing: fitted ONLY on training split
    scaler = StandardScaler()
    X_train_num = scaler.fit_transform(train_df[NUMERIC_FEATURES])
    X_val_num = scaler.transform(val_df[NUMERIC_FEATURES])
    X_test_num = scaler.transform(test_df[NUMERIC_FEATURES])

    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

    X_train_cat = encoder.fit_transform(train_df[CATEGORICAL_FEATURES])
    X_val_cat = encoder.transform(val_df[CATEGORICAL_FEATURES])
    X_test_cat = encoder.transform(test_df[CATEGORICAL_FEATURES])

    X_train_app = np.hstack([X_train_num, X_train_cat]).astype(np.float32)
    X_val_app = np.hstack([X_val_num, X_val_cat]).astype(np.float32)
    X_test_app = np.hstack([X_test_num, X_test_cat]).astype(np.float32)

    base_feature_dim = X_train_app.shape[1]  # 77

    # Global node mapping (identical to Python.py sequential order)
    node_maps = {t: {} for t in NODE_TYPE_NAMES}
    next_node_id = 0

    def add_node(node_type: str, node_identifier: Any) -> int:
        nonlocal next_node_id
        if node_identifier not in node_maps[node_type]:
            node_maps[node_type][node_identifier] = next_node_id
            next_node_id += 1
        return node_maps[node_type][node_identifier]

    all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)

    for row in all_df.itertuples(index=False):
        add_node("application", row.application_id)
        add_node("student", row.student_id)
        add_node("company", row.company_id)
        add_node("job", row.job_id)

    if edges_df is not None:
        for row in edges_df.itertuples(index=False):
            src = str(row.source_id)
            dst = str(row.target_id)
            if src.startswith("SK_"):
                add_node("skill", src)
            if dst.startswith("SK_"):
                add_node("skill", dst)

    num_nodes = next_node_id
    graph_feature_dim = base_feature_dim + len(NODE_TYPE_NAMES)  # 77 + 5 = 82
    X_graph = np.zeros((num_nodes, graph_feature_dim), dtype=np.float32)

    node_type_ids = {name: i for i, name in enumerate(NODE_TYPE_NAMES)}
    for node_type, mapping in node_maps.items():
        t = node_type_ids[node_type]
        for node_idx in mapping.values():
            X_graph[node_idx, base_feature_dim + t] = 1.0

    for subset_df, X_subset in [
        (train_df, X_train_app),
        (val_df, X_val_app),
        (test_df, X_test_app)
    ]:
        for app_id, vector in zip(subset_df["application_id"], X_subset):
            idx = node_maps["application"][app_id]
            X_graph[idx, :base_feature_dim] = vector

    # Edges
    edge_src: List[int] = []
    edge_dst: List[int] = []
    edge_relation_names: List[str] = []

    def add_edge(source: int, target: int, relation: str):
        edge_src.append(source)
        edge_dst.append(target)
        edge_relation_names.append(relation)

    for row in all_df.itertuples(index=False):
        app = node_maps["application"][row.application_id]
        student = node_maps["student"][row.student_id]
        company = node_maps["company"][row.company_id]
        job = node_maps["job"][row.job_id]

        add_edge(app, student, "APPLICATION_STUDENT")
        add_edge(student, app, "STUDENT_APPLICATION")
        add_edge(app, company, "APPLICATION_COMPANY")
        add_edge(company, app, "COMPANY_APPLICATION")
        add_edge(app, job, "APPLICATION_JOB")
        add_edge(job, app, "JOB_APPLICATION")

    if edges_df is not None:
        for row in edges_df.itertuples(index=False):
            src_id = str(row.source_id)
            relation = str(row.relation_type)
            dst_id = str(row.target_id)

            if src_id in node_maps["student"] and dst_id in node_maps["skill"]:
                src = node_maps["student"][src_id]
                dst = node_maps["skill"][dst_id]
                add_edge(src, dst, relation)
                add_edge(dst, src, "REV_" + relation)
            elif src_id in node_maps["job"] and dst_id in node_maps["skill"]:
                src = node_maps["job"][src_id]
                dst = node_maps["skill"][dst_id]
                add_edge(src, dst, relation)
                add_edge(dst, src, "REV_" + relation)
            elif src_id in node_maps["job"] and dst_id in node_maps["company"]:
                src = node_maps["job"][src_id]
                dst = node_maps["company"][dst_id]
                add_edge(src, dst, relation)
                add_edge(dst, src, "REV_" + relation)

    relation_to_id: Dict[str, int] = {}
    for relation in edge_relation_names:
        if relation not in relation_to_id:
            relation_to_id[relation] = len(relation_to_id)

    edge_type = torch.tensor([relation_to_id[r] for r in edge_relation_names], dtype=torch.long)
    edge_index = torch.tensor([edge_src, edge_dst], dtype=torch.long)
    x_graph = torch.tensor(X_graph, dtype=torch.float32)

    y = torch.full((num_nodes,), -1.0, dtype=torch.float32)
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)

    for row in train_df.itertuples(index=False):
        idx = node_maps["application"][row.application_id]
        train_mask[idx] = True
        y[idx] = float(row.final_status)

    for row in val_df.itertuples(index=False):
        idx = node_maps["application"][row.application_id]
        val_mask[idx] = True
        y[idx] = float(row.final_status)

    for row in test_df.itertuples(index=False):
        idx = node_maps["application"][row.application_id]
        test_mask[idx] = True
        y[idx] = float(row.final_status)

    data = Data(
        x=x_graph,
        edge_index=edge_index,
        edge_type=edge_type,
        y=y,
        train_mask=train_mask,
        val_mask=val_mask,
        test_mask=test_mask
    )

    # Verification assertions
    assert num_nodes == 5977, f"Expected 5977 nodes, got {num_nodes}"
    assert edge_index.size(1) == 43044, f"Expected 43044 edges, got {edge_index.size(1)}"
    assert len(relation_to_id) == 12, f"Expected 12 relation types, got {len(relation_to_id)}"
    assert train_mask.sum().item() == 1594, f"Expected 1594 train applications, got {train_mask.sum().item()}"
    assert val_mask.sum().item() == 1160, f"Expected 1160 val applications, got {val_mask.sum().item()}"
    assert test_mask.sum().item() == 1246, f"Expected 1246 test applications, got {test_mask.sum().item()}"
    assert x_graph.size(1) == 82, f"Expected 82 node features, got {x_graph.size(1)}"
    if use_cache:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        torch.save({
            "data": data,
            "relation_to_id": relation_to_id,
            "df": df
        }, CACHE_PATH)

    return data, relation_to_id, df
