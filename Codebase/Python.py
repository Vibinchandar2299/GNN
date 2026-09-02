# ================================================================
# FINAL GOOGLE COLAB PIPELINE
# GraphSAGE vs. Adaptive Multi-Scale Relation-Gated GraphSAGE
#
# Dataset:
#   unified_dataset
#   graph_edges
#   data_dictionary (optional)
#
# Main task:
#   Pre-interview binary prediction
#
# Output:
#   1. Dataset validation
#   2. Graph construction
#   3. Standard GraphSAGE
#   4. Proposed AMRG-GraphSAGE
#   5. Ablation study
#   6. Metrics
#   7. Figures 1, 2, 3
#   8. GNNExplainer
#   9. Prediction CSV
#  10. Model weights
# ================================================================

# ================================================================
# 1. INSTALL
# ================================================================
# pip install torch-geometric openpyxl scikit-learn matplotlib pandas numpy

# ================================================================
# 2. IMPORTS
# ================================================================
import os
import copy
import random
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
from torch_geometric.utils import softmax as pyg_softmax


# ================================================================
# 3. REPRODUCIBILITY
# ================================================================
SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("=" * 72)
print("ENVIRONMENT")
print("=" * 72)

print("PyTorch:", torch.__version__)

import torch_geometric

print(
    "PyTorch Geometric:",
    torch_geometric.__version__
)

print("Device:", device)

if torch.cuda.is_available():
    print(
        "GPU:",
        torch.cuda.get_device_name(0)
    )
else:
    print(
        "WARNING: Running on CPU. "
        "The optimized code should still run, "
        "but GPU is recommended."
    )


# ================================================================
# 4. UPLOAD FINAL EXCEL DATASET
# ================================================================
file_name = r"c:\Users\VIBIN\Vibin Projects\GNN\Dataset\GNN_Placement_Dataset.xlsx"
print("Local file:", file_name)


# ================================================================
# 5. LOAD WORKBOOK
# ================================================================
xls = pd.ExcelFile(file_name)

print("\nWorkbook sheets:")

for sheet in xls.sheet_names:
    print("  -", sheet)

if "unified_dataset" not in xls.sheet_names:
    raise ValueError(
        "Sheet 'unified_dataset' was not found."
    )

df = pd.read_excel(
    file_name,
    sheet_name="unified_dataset"
)

if "graph_edges" in xls.sheet_names:
    edges_df = pd.read_excel(
        file_name,
        sheet_name="graph_edges"
    )
else:
    edges_df = None

print("\nUnified dataset shape:", df.shape)

if edges_df is not None:
    print(
        "Graph edge table shape:",
        edges_df.shape
    )


# ================================================================
# 6. FINAL COLUMN DEFINITION
# ================================================================
id_columns = [
    "application_id",
    "student_id",
    "company_id",
    "job_id"
]

temporal_column = "recruitment_cycle"

direct_features = [
    "cgpa",
    "backlogs",
    "department",
    "aptitude_score_pre",
    "coding_score_pre",
    "communication_score_pre",
    "projects_count",
    "internships_count",
    "certifications_count",
    "resume_score",
    "industry",
    "company_size",
    "expected_hiring_count",
    "job_title",
    "job_domain",
    "minimum_cgpa",
    "experience_required_months",
    "salary_lpa"
]

derived_features = [
    "relevant_experience_months",
    "total_skill_count",
    "average_skill_proficiency",
    "required_skill_count",
    "historical_selection_rate",
    "historical_average_selected_cgpa",
    "role_shift_score",
    "skill_match_ratio",
    "required_skill_level_gap",
    "role_experience_match"
]

target_column = "final_status"

required_columns = (
    id_columns
    + [temporal_column]
    + direct_features
    + derived_features
    + [target_column]
)

missing_columns = [
    c for c in required_columns
    if c not in df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns:\n"
        + str(missing_columns)
    )

print("\nAll required columns are present.")

print(
    "Predictive feature count:",
    len(direct_features) + len(derived_features)
)


# ================================================================
# 7. DATA QUALITY VALIDATION
# ================================================================
print("\n" + "=" * 72)
print("DATA QUALITY VALIDATION")
print("=" * 72)

# Exact duplicates
duplicate_rows = int(
    df.duplicated().sum()
)

# Duplicate application IDs
duplicate_application_ids = int(
    df["application_id"].duplicated().sum()
)

print(
    "Duplicate rows:",
    duplicate_rows
)

print(
    "Duplicate application IDs:",
    duplicate_application_ids
)

if duplicate_rows > 0:
    df = df.drop_duplicates().copy()

if duplicate_application_ids > 0:
    df = (
        df
        .drop_duplicates(
            subset=["application_id"],
            keep="first"
        )
        .copy()
    )

# Missing values
missing_cells = int(
    df.isna().sum().sum()
)

print(
    "Missing/null cells:",
    missing_cells
)

if missing_cells > 0:
    print(
        "Removing incomplete rows..."
    )

    df = (
        df
        .dropna()
        .reset_index(drop=True)
    )

print(
    "Rows after cleaning:",
    len(df)
)

print(
    "Remaining null cells:",
    int(df.isna().sum().sum())
)

# Final duplicate checks
assert not df.duplicated().any()

assert df[
    "application_id"
].is_unique

assert (
    df.isna().sum().sum()
    == 0
)


# ================================================================
# 8. PRE-INTERVIEW LEAKAGE CHECK
# ================================================================
post_interview_fields = [
    "technical_score",
    "round_score",
    "interviewer_rating",
    "round_result",
    "final_interview_score",
    "rejection_stage",
    "offer_status",
    "joining_status",
    "final_comments",
    "decision_comment",
    "hr_feedback"
]

