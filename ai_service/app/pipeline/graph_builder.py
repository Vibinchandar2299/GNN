from typing import Tuple, Dict, Any, List
import numpy as np
import pandas as pd
import torch
from torch_geometric.data import Data
from ai_service.app.pipeline.preprocessor import (
    Preprocessor,
    TEMPORAL_COLUMN,
    TARGET_COLUMN,
    NODE_TYPE_NAMES,
)
from ai_service.app.core.logging import logger

def build_graph(
    df: pd.DataFrame,
    edges_df: pd.DataFrame,
    preprocessor: Preprocessor
) -> Tuple[Data, Dict[str, Dict[str, int]], Dict[str, int], Dict[int, str]]:
    """
    Constructs the exact PyG Data object matching Python.py from the research codebase:
    - 5,977 nodes
    - 4,000 application nodes
    - 1,534 student nodes
    - 125 company nodes
    - 300 job nodes
    - 18 skill nodes
    - 43,044 edges
    - 12 relation types
    - Feature dimension = 82
    """
    # 1. Clean dataset
    df = preprocessor.clean_dataset(df)

    # 2. Chronological Temporal Split
    cycles = sorted(df[TEMPORAL_COLUMN].unique())
    train_cycles = cycles[:-2]  # [2023, 2024]
    val_cycles = [cycles[-2]]   # [2025]
    test_cycles = [cycles[-1]]  # [2026]

    train_df = df[df[TEMPORAL_COLUMN].isin(train_cycles)].copy()
    val_df = df[df[TEMPORAL_COLUMN].isin(val_cycles)].copy()
    test_df = df[df[TEMPORAL_COLUMN].isin(test_cycles)].copy()

    # 3. Ensure preprocessor is fitted on train cycles
    if not preprocessor.is_fitted:
        preprocessor.fit_on_training_cycles(df, train_cycles)

    # Transform subsets
    X_train_app = preprocessor.transform(train_df)
    X_val_app = preprocessor.transform(val_df)
    X_test_app = preprocessor.transform(test_df)
    base_feature_dim = X_train_app.shape[1]  # 77

    # 4. Node Indexing (Preserve exact sequential allocation order)
    node_maps: Dict[str, Dict[str, int]] = {
        "application": {},
        "student": {},
        "company": {},
        "job": {},
        "skill": {}
    }
    next_node_id = 0

    def add_node(node_type: str, node_identifier: str) -> int:
        nonlocal next_node_id
        if node_identifier not in node_maps[node_type]:
            node_maps[node_type][node_identifier] = next_node_id
            next_node_id += 1
        return node_maps[node_type][node_identifier]

    all_df = pd.concat([train_df, val_df, test_df], ignore_index=True)

    for row in all_df.itertuples(index=False):
        add_node("application", str(row.application_id))
        add_node("student", str(row.student_id))
        add_node("company", str(row.company_id))
        add_node("job", str(row.job_id))

    if edges_df is not None:
        for row in edges_df.itertuples(index=False):
            src = str(row.source_id)
            dst = str(row.target_id)
            if src.startswith("SK_"):
                add_node("skill", src)
            if dst.startswith("SK_"):
                add_node("skill", dst)

    num_nodes = next_node_id

    # 5. Node Feature Matrix [num_nodes, 82]
    graph_feature_dim = base_feature_dim + len(NODE_TYPE_NAMES)  # 77 + 5 = 82
    X_graph = np.zeros((num_nodes, graph_feature_dim), dtype=np.float32)
    node_type_ids = {name: i for i, name in enumerate(NODE_TYPE_NAMES)}

    # Set one-hot node type indicators
    for node_type, mapping in node_maps.items():
        t = node_type_ids[node_type]
        for node_idx in mapping.values():
            X_graph[node_idx, base_feature_dim + t] = 1.0

    # Assign base application feature vectors
    for subset_df, X_subset in [
        (train_df, X_train_app),
        (val_df, X_val_app),
        (test_df, X_test_app)
    ]:
        for app_id, vector in zip(subset_df["application_id"], X_subset):
            idx = node_maps["application"][str(app_id)]
            X_graph[idx, :base_feature_dim] = vector

    # 6. Graph Edges Construction
    edge_src = []
    edge_dst = []
    edge_relation_names = []

    def add_edge(source: int, target: int, relation: str):
        edge_src.append(source)
        edge_dst.append(target)
        edge_relation_names.append(relation)

    for row in all_df.itertuples(index=False):
        app = node_maps["application"][str(row.application_id)]
        student = node_maps["student"][str(row.student_id)]
        company = node_maps["company"][str(row.company_id)]
        job = node_maps["job"][str(row.job_id)]

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

    # Relation mapping
    relation_to_id: Dict[str, int] = {}
    for relation in edge_relation_names:
        if relation not in relation_to_id:
            relation_to_id[relation] = len(relation_to_id)

    id_to_relation = {v: k for k, v in relation_to_id.items()}

    # 7. Convert to PyTorch Tensors
    edge_type = torch.tensor(
        [relation_to_id[r] for r in edge_relation_names],
        dtype=torch.long
    )
    edge_index = torch.tensor(
        [edge_src, edge_dst],
        dtype=torch.long
    )
    x_graph = torch.tensor(
        X_graph,
        dtype=torch.float32
    )

    # 8. Target & Masks
    y = torch.full((num_nodes,), -1.0, dtype=torch.float32)
    train_mask = torch.zeros(num_nodes, dtype=torch.bool)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool)

    for subset_df, mask in [
        (train_df, train_mask),
        (val_df, val_mask),
        (test_df, test_mask)
    ]:
        for row in subset_df.itertuples(index=False):
            idx = node_maps["application"][str(row.application_id)]
            mask[idx] = True
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

    logger.info(
        f"Graph construction completed: {num_nodes} nodes, "
        f"{edge_index.shape[1]} edges, {len(relation_to_id)} relation types, "
        f"feature dimension {data.num_node_features}"
    )

    return data, node_maps, relation_to_id, id_to_relation
