import os
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
from torch_geometric.utils import softmax as pyg_softmax

# Define constants exactly matching Python.py
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

device = torch.device("cpu")

EXCEL_PATH = r"c:\Users\VIBIN\Vibin Projects\GNN\Dataset\GNN_Placement_Dataset.xlsx"
AMRG_CHECKPOINT = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\AMRG_GraphSAGE_model.pt"
BASELINE_CHECKPOINT = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\Baseline_GraphSAGE_model.pt"

# Model definitions exactly as in Python.py
class BaselineGraphSAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels=64, num_layers=2, dropout=0.30):
        super().__init__()
        self.convs = nn.ModuleList()
        self.convs.append(SAGEConv(in_channels, hidden_channels))
        for _ in range(num_layers - 1):
            self.convs.append(SAGEConv(hidden_channels, hidden_channels))
        self.dropout = dropout
        self.classifier = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, edge_type=None):
        for conv in self.convs:
            x = conv(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        return self.classifier(x).squeeze(-1)

class RelationAwareWeightedSAGEConv(nn.Module):
    def __init__(self, in_channels, out_channels, num_relations, relation_dim=16):
        super().__init__()
        self.self_linear = nn.Linear(in_channels, out_channels)
        self.neighbor_linear = nn.Linear(in_channels, out_channels)
        self.relation_embedding = nn.Embedding(num_relations, relation_dim)
        self.score_mlp = nn.Sequential(
            nn.Linear(in_channels * 2 + relation_dim, out_channels),
            nn.ReLU(),
            nn.Linear(out_channels, 1)
        )
        self.gate = nn.Linear(out_channels * 2, out_channels)

    def forward(self, x, edge_index, edge_type):
        src = edge_index[0]
        dst = edge_index[1]
        x_src = x[src]
        x_dst = x[dst]

        relation_vector = self.relation_embedding(edge_type)
        score_input = torch.cat([x_dst, x_src, relation_vector], dim=-1)
        scores = self.score_mlp(score_input).squeeze(-1)

        alpha = pyg_softmax(scores, dst)
        transformed_neighbors = self.neighbor_linear(x_src)
        messages = transformed_neighbors * alpha.unsqueeze(-1)

        aggregated = torch.zeros(x.size(0), messages.size(1), device=x.device, dtype=x.dtype)
        aggregated.index_add_(0, dst, messages)

        self_representation = self.self_linear(x)
        gate_input = torch.cat([self_representation, aggregated], dim=-1)
        gate = torch.sigmoid(self.gate(gate_input))

        output = gate * self_representation + (1.0 - gate) * aggregated
        return output

class AMRGGraphSAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels=64, num_relations=10, num_layers=2, dropout=0.30):
        super().__init__()
        self.layers = nn.ModuleList()
        self.norms = nn.ModuleList()

        self.layers.append(RelationAwareWeightedSAGEConv(in_channels, hidden_channels, num_relations))
        self.norms.append(nn.LayerNorm(hidden_channels))

        for _ in range(num_layers - 1):
            self.layers.append(RelationAwareWeightedSAGEConv(hidden_channels, hidden_channels, num_relations))
            self.norms.append(nn.LayerNorm(hidden_channels))

        self.scale_score = nn.Linear(hidden_channels, 1)
        self.dropout = dropout
        self.classifier = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, edge_type):
        layer_outputs = []
        for layer, norm in zip(self.layers, self.norms):
            x = layer(x, edge_index, edge_type)
            x = norm(x)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
            layer_outputs.append(x)

        H = torch.stack(layer_outputs, dim=1)
        scale_logits = self.scale_score(H).squeeze(-1)
        beta = torch.softmax(scale_logits, dim=1)
        z = torch.sum(H * beta.unsqueeze(-1), dim=1)
        return self.classifier(z).squeeze(-1)