leakage_columns = [
    c for c in post_interview_fields
    if c in df.columns
]

if leakage_columns:
    raise ValueError(
        "Post-interview fields detected:\n"
        + str(leakage_columns)
    )

print(
    "Pre-interview leakage check: PASSED"
)


# ================================================================
# 9. TARGET VALIDATION
# ================================================================
if not set(
    df[target_column].unique()
).issubset({0, 1}):

    raise ValueError(
        "final_status must contain only 0 and 1."
    )

print("\nTarget distribution:")

print(
    df[target_column]
    .value_counts()
    .rename("count")
    .to_frame()
)

print("\nTarget proportions:")

print(
    df[target_column]
    .value_counts(
        normalize=True
    )
    .rename("proportion")
    .to_frame()
)


# ================================================================
# 10. RANGE CHECKS
# ================================================================
range_checks = {

    "cgpa": (0, 10),

    "backlogs": (0, None),

    "aptitude_score_pre": (0, 100),

    "coding_score_pre": (0, 100),

    "communication_score_pre": (0, 100),

    "projects_count": (0, None),

    "internships_count": (0, None),

    "certifications_count": (0, None),

    "resume_score": (0, 100),

    "historical_selection_rate": (0, 1),

    "role_shift_score": (0, 1),

    "skill_match_ratio": (0, 1),

    "role_experience_match": (0, 1)
}

for feature, (low, high) in range_checks.items():

    if low is not None:

        if not (
            df[feature] >= low
        ).all():

            raise ValueError(
                f"{feature} has values below {low}"
            )

    if high is not None:

        if not (
            df[feature] <= high
        ).all():

            raise ValueError(
                f"{feature} has values above {high}"
            )

print(
    "Range validation: PASSED"
)


# ================================================================
# 11. TEMPORAL TRAIN / VALIDATION / TEST SPLIT
# ================================================================
print("\n" + "=" * 72)
print("TEMPORAL SPLIT")
print("=" * 72)

cycles = sorted(
    df[temporal_column]
    .unique()
)

print(
    "Available cycles:",
    cycles
)

if len(cycles) < 3:
    raise ValueError(
        "At least 3 recruitment cycles are required."
    )

train_cycles = cycles[:-2]
val_cycles = [cycles[-2]]
test_cycles = [cycles[-1]]

train_df = df[
    df[temporal_column]
    .isin(train_cycles)
].copy()

val_df = df[
    df[temporal_column]
    .isin(val_cycles)
].copy()

test_df = df[
    df[temporal_column]
    .isin(test_cycles)
].copy()

print(
    "Training cycles:",
    train_cycles
)

print(
    "Validation cycle:",
    val_cycles
)

print(
    "Test cycle:",
    test_cycles
)

print(
    "\nTrain:",
    train_df.shape
)

print(
    "Validation:",
    val_df.shape
)

print(
    "Test:",
    test_df.shape
)


# ================================================================
# 12. FEATURE PREPROCESSING
# ================================================================
numeric_features = [
    "cgpa",
    "backlogs",
    "aptitude_score_pre",
    "coding_score_pre",
    "communication_score_pre",
    "projects_count",
    "internships_count",
    "certifications_count",
    "resume_score",
    "expected_hiring_count",
    "minimum_cgpa",
    "experience_required_months",
    "salary_lpa",
    "relevant_experience_months",
    "total_skill_count",
    "average_skill_proficiency",
    "required_skill_count",
    "historical_selection_rate",
    "historical_average_selected_cgpa",
    "role_shift_score",
    "skill_match_ratio",
    "required_skill_level_gap",
    "role_experience_match"
]

categorical_features = [
    "department",
    "industry",
    "company_size",
    "job_title",
    "job_domain"
]

# Numerical features
scaler = StandardScaler()

X_train_num = scaler.fit_transform(
    train_df[numeric_features]
)

X_val_num = scaler.transform(
    val_df[numeric_features]
)

X_test_num = scaler.transform(
    test_df[numeric_features]
)

# Categorical features
try:

    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    )

except TypeError:

    encoder = OneHotEncoder(
        handle_unknown="ignore",
        sparse=False
    )

X_train_cat = encoder.fit_transform(
    train_df[categorical_features]
)

X_val_cat = encoder.transform(
    val_df[categorical_features]
)

X_test_cat = encoder.transform(
    test_df[categorical_features]
)

# Final application feature matrices
X_train_app = np.hstack(
    [
        X_train_num,
        X_train_cat
    ]
).astype(np.float32)

X_val_app = np.hstack(
    [
        X_val_num,
        X_val_cat
    ]
).astype(np.float32)

X_test_app = np.hstack(
    [
        X_test_num,
        X_test_cat
    ]
).astype(np.float32)

print(
    "\nEncoded application feature dimension:",
    X_train_app.shape[1]
)


# ================================================================
# 13. GRAPH NODE INDEXING
# ================================================================
print("\n" + "=" * 72)
print("GRAPH CONSTRUCTION")
print("=" * 72)

node_maps = {
    "application": {},
    "student": {},
    "company": {},
    "job": {},
    "skill": {}
}

next_node_id = 0

def add_node(
    node_type,
    node_identifier
):

    global next_node_id

    if (
        node_identifier
        not in node_maps[node_type]
    ):

        node_maps[node_type][
            node_identifier
        ] = next_node_id

        next_node_id += 1

    return node_maps[node_type][
        node_identifier
    ]


all_df = pd.concat(
    [
        train_df,
        val_df,
        test_df
    ],
    ignore_index=True
)

# Application/student/company/job nodes
for row in all_df.itertuples(
    index=False
):

    add_node(
        "application",
        row.application_id
    )

    add_node(
        "student",
        row.student_id
    )

    add_node(
        "company",
        row.company_id
    )

    add_node(
        "job",
        row.job_id
    )

