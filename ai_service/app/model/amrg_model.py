import torch
import torch.nn as nn
import torch.nn.functional as F
from ai_service.app.model.layers import RelationAwareWeightedSAGEConv

class AMRGGraphSAGE(nn.Module):
    """
    Adaptive Multi-Scale Relation-Gated GraphSAGE (AMRG-GraphSAGE).
    Extracted directly from research codebase Python.py.
    """
    def __init__(
        self,
        in_channels: int,
        hidden_channels: int = 128,
        num_relations: int = 12,
        num_layers: int = 2,
        dropout: float = 0.20
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

        for _ in range(num_layers - 1):
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
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor
    ) -> torch.Tensor:
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
        H = torch.stack(layer_outputs, dim=1)

        scale_logits = self.scale_score(H).squeeze(-1)
        beta = torch.softmax(scale_logits, dim=1)

        # Adaptive multi-scale fusion
        z = torch.sum(H * beta.unsqueeze(-1), dim=1)

        return self.classifier(z).squeeze(-1)