def load_data_and_build_graph():
    print("Loading dataset from:", EXCEL_PATH)
    xls = pd.ExcelFile(EXCEL_PATH)
    df = pd.read_excel(xls, sheet_name="unified_dataset")
    edges_df = pd.read_excel(xls, sheet_name="graph_edges")

    # Cleaning
    df = df.drop_duplicates().copy()
    df = df.drop_duplicates(subset=["application_id"], keep="first").copy()
    df = df.dropna().reset_index(drop=True)

    numeric_features = [
        "cgpa", "backlogs", "aptitude_score_pre", "coding_score_pre", "communication_score_pre",
        "projects_count", "internships_count", "certifications_count", "resume_score",
        "expected_hiring_count", "minimum_cgpa", "experience_required_months", "salary_lpa",
        "relevant_experience_months", "total_skill_count", "average_skill_proficiency",
        "required_skill_count", "historical_selection_rate", "historical_average_selected_cgpa",
        "role_shift_score", "skill_match_ratio", "required_skill_level_gap", "role_experience_match"
    ]
    categorical_features = [
        "department", "industry", "company_size", "job_title", "job_domain"
    ]

    cycles = sorted(df["recruitment_cycle"].unique())
    train_cycles = cycles[:-2]
    val_cycles = [cycles[-2]]
    test_cycles = [cycles[-1]]

    train_df = df[df["recruitment_cycle"].isin(train_cycles)].copy()
    val_df = df[df["recruitment_cycle"].isin(val_cycles)].copy()
    test_df = df[df["recruitment_cycle"].isin(test_cycles)].copy()

    scaler = StandardScaler()
    X_train_num = scaler.fit_transform(train_df[numeric_features])
    X_val_num = scaler.transform(val_df[numeric_features])
    X_test_num = scaler.transform(test_df[numeric_features])

    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

    X_train_cat = encoder.fit_transform(train_df[categorical_features])
    X_val_cat = encoder.transform(val_df[categorical_features])
    X_test_cat = encoder.transform(test_df[categorical_features])

    X_train_app = np.hstack([X_train_num, X_train_cat]).astype(np.float32)
    X_val_app = np.hstack([X_val_num, X_val_cat]).astype(np.float32)
    X_test_app = np.hstack([X_test_num, X_test_cat]).astype(np.float32)

    base_feature_dim = X_train_app.shape[1]

    node_maps = {"application": {}, "student": {}, "company": {}, "job": {}, "skill": {}}
    next_node_id = 0

    def add_node(node_type, node_identifier):
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
    node_type_names = ["application", "student", "company", "job", "skill"]
    graph_feature_dim = base_feature_dim + len(node_type_names)
    X_graph = np.zeros((num_nodes, graph_feature_dim), dtype=np.float32)

    node_type_ids = {name: i for i, name in enumerate(node_type_names)}
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

    edge_src = []
    edge_dst = []
    edge_relation_names = []

    def add_edge(source, target, relation):
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

    relation_to_id = {}
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

    print(f"Graph constructed: {num_nodes} nodes, {edge_index.size(1)} edges, {len(relation_to_id)} relations")
    print(f"Masks: Train={train_mask.sum().item()}, Val={val_mask.sum().item()}, Test={test_mask.sum().item()}")
    return data, relation_to_id

def evaluate(model, data, mask):
    model.eval()
    with torch.no_grad():
        logits = model(data.x, data.edge_index, data.edge_type)
        probabilities = torch.sigmoid(logits[mask]).cpu().numpy()
        true = data.y[mask].cpu().numpy().astype(int)
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "Accuracy": float(accuracy_score(true, predictions)),
        "Precision": float(precision_score(true, predictions, zero_division=0)),
        "Recall": float(recall_score(true, predictions, zero_division=0)),
        "F1": float(f1_score(true, predictions, zero_division=0)),
        "ROC-AUC": float(roc_auc_score(true, probabilities))
    }

if __name__ == "__main__":
    data, relation_to_id = load_data_and_build_graph()

    print("\n--- Testing AMRG-GraphSAGE Checkpoint ---")
    amrg_model = AMRGGraphSAGE(
        in_channels=data.num_node_features,
        hidden_channels=128,
        num_relations=len(relation_to_id),
        num_layers=2,
        dropout=0.20
    ).to(device)
    amrg_model.load_state_dict(torch.load(AMRG_CHECKPOINT, map_location=device))
    amrg_res = evaluate(amrg_model, data, data.test_mask)
    for k, v in amrg_res.items():
        print(f"  {k:12s}: {v:.6f}")

    print("\n--- Testing Baseline GraphSAGE Checkpoint ---")
    baseline_model = BaselineGraphSAGE(
        in_channels=data.num_node_features,
        hidden_channels=64,
        num_layers=2,
        dropout=0.30
    ).to(device)
    baseline_model.load_state_dict(torch.load(BASELINE_CHECKPOINT, map_location=device))
    base_res = evaluate(baseline_model, data, data.test_mask)
    for k, v in base_res.items():
        print(f"  {k:12s}: {v:.6f}")