# Skill nodes
if edges_df is not None:

    for row in edges_df.itertuples(
        index=False
    ):

        src = str(
            row.source_id
        )

        dst = str(
            row.target_id
        )

        if src.startswith("SK_"):

            add_node(
                "skill",
                src
            )

        if dst.startswith("SK_"):

            add_node(
                "skill",
                dst
            )

num_nodes = next_node_id

print(
    "Application nodes:",
    len(node_maps["application"])
)

print(
    "Student nodes:",
    len(node_maps["student"])
)

print(
    "Company nodes:",
    len(node_maps["company"])
)

print(
    "Job nodes:",
    len(node_maps["job"])
)

print(
    "Skill nodes:",
    len(node_maps["skill"])
)

print(
    "Total nodes:",
    num_nodes
)


# ================================================================
# 14. NODE FEATURE MATRIX
# ================================================================
base_feature_dim = X_train_app.shape[1]

node_type_names = [
    "application",
    "student",
    "company",
    "job",
    "skill"
]

graph_feature_dim = (
    base_feature_dim
    + len(node_type_names)
)

X_graph = np.zeros(
    (
        num_nodes,
        graph_feature_dim
    ),
    dtype=np.float32
)

node_type_ids = {
    name: i
    for i, name in enumerate(
        node_type_names
    )
}

for node_type, mapping in node_maps.items():

    t = node_type_ids[node_type]

    for node_idx in mapping.values():

        X_graph[
            node_idx,
            base_feature_dim + t
        ] = 1.0


# Add application features
for subset_df, X_subset in [
    (
        train_df,
        X_train_app
    ),
    (
        val_df,
        X_val_app
    ),
    (
        test_df,
        X_test_app
    )
]:

    for app_id, vector in zip(
        subset_df["application_id"],
        X_subset
    ):

        idx = node_maps[
            "application"
        ][app_id]

        X_graph[
            idx,
            :base_feature_dim
        ] = vector


# ================================================================
# 15. GRAPH EDGE CONSTRUCTION
# ================================================================
edge_src = []
edge_dst = []
edge_relation_names = []

def add_edge(
    source,
    target,
    relation
):

    edge_src.append(source)
    edge_dst.append(target)
    edge_relation_names.append(
        relation
    )


# Application ↔ entity relationships
for row in all_df.itertuples(
    index=False
):

    app = node_maps[
        "application"
    ][row.application_id]

    student = node_maps[
        "student"
    ][row.student_id]

    company = node_maps[
        "company"
    ][row.company_id]

    job = node_maps[
        "job"
    ][row.job_id]

    # Application ↔ Student
    add_edge(
        app,
        student,
        "APPLICATION_STUDENT"
    )

    add_edge(
        student,
        app,
        "STUDENT_APPLICATION"
    )

    # Application ↔ Company
    add_edge(
        app,
        company,
        "APPLICATION_COMPANY"
    )

    add_edge(
        company,
        app,
        "COMPANY_APPLICATION"
    )

    # Application ↔ Job
    add_edge(
        app,
        job,
        "APPLICATION_JOB"
    )

    add_edge(
        job,
        app,
        "JOB_APPLICATION"
    )


# Additional typed graph relations
if edges_df is not None:

    for row in edges_df.itertuples(
        index=False
    ):

        src_id = str(
            row.source_id
        )

        relation = str(
            row.relation_type
        )

        dst_id = str(
            row.target_id
        )

        # Student -> Skill
        if (
            src_id
            in node_maps["student"]
            and
            dst_id
            in node_maps["skill"]
        ):

            src = node_maps[
                "student"
            ][src_id]

            dst = node_maps[
                "skill"
            ][dst_id]

            add_edge(
                src,
                dst,
                relation
            )

            add_edge(
                dst,
                src,
                "REV_" + relation
            )

        # Job -> Skill
        elif (
            src_id
            in node_maps["job"]
            and
            dst_id
            in node_maps["skill"]
        ):

            src = node_maps[
                "job"
            ][src_id]

            dst = node_maps[
                "skill"
            ][dst_id]

            add_edge(
                src,
                dst,
                relation
            )

            add_edge(
                dst,
                src,
                "REV_" + relation
            )

        # Job -> Company
        elif (
            src_id
            in node_maps["job"]
            and
            dst_id
            in node_maps["company"]
        ):

            src = node_maps[
                "job"
            ][src_id]

            dst = node_maps[
                "company"
            ][dst_id]

            add_edge(
                src,
                dst,
                relation
            )

            add_edge(
                dst,
                src,
                "REV_" + relation
            )


# Register relation types
relation_to_id = {}

for relation in edge_relation_names:

    if relation not in relation_to_id:

        relation_to_id[
            relation
        ] = len(relation_to_id)


edge_type = torch.tensor(
    [
        relation_to_id[r]
        for r in edge_relation_names
    ],
    dtype=torch.long
)

edge_index = torch.tensor(
    [
        edge_src,
        edge_dst
    ],
    dtype=torch.long
)

x_graph = torch.tensor(
    X_graph,
    dtype=torch.float32
)

print(
    "\nGraph edges:",
    edge_index.shape[1]
)

print(
    "Relation types:",
    len(relation_to_id)
)


# ================================================================
# 16. TARGET / TEMPORAL MASKS
# ================================================================
y = torch.full(
    (num_nodes,),
    -1.0,
    dtype=torch.float32
)

train_mask = torch.zeros(
    num_nodes,
    dtype=torch.bool
)

val_mask = torch.zeros(
    num_nodes,
    dtype=torch.bool
)

test_mask = torch.zeros(
    num_nodes,
    dtype=torch.bool
)


