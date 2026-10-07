import torch
import torch.nn as nn
from torch_geometric.utils import softmax as pyg_softmax

class RelationAwareWeightedSAGEConv(nn.Module):
    """
    Optimized Relation-Aware Weighted GraphSAGE Convolution layer
    with adaptive relation-aware neighbor scoring and feature-confidence gating.
    Extracted directly from research codebase Python.py.
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        num_relations: int,
        relation_dim: int = 16
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
                in_channels * 2 + relation_dim,
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
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor
    ) -> torch.Tensor:
        src = edge_index[0]
        dst = edge_index[1]

        x_src = x[src]
        x_dst = x[dst]

        relation_vector = self.relation_embedding(edge_type)

        score_input = torch.cat(
            [
                x_dst,
                x_src,
                relation_vector
            ],
            dim=-1
        )

        scores = self.score_mlp(score_input).squeeze(-1)

        # Vectorized graph-wise softmax across incoming edges per destination
        alpha = pyg_softmax(scores, dst)

        transformed_neighbors = self.neighbor_linear(x_src)

        messages = transformed_neighbors * alpha.unsqueeze(-1)

        aggregated = torch.zeros(
            x.size(0),
            messages.size(1),
            device=x.device,
            dtype=x.dtype
        )

        aggregated.index_add_(0, dst, messages)

        self_representation = self.self_linear(x)

        gate_input = torch.cat(
            [
                self_representation,
                aggregated
            ],
            dim=-1
        )

        gate = torch.sigmoid(self.gate(gate_input))

        output = (
            gate * self_representation
            + (1.0 - gate) * aggregated
        )

        return output
