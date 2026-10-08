"""
Neural Network Architectures for HireGraph AI Research Validation & Ablation Study.

Contains:
1. BaselineGraphSAGE: Standard uniform GraphSAGE baseline (hidden=64, 2 layers, dropout=0.30).
2. AMRGGraphSAGE: Full proposed architecture with all 6 novel mechanisms enabled.
3. AMRGNoRelationGraphSAGE (Variant C): Ablation with relation-awareness disabled.
4. AMRGNoAdaptiveWeightingGraphSAGE (Variant D): Ablation with uniform neighbor weighting (no attention).
5. AMRGNoGatingGraphSAGE (Variant E): Ablation with ungated additive combination (no confidence gate).
6. AMRGNoMultiScaleGraphSAGE (Variant F): Ablation with single-scale representation (final layer only).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch_geometric.utils import softmax as pyg_softmax


# ====================================================================
# VARIANT A: STANDARD GRAPHSAGE BASELINE
# ====================================================================
class BaselineGraphSAGE(nn.Module):
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 64,
        num_layers: int = 2,
        dropout: float = 0.30
    ):
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


# ====================================================================
# RELATION-AWARE WEIGHTED SAGE CONV (CORE AMRG LAYER)
# ====================================================================
class RelationAwareWeightedSAGEConv(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        num_relations: int,
        relation_dim: int = 16,
        disable_relation: bool = False,
        disable_adaptive_weighting: bool = False,
        disable_gating: bool = False
    ):
        super().__init__()
        self.disable_relation = disable_relation
        self.disable_adaptive_weighting = disable_adaptive_weighting
        self.disable_gating = disable_gating

        self.self_linear = nn.Linear(in_channels, out_channels)
        self.neighbor_linear = nn.Linear(in_channels, out_channels)
        self.relation_embedding = nn.Embedding(num_relations, relation_dim)

        self.score_mlp = nn.Sequential(
            nn.Linear(in_channels * 2 + relation_dim, out_channels),
            nn.ReLU(),
            nn.Linear(out_channels, 1)
        )

        if not self.disable_gating:
            self.gate = nn.Linear(out_channels * 2, out_channels)
        else:
            self.gate = None

    def forward(self, x, edge_index, edge_type):
        src = edge_index[0]
        dst = edge_index[1]

        x_src = x[src]
        x_dst = x[dst]

        # 1. Relation embedding (ablated if disable_relation=True)
        if self.disable_relation:
            relation_vector = torch.zeros(
                edge_type.size(0),
                self.relation_embedding.embedding_dim,
                device=x.device,
                dtype=x.dtype
            )
        else:
            relation_vector = self.relation_embedding(edge_type)

        # 2. Neighbor weighting
        transformed_neighbors = self.neighbor_linear(x_src)

        if self.disable_adaptive_weighting:
            # Uniform mean neighbor aggregation: 1 / degree(dst)
            ones = torch.ones(edge_index.size(1), device=x.device, dtype=x.dtype)
            deg = torch.zeros(x.size(0), device=x.device, dtype=x.dtype)
            deg.index_add_(0, dst, ones)
            deg = deg.clamp(min=1.0)
            alpha = 1.0 / deg[dst]
        else:
            score_input = torch.cat([x_dst, x_src, relation_vector], dim=-1)
            scores = self.score_mlp(score_input).squeeze(-1)
            alpha = pyg_softmax(scores, dst)

        messages = transformed_neighbors * alpha.unsqueeze(-1)

        aggregated = torch.zeros(x.size(0), messages.size(1), device=x.device, dtype=x.dtype)
        aggregated.index_add_(0, dst, messages)

        self_representation = self.self_linear(x)

        # 3. Combination: Gated vs Ungated
        if self.disable_gating:
            # Standard additive combination h_self + h_neigh
            output = self_representation + aggregated
        else:
            gate_input = torch.cat([self_representation, aggregated], dim=-1)
            gate = torch.sigmoid(self.gate(gate_input))
            output = gate * self_representation + (1.0 - gate) * aggregated

        return output


# ====================================================================
# VARIANT B: FULL AMRG-GRAPHSAGE (PROPOSED MODEL)
# ====================================================================
class AMRGGraphSAGE(nn.Module):
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 128,
        num_relations: int = 12,
        num_layers: int = 2,
        dropout: float = 0.20,
        disable_relation: bool = False,
        disable_adaptive_weighting: bool = False,
        disable_gating: bool = False,
        disable_multiscale: bool = False
    ):
        super().__init__()
        self.disable_multiscale = disable_multiscale
        self.layers = nn.ModuleList()
        self.norms = nn.ModuleList()

        self.layers.append(
            RelationAwareWeightedSAGEConv(
                in_channels,
                hidden_channels,
                num_relations,
                disable_relation=disable_relation,
                disable_adaptive_weighting=disable_adaptive_weighting,
                disable_gating=disable_gating
            )
        )
        self.norms.append(nn.LayerNorm(hidden_channels))

        for _ in range(num_layers - 1):
            self.layers.append(
                RelationAwareWeightedSAGEConv(
                    hidden_channels,
                    hidden_channels,
                    num_relations,
                    disable_relation=disable_relation,
                    disable_adaptive_weighting=disable_adaptive_weighting,
                    disable_gating=disable_gating
                )
            )
            self.norms.append(nn.LayerNorm(hidden_channels))

        if not self.disable_multiscale:
            self.scale_score = nn.Linear(hidden_channels, 1)
        else:
            self.scale_score = None

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

        if self.disable_multiscale:
            # Pass final layer output directly to classifier
            z = layer_outputs[-1]
        else:
            # Adaptive multi-scale fusion
            H = torch.stack(layer_outputs, dim=1)
            scale_logits = self.scale_score(H).squeeze(-1)
            beta = torch.softmax(scale_logits, dim=1)
            z = torch.sum(H * beta.unsqueeze(-1), dim=1)

        return self.classifier(z).squeeze(-1)


# ====================================================================
# SPECIFIC ABLATION VARIANT CONVENIENCE CLASSES
# ====================================================================
class AMRGNoRelationGraphSAGE(AMRGGraphSAGE):
    """Variant C: Relation embeddings disabled (zeroed)."""
    def __init__(self, in_channels: int, hidden_channels: int = 128, num_relations: int = 12, **kwargs):
        super().__init__(
            in_channels,
            hidden_channels=hidden_channels,
            num_relations=num_relations,
            disable_relation=True,
            **kwargs
        )


class AMRGNoAdaptiveWeightingGraphSAGE(AMRGGraphSAGE):
    """Variant D: Softmax attention weighting replaced by uniform 1/deg(dst) aggregation."""
    def __init__(self, in_channels: int, hidden_channels: int = 128, num_relations: int = 12, **kwargs):
        super().__init__(
            in_channels,
            hidden_channels=hidden_channels,
            num_relations=num_relations,
            disable_adaptive_weighting=True,
            **kwargs
        )


class AMRGNoGatingGraphSAGE(AMRGGraphSAGE):
    """Variant E: Feature-confidence gating replaced by standard addition h_self + h_neigh."""
    def __init__(self, in_channels: int, hidden_channels: int = 128, num_relations: int = 12, **kwargs):
        super().__init__(
            in_channels,
            hidden_channels=hidden_channels,
            num_relations=num_relations,
            disable_gating=True,
            **kwargs
        )


class AMRGNoMultiScaleGraphSAGE(AMRGGraphSAGE):
    """Variant F: Multi-scale fusion disabled; final layer output fed directly to classifier."""
    def __init__(self, in_channels: int, hidden_channels: int = 128, num_relations: int = 12, **kwargs):
        super().__init__(
            in_channels,
            hidden_channels=hidden_channels,
            num_relations=num_relations,
            disable_multiscale=True,
            **kwargs
        )