for row in train_df.itertuples(
    index=False
):

    idx = node_maps[
        "application"
    ][row.application_id]

    train_mask[idx] = True

    y[idx] = float(
        row.final_status
    )


for row in val_df.itertuples(
    index=False
):

    idx = node_maps[
        "application"
    ][row.application_id]

    val_mask[idx] = True

    y[idx] = float(
        row.final_status
    )


for row in test_df.itertuples(
    index=False
):

    idx = node_maps[
        "application"
    ][row.application_id]

    test_mask[idx] = True

    y[idx] = float(
        row.final_status
    )


data = Data(
    x=x_graph,
    edge_index=edge_index,
    edge_type=edge_type,
    y=y,
    train_mask=train_mask,
    val_mask=val_mask,
    test_mask=test_mask
)

data = data.to(device)

print(
    "\nPyG Data:"
)

print(data)


# ================================================================
# 17. STANDARD GRAPHSAGE BASELINE
# ================================================================
class BaselineGraphSAGE(
    nn.Module
):

    def __init__(
        self,
        in_channels,
        hidden_channels=64,
        num_layers=2,
        dropout=0.30
    ):

        super().__init__()

        self.convs = nn.ModuleList()

        self.convs.append(
            SAGEConv(
                in_channels,
                hidden_channels
            )
        )

        for _ in range(
            num_layers - 1
        ):

            self.convs.append(
                SAGEConv(
                    hidden_channels,
                    hidden_channels
                )
            )

        self.dropout = dropout

        self.classifier = nn.Linear(
            hidden_channels,
            1
        )


    def forward(
        self,
        x,
        edge_index,
        edge_type=None
    ):

        for conv in self.convs:

            x = conv(
                x,
                edge_index
            )

            x = F.relu(x)

            x = F.dropout(
                x,
                p=self.dropout,
                training=self.training
            )

        return self.classifier(
            x
        ).squeeze(-1)


# ================================================================
# 18. OPTIMIZED RELATION-AWARE SAGE LAYER
# ================================================================
class RelationAwareWeightedSAGEConv(
    nn.Module
):

    def __init__(
        self,
        in_channels,
        out_channels,
        num_relations,
        relation_dim=16
    ):

        super().__init__()

        self.self_linear = nn.Linear(
            in_channels,
            out_channels
        )

        self.neighbor_linear = nn.Linear(
            in_channels,
            out_channels
        )

        self.relation_embedding = nn.Embedding(
            num_relations,
            relation_dim
        )

        self.score_mlp = nn.Sequential(

            nn.Linear(
                in_channels * 2
                + relation_dim,
                out_channels
            ),

            nn.ReLU(),

            nn.Linear(
                out_channels,
                1
            )
        )

        self.gate = nn.Linear(
            out_channels * 2,
            out_channels
        )


    def forward(
        self,
        x,
        edge_index,
        edge_type
    ):

        src = edge_index[0]
        dst = edge_index[1]

        x_src = x[src]
        x_dst = x[dst]

        relation_vector = (
            self.relation_embedding(
                edge_type
            )
        )

        score_input = torch.cat(
            [
                x_dst,
                x_src,
                relation_vector
            ],
            dim=-1
        )

        scores = (
            self.score_mlp(
                score_input
            )
            .squeeze(-1)
        )

        # --------------------------------------------------------
        # IMPORTANT PERFORMANCE FIX
        #
        # Old version:
        #   for every destination node:
        #       calculate softmax
        #
        # New version:
        #   fully vectorized graph-wise softmax
        # --------------------------------------------------------
        alpha = pyg_softmax(
            scores,
            dst
        )

        transformed_neighbors = (
            self.neighbor_linear(
                x_src
            )
        )

        messages = (
            transformed_neighbors
            *
            alpha.unsqueeze(-1)
        )

        aggregated = torch.zeros(
            x.size(0),
            messages.size(1),
            device=x.device,
            dtype=x.dtype
        )

        aggregated.index_add_(
            0,
            dst,
            messages
        )

        self_representation = (
            self.self_linear(x)
        )

        gate_input = torch.cat(
            [
                self_representation,
                aggregated
            ],
            dim=-1
        )

        gate = torch.sigmoid(
            self.gate(
                gate_input
            )
        )

        output = (
            gate
            * self_representation
            +
            (1.0 - gate)
            * aggregated
        )

        return output


# ================================================================
# 19. PROPOSED AMRG-GRAPHSAGE
# ================================================================
class AMRGGraphSAGE(
    nn.Module
):

    def __init__(
        self,
        in_channels,
        hidden_channels=64,
        num_relations=10,
        num_layers=2,
        dropout=0.30
    ):

        super().__init__()

        self.layers = nn.ModuleList()
        self.norms = nn.ModuleList()

        self.layers.append(
            RelationAwareWeightedSAGEConv(
                in_channels,
                hidden_channels,
                num_relations
            )
        )
        self.norms.append(nn.LayerNorm(hidden_channels))

        for _ in range(
            num_layers - 1
        ):

            self.layers.append(
                RelationAwareWeightedSAGEConv(
                    hidden_channels,
                    hidden_channels,
                    num_relations
                )
            )
            self.norms.append(nn.LayerNorm(hidden_channels))

        # Adaptive multi-scale weighting
        self.scale_score = nn.Linear(
            hidden_channels,
            1
        )

        self.dropout = dropout

        self.classifier = nn.Linear(
            hidden_channels,
            1
        )


    def forward(
        self,
        x,
        edge_index,
        edge_type
    ):

        layer_outputs = []

        for layer, norm in zip(self.layers, self.norms):

            x = layer(
                x,
                edge_index,
                edge_type
            )
            
            x = norm(x)

            x = F.relu(x)

            x = F.dropout(
                x,
                p=self.dropout,
                training=self.training
            )

            layer_outputs.append(x)

        # Stack representations from different graph depths
        H = torch.stack(
            layer_outputs,
            dim=1
        )

        scale_logits = (
            self.scale_score(H)
            .squeeze(-1)
        )

        beta = torch.softmax(
            scale_logits,
            dim=1
        )

        # Adaptive multi-scale fusion
        z = torch.sum(
            H
            *
            beta.unsqueeze(-1),
            dim=1
        )

        return self.classifier(
            z
        ).squeeze(-1)


# ================================================================
# 20. PAIRWISE RANKING LOSS
# ================================================================
def ranking_loss(
    logits,
    labels,
    margin=0.20,
    max_pairs=512
):

    positive_idx = torch.where(
        labels == 1
    )[0]

    negative_idx = torch.where(
        labels == 0
    )[0]

    if (
        len(positive_idx) == 0
        or len(negative_idx) == 0
    ):

        return torch.tensor(
            0.0,
            device=logits.device
        )

    n = min(
        max_pairs,
        len(positive_idx),
        len(negative_idx)
    )

    positive_selection = (
        torch.randperm(
            len(positive_idx),
            device=logits.device
        )[:n]
    )

    negative_selection = (
        torch.randperm(
            len(negative_idx),
            device=logits.device
        )[:n]
    )

    pos = logits[
        positive_idx[
            positive_selection
        ]
    ]

    neg = logits[
        negative_idx[
            negative_selection
        ]
    ]

    return F.relu(
        margin
        - pos
        + neg
    ).mean()


# ================================================================
# 21. EVALUATION
# ================================================================
def evaluate_model(
    model,
    graph,
    mask
):

    model.eval()

    with torch.no_grad():

        logits = model(
            graph.x,
            graph.edge_index,
            graph.edge_type
        )

        probabilities = torch.sigmoid(
            logits[mask]
        ).cpu().numpy()

        true = (
            graph.y[mask]
            .cpu()
            .numpy()
            .astype(int)
        )

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    results = {

        "Accuracy":
            accuracy_score(
                true,
                predictions
            ),

        "Precision":
            precision_score(
                true,
                predictions,
                zero_division=0
            ),

        "Recall":
            recall_score(
                true,
                predictions,
                zero_division=0
            ),

        "F1":
            f1_score(
                true,
                predictions,
                zero_division=0
            ),

        "ROC-AUC":
            roc_auc_score(
                true,
                probabilities
            )
    }

    return (
        results,
        true,
        predictions,
        probabilities
    )


# ================================================================
# 22. TRAINING FUNCTION
# ================================================================
def train_model(
    model,
    graph,
    epochs=120,
    lr=1e-3,
    weight_decay=1e-4,
    ranking_lambda=0.0,
    patience=15,
    pos_weight=1.0
):

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=lr,
        weight_decay=weight_decay
    )

    best_state = None

    best_val_f1 = -np.inf

    patience_counter = 0

    history = {

        "train_loss": [],

        "val_f1": [],

        "val_auc": []
    }

    for epoch in range(
        1,
        epochs + 1
    ):

        model.train()

        optimizer.zero_grad()

        logits = model(
            graph.x,
            graph.edge_index,
            graph.edge_type
        )

        train_logits = logits[
            graph.train_mask
        ]

        train_labels = graph.y[
            graph.train_mask
        ]

        bce_loss = F.binary_cross_entropy_with_logits(
            train_logits,
            train_labels,
            reduction='none'
        )
        if pos_weight is not None and pos_weight != 1.0:
            weight = torch.ones_like(train_labels)
            weight[train_labels == 1] = float(pos_weight)
            bce = (bce_loss * weight).mean()
        else:
            bce = bce_loss.mean()

        if ranking_lambda > 0:

            rank = ranking_loss(
                train_logits,
                train_labels
            )

        else:

            rank = torch.tensor(
                0.0,
                device=graph.x.device
            )

        loss = (
            (1.0 - ranking_lambda)
            * bce
            +
            ranking_lambda
            * rank
        )

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=2.0
        )

        optimizer.step()

        # ---------------------------
        # Validation
        # ---------------------------
        model.eval()

        with torch.no_grad():

            validation_logits = model(
                graph.x,
                graph.edge_index,
                graph.edge_type
            )

            validation_prob = torch.sigmoid(
                validation_logits[
                    graph.val_mask
                ]
            ).cpu().numpy()

            validation_true = (
                graph.y[
                    graph.val_mask
                ]
                .cpu()
                .numpy()
                .astype(int)
            )

            validation_pred = (
                validation_prob >= 0.5
            ).astype(int)

            validation_f1 = f1_score(
                validation_true,
                validation_pred,
                zero_division=0
            )

            validation_auc = roc_auc_score(
                validation_true,
                validation_prob
            )

        history[
            "train_loss"
        ].append(
            float(loss.item())
        )

        history[
            "val_f1"
        ].append(
            float(validation_f1)
        )

        history[
            "val_auc"
        ].append(
            float(validation_auc)
        )

        # Best validation model
        if (
            validation_f1
            >
            best_val_f1
        ):

            best_val_f1 = (
                validation_f1
            )

            best_state = copy.deepcopy(
                model.state_dict()
            )

            patience_counter = 0

        else:

            patience_counter += 1

        if epoch == 1 or epoch % 10 == 0:

            print(
                f"Epoch {epoch:03d} | "
                f"Loss={loss.item():.4f} | "
                f"Val F1={validation_f1:.4f} | "
                f"Val AUC={validation_auc:.4f}"
            )

        if (
            patience_counter
            >= patience
        ):

            print(
                "Early stopping at epoch",
                epoch
            )

            break

    if best_state is not None:

        model.load_state_dict(
            best_state
        )

    return (
        model,
        history
    )


# ================================================================
# 23. TRAIN STANDARD GRAPHSAGE
# ================================================================
print("\n" + "=" * 72)
print("TRAINING STANDARD GRAPHSAGE")
print("=" * 72)

baseline_model = BaselineGraphSAGE(
    in_channels=data.num_node_features,
    hidden_channels=64,
    num_layers=2,
    dropout=0.30
).to(device)

baseline_model, baseline_history = train_model(
    baseline_model,
    data,
    epochs=120,
    lr=1e-3,
    weight_decay=1e-4,
    ranking_lambda=0.0,
    patience=15
)

(
    baseline_results,
    baseline_true,
    baseline_pred,
    baseline_prob
) = evaluate_model(
    baseline_model,
    data,
    data.test_mask
)

print(
    "\nSTANDARD GRAPHSAGE TEST RESULTS"
)

for metric, value in baseline_results.items():

    print(
        f"{metric:10s}: {value:.4f}"
    )


# ================================================================
# 24. TRAIN PROPOSED AMRG-GRAPHSAGE
# ================================================================
print("\n" + "=" * 72)
print("TRAINING PROPOSED AMRG-GRAPHSAGE")
print("=" * 72)

proposed_model = AMRGGraphSAGE(
    in_channels=data.num_node_features,
    hidden_channels=128,
    num_relations=len(relation_to_id),
    num_layers=2,
    dropout=0.20
).to(device)

proposed_model, proposed_history = train_model(
    proposed_model,
    data,
    epochs=400,
    lr=1e-3,
    weight_decay=1e-4,
    ranking_lambda=0.08,
    patience=50,
    pos_weight=1.12
)

(
    proposed_results,
    proposed_true,
    proposed_pred,
    proposed_prob
) = evaluate_model(
    proposed_model,
    data,
    data.test_mask
)

print(
    "\nPROPOSED AMRG-GRAPHSAGE TEST RESULTS"
)

for metric, value in proposed_results.items():

    print(
        f"{metric:10s}: {value:.4f}"
    )


# ================================================================
# 25. MODEL COMPARISON
# ================================================================
comparison = pd.DataFrame({

    "Metric":
        list(
            baseline_results.keys()
        ),

    "Standard_GraphSAGE":
        list(
            baseline_results.values()
        ),

    "AMRG_GraphSAGE":
        list(
            proposed_results.values()
        )
})

comparison[
    "Improvement"
] = (
    comparison[
        "AMRG_GraphSAGE"
    ]
    -
    comparison[
        "Standard_GraphSAGE"
    ]
)

print(
    "\n" + "=" * 72
)
print(
    "BASELINE VS PROPOSED"
)
print(
    "=" * 72
)

print(comparison)


# ================================================================
# 26. CLASSIFICATION REPORT
# ================================================================
print(
    "\nPROPOSED MODEL CLASSIFICATION REPORT"
)

print(
    classification_report(
        proposed_true,
        proposed_pred,
        target_names=[
            "Rejected",
            "Selected"
        ],
        zero_division=0
    )
)


# ================================================================
# 27. CONFUSION MATRIX
# ================================================================
cm = confusion_matrix(
    proposed_true,
    proposed_pred
)

plt.figure(
    figsize=(6, 5)
)

plt.imshow(cm)

plt.xticks(
    [0, 1],
    ["Rejected", "Selected"]
)

plt.yticks(
    [0, 1],
    ["Rejected", "Selected"]
)

plt.xlabel(
    "Predicted"
)

plt.ylabel(
    "Actual"
)

plt.title(
    "AMRG-GraphSAGE Confusion Matrix"
)

for i in range(2):

    for j in range(2):

        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center"
        )

plt.colorbar()

plt.tight_layout()

plt.close('all')


# ================================================================
# 28. TRAINING LOSS
# ================================================================
plt.figure(
    figsize=(8, 5)
)

plt.plot(
    baseline_history[
        "train_loss"
    ],
    label="Standard GraphSAGE"
)

plt.plot(
    proposed_history[
        "train_loss"
    ],
    label="AMRG-GraphSAGE"
)

plt.xlabel(
    "Epoch"
)

plt.ylabel(
    "Training Loss"
)

plt.title(
    "Training Loss Comparison"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.close('all')


# ================================================================
# 29. VALIDATION F1
# ================================================================
plt.figure(
    figsize=(8, 5)
)

plt.plot(
    baseline_history[
        "val_f1"
    ],
    label="Standard GraphSAGE"
)

plt.plot(
    proposed_history[
        "val_f1"
    ],
    label="AMRG-GraphSAGE"
)

plt.xlabel(
    "Epoch"
)

plt.ylabel(
    "Validation F1"
)

plt.title(
    "Validation F1 Comparison"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.close('all')


# ================================================================
# 30. DRAWING HELPERS FOR METHODOLOGY FIGURES
# ================================================================
def draw_box(
    ax,
    x,
    y,
    w,
    h,
    text,
    fontsize=10
):

    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02"
    )

    ax.add_patch(box)

    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize
    )


def draw_arrow(
    ax,
    x1,
    y1,
    x2,
    y2
):

    arrow = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="->",
        mutation_scale=15
    )

    ax.add_patch(
        arrow
    )


# ================================================================
# 31. FIGURE 1
# ================================================================
print(
    "\nDisplaying FIGURE 1"
)

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.set_xlim(
    0,
    12
)

ax.set_ylim(
    0,
    5
)

ax.axis(
    "off"
)

draw_box(
    ax,
    0.3,
    2.0,
    1.8,
    0.9,
    "Unified\nDataset"
)

draw_box(
    ax,
    2.7,
    2.0,
    1.8,
    0.9,
    "Preprocessing"
)

draw_box(
    ax,
    5.1,
    2.0,
    1.8,
    0.9,
    "Feature\nEncoding"
)

draw_box(
    ax,
    7.5,
    2.0,
    1.8,
    0.9,
    "Node & Edge\nConstruction"
)

draw_box(
    ax,
    9.9,
    2.0,
    1.8,
    0.9,
    "Graph"
)

draw_arrow(
    ax,
    2.1,
    2.45,
    2.7,
    2.45
)

draw_arrow(
    ax,
    4.5,
    2.45,
    5.1,
    2.45
)

draw_arrow(
    ax,
    6.9,
    2.45,
    7.5,
    2.45
)

draw_arrow(
    ax,
    9.3,
    2.45,
    9.9,
    2.45
)

ax.set_title(
    "Fig. 1. Unified Feature-to-Graph Construction Pipeline",
    fontsize=13
)

plt.tight_layout()

plt.close('all')


# ================================================================
# 32. FIGURE 2
# ================================================================
print(
    "\nDisplaying FIGURE 2"
)

fig, ax = plt.subplots(
    figsize=(13, 7)
)

ax.set_xlim(
    0,
    13
)

ax.set_ylim(
    0,
    8
)

ax.axis(
    "off"
)

draw_box(
    ax,
    5.2,
    6.5,
    2.4,
    0.8,
    "Input Graph"
)

# Baseline branch
draw_box(
    ax,
    0.8,
    4.8,
    2.8,
    0.9,
    "Standard GraphSAGE"
)

draw_box(
    ax,
    0.8,
    2.9,
    2.8,
    0.9,
    "Uniform\nAggregation"
)

draw_box(
    ax,
    0.8,
    1.0,
    2.8,
    0.9,
    "Prediction"
)

# Proposed branch
draw_box(
    ax,
    4.5,
    5.0,
    3.0,
    0.8,
    "Relation-Aware\nNeighbor Scoring"
)

draw_box(
    ax,
    8.3,
    5.0,
    3.0,
    0.8,
    "Adaptive Neighbor\nWeighting"
)

draw_box(
    ax,
    4.5,
    3.0,
    3.0,
    0.8,
    "Feature-Confidence\nGating"
)

draw_box(
    ax,
    8.3,
    3.0,
    3.0,
    0.8,
    "Adaptive Multi-Scale\nFusion"
)

draw_box(
    ax,
    6.3,
    1.0,
    3.0,
    0.9,
    "Proposed Prediction"
)

draw_arrow(
    ax,
    6.4,
    6.5,
    2.2,
    5.7
)

draw_arrow(
    ax,
    6.4,
    6.5,
    6.0,
    5.8
)

draw_arrow(
    ax,
    7.5,
    5.4,
    8.3,
    5.4
)

draw_arrow(
    ax,
    6.0,
    5.0,
    6.0,
    3.8
)

draw_arrow(
    ax,
    9.8,
    5.0,
    9.8,
    3.8
)

draw_arrow(
    ax,
    6.0,
    3.0,
    7.2,
    1.95
)

draw_arrow(
    ax,
    9.8,
    3.0,
    8.4,
    1.95
)

draw_arrow(
    ax,
    2.2,
    4.8,
    2.2,
    3.8
)

draw_arrow(
    ax,
    2.2,
    2.9,
    2.2,
    1.95
)

ax.set_title(
    "Fig. 2. Standard GraphSAGE and Proposed AMRG-GraphSAGE Architecture",
    fontsize=13
)

plt.tight_layout()

plt.close('all')


# ================================================================
# 33. FIGURE 3
# ================================================================
print(
    "\nDisplaying FIGURE 3"
)

fig, ax = plt.subplots(
    figsize=(12, 6)
)

ax.set_xlim(
    0,
    12
)

ax.set_ylim(
    0,
    7
)

ax.axis(
    "off"
)

draw_box(
    ax,
    0.4,
    2.8,
    2.0,
    0.9,
    "Graph"
)

draw_box(
    ax,
    3.0,
    2.8,
    2.3,
    0.9,
    "AMRG-\nGraphSAGE"
)

draw_box(
    ax,
    5.9,
    2.8,
    2.0,
    0.9,
    "Prediction"
)

draw_box(
    ax,
    8.5,
    4.5,
    2.5,
    0.9,
    "GNNExplainer"
)

draw_box(
    ax,
    8.5,
    2.8,
    2.5,
    0.9,
    "Important\nFeatures / Edges"
)

draw_box(
    ax,
    8.5,
    1.2,
    2.5,
    0.9,
    "Explanation"
)

draw_box(
    ax,
    5.8,
    5.1,
    2.2,
    0.9,
    "Actual\nOutcome"
)

draw_box(
    ax,
    3.0,
    1.2,
    2.3,
    0.9,
    "Correct /\nIncorrect"
)

draw_box(
    ax,
    0.4,
    1.2,
    2.0,
    0.9,
    "Error\nAnalysis"
)

draw_arrow(
    ax,
    2.4,
    3.25,
    3.0,
    3.25
)

draw_arrow(
    ax,
    5.3,
    3.25,
    5.9,
    3.25
)

draw_arrow(
    ax,
    7.9,
    3.7,
    8.5,
    4.55
)

draw_arrow(
    ax,
    9.75,
    4.5,
    9.75,
    3.7
)

draw_arrow(
    ax,
    9.75,
    2.8,
    9.75,
    2.1
)

draw_arrow(
    ax,
    6.9,
    5.1,
    6.9,
    3.7
)

draw_arrow(
    ax,
    5.8,
    5.55,
    5.3,
    2.0
)

draw_arrow(
    ax,
    3.0,
    1.65,
    2.4,
    1.65
)

draw_arrow(
    ax,
    3.0,
    1.65,
    5.3,
    1.65
)

ax.set_title(
    "Fig. 3. Explainable Prediction and Prediction Error Analysis Framework",
    fontsize=13
)

plt.tight_layout()

plt.close('all')


# ================================================================
# 34. GNNEXPLAINER
# ================================================================
print(
    "\n" + "=" * 72
)

print(
    "GNNEXPLAINER"
)

print(
    "=" * 72
)

try:

    from torch_geometric.explain import (
        Explainer,
        GNNExplainer
    )

    proposed_model.eval()

    test_nodes = torch.where(
        data.test_mask
    )[0]

    if len(test_nodes) == 0:

        print(
            "No test application nodes found."
        )

    else:

        # Choose first test application
        sample_node = (
            test_nodes[0]
            .item()
        )

        print(
            "Explaining graph node:",
            sample_node
        )

        try:

            explainer = Explainer(
                model=proposed_model,
                algorithm=GNNExplainer(
                    epochs=100
                ),
                explanation_type="model",
                node_mask_type="attributes",
                edge_mask_type="object",
                model_config=dict(
                    mode="binary_classification",
                    task_level="node",
                    return_type="raw"
                )
            )

            explanation = explainer(
                data.x,
                data.edge_index,
                edge_type=data.edge_type,
                index=sample_node
            )

            print(
                explanation
            )

            if explanation.node_mask is not None:

                mask = (
                    explanation
                    .node_mask[
                        sample_node
                    ]
                    .detach()
                    .cpu()
                    .numpy()
                )

                feature_names = (
                    numeric_features
                    +
                    list(
                        encoder
                        .get_feature_names_out(
                            categorical_features
                        )
                    )
                    +
                    [
                        "node_type_application",
                        "node_type_student",
                        "node_type_company",
                        "node_type_job",
                        "node_type_skill"
                    ]
                )

                usable = min(
                    len(mask),
                    len(feature_names)
                )

                ranking = np.argsort(
                    mask[:usable]
                )[::-1]

                print(
                    "\nTop influential feature dimensions:"
                )

                for idx in ranking[:15]:

                    print(
                        f"{feature_names[idx]:45s}"
                        f"{mask[idx]:.6f}"
                    )

        except Exception as xai_error:

            print(
                "\nGNNExplainer could not be executed "
                "with this installed PyG configuration."
            )

            print(
                "Error:",
                str(xai_error)
            )

            print(
                "\nPrediction model itself is unaffected."
            )

except Exception as import_error:

    print(
        "PyG Explain module unavailable."
    )

    print(
        "Error:",
        str(import_error)
    )


# ================================================================
# 35. PREDICTION EXPORT
# ================================================================
print(
    "\n" + "=" * 72
)

print(
    "EXPORTING PREDICTIONS AND MODELS"
)

print(
    "=" * 72
)

proposed_model.eval()

with torch.no_grad():

    all_logits = proposed_model(
        data.x,
        data.edge_index,
        data.edge_type
    )

    all_probabilities = (
        torch.sigmoid(
            all_logits
        )
        .cpu()
        .numpy()
    )

prediction_rows = []

for row in df.itertuples(
    index=False
):

    application_node = (
        node_maps[
            "application"
        ][row.application_id]
    )

    probability = float(
        all_probabilities[
            application_node
        ]
    )

    prediction_rows.append({

        "application_id":
            row.application_id,

        "student_id":
            row.student_id,

        "company_id":
            row.company_id,

        "job_id":
            row.job_id,

        "recruitment_cycle":
            row.recruitment_cycle,

        "predicted_probability":
            probability,

        "predicted_status":
            int(
                probability >= 0.5
            ),

        "actual_status":
            int(
                row.final_status
            )
    })

prediction_df = pd.DataFrame(
    prediction_rows
)

prediction_df.to_csv(
    "AMRG_GraphSAGE_predictions.csv",
    index=False
)

comparison.to_csv(
    "GraphSAGE_model_comparison.csv",
    index=False
)

torch.save(
    proposed_model.state_dict(),
    "AMRG_GraphSAGE_model.pt"
)

torch.save(
    baseline_model.state_dict(),
    "Baseline_GraphSAGE_model.pt"
)

print(
    "Saved:"
)

print(
    "  AMRG_GraphSAGE_predictions.csv"
)

print(
    "  GraphSAGE_model_comparison.csv"
)

print(
    "  AMRG_GraphSAGE_model.pt"
)

print(
    "  Baseline_GraphSAGE_model.pt"
)


# ================================================================
# 36. FINAL SUMMARY
# ================================================================
print(
    "\n" + "=" * 72
)

print(
    "FINAL PIPELINE SUMMARY"
)

print(
    "=" * 72
)

print(
    "Dataset rows:",
    len(df)
)

print(
    "Dataset columns:",
    len(df.columns)
)

print(
    "Predictive inputs:",
    len(direct_features)
    +
    len(derived_features)
)

print(
    "Target:",
    target_column
)

print(
    "Null cells:",
    int(
        df.isna().sum().sum()
    )
)

print(
    "Duplicate rows:",
    int(
        df.duplicated().sum()
    )
)

print(
    "Graph nodes:",
    data.num_nodes
)

print(
    "Graph edges:",
    data.num_edges
)

print(
    "\nStandard GraphSAGE:"
)

for k, v in baseline_results.items():

    print(
        f"  {k:10s}: {v:.4f}"
    )

print(
    "\nAMRG-GraphSAGE:"
)

for k, v in proposed_results.items():

    print(
        f"  {k:10s}: {v:.4f}"
    )

print(
    "\nPipeline completed successfully."
)