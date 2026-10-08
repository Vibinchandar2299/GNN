"""
Training and Evaluation Utilities for HireGraph AI Research Validation.
Exactly matches the loss, evaluation, and early-stopping protocol of Python.py.
"""

import copy
import random
from typing import Dict, Any, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


def set_seed(seed: int):
    """Sets deterministic random seed across random, numpy, and torch."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def ranking_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    margin: float = 0.20,
    max_pairs: int = 512
) -> torch.Tensor:
    """
    Pairwise ranking margin loss exactly matching Python.py.
    """
    positive_idx = torch.where(labels == 1)[0]
    negative_idx = torch.where(labels == 0)[0]

    if len(positive_idx) == 0 or len(negative_idx) == 0:
        return torch.tensor(0.0, device=logits.device)

    n = min(max_pairs, len(positive_idx), len(negative_idx))
    positive_selection = torch.randperm(len(positive_idx), device=logits.device)[:n]
    negative_selection = torch.randperm(len(negative_idx), device=logits.device)[:n]

    pos = logits[positive_idx[positive_selection]]
    neg = logits[negative_idx[negative_selection]]

    return F.relu(margin - pos + neg).mean()


def evaluate_model(
    model: nn.Module,
    graph: Any,
    mask: torch.Tensor
) -> Tuple[Dict[str, float], np.ndarray, np.ndarray, np.ndarray]:
    """
    Evaluates model on given mask, returning standard research metrics.
    """
    model.eval()
    with torch.no_grad():
        logits = model(graph.x, graph.edge_index, graph.edge_type)
        probabilities = torch.sigmoid(logits[mask]).cpu().numpy()
        true = graph.y[mask].cpu().numpy().astype(int)

    predictions = (probabilities >= 0.5).astype(int)

    # Calculate additional per-class precision/recall
    cm = confusion_matrix(true, predictions)
    # cm: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    
    rejected_prec = float(tn / (tn + fn)) if (tn + fn) > 0 else 0.0
    rejected_rec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    rejected_f1 = float(2 * rejected_prec * rejected_rec / (rejected_prec + rejected_rec)) if (rejected_prec + rejected_rec) > 0 else 0.0

    selected_prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    selected_rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    selected_f1 = float(2 * selected_prec * selected_rec / (selected_prec + selected_rec)) if (selected_prec + selected_rec) > 0 else 0.0

    results = {
        "Accuracy": float(accuracy_score(true, predictions)),
        "Precision": float(precision_score(true, predictions, zero_division=0)),
        "Recall": float(recall_score(true, predictions, zero_division=0)),
        "F1": float(f1_score(true, predictions, zero_division=0)),
        "ROC-AUC": float(roc_auc_score(true, probabilities)),
        "Selected_Precision": selected_prec,
        "Selected_Recall": selected_rec,
        "Selected_F1": selected_f1,
        "Rejected_Precision": rejected_prec,
        "Rejected_Recall": rejected_rec,
        "Rejected_F1": rejected_f1,
        "TP": int(tp),
        "FP": int(fp),
        "FN": int(fn),
        "TN": int(tn)
    }

    return results, true, predictions, probabilities


def train_model(
    model: nn.Module,
    graph: Any,
    epochs: int = 120,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    ranking_lambda: float = 0.0,
    patience: int = 15,
    pos_weight: float = 1.0,
    seed: int = 42,
    verbose: bool = True
) -> Tuple[nn.Module, Dict[str, list], float, int, int]:
    """
    Trains model with Adam, gradient clipping, weighted BCE, optional ranking loss,
    and patience-based early stopping on validation F1.
    """
    set_seed(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

    best_state = None
    best_val_f1 = -np.inf
    best_epoch = 0
    patience_counter = 0

    history = {
        "train_loss": [],
        "val_f1": [],
        "val_auc": []
    }

    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()

        logits = model(graph.x, graph.edge_index, graph.edge_type)
        train_logits = logits[graph.train_mask]
        train_labels = graph.y[graph.train_mask]

        bce_loss = F.binary_cross_entropy_with_logits(
            train_logits, train_labels, reduction='none'
        )
        if pos_weight is not None and pos_weight != 1.0:
            weight = torch.ones_like(train_labels)
            weight[train_labels == 1] = float(pos_weight)
            bce = (bce_loss * weight).mean()
        else:
            bce = bce_loss.mean()

        if ranking_lambda > 0:
            rank = ranking_loss(train_logits, train_labels)
        else:
            rank = torch.tensor(0.0, device=graph.x.device)

        loss = (1.0 - ranking_lambda) * bce + ranking_lambda * rank

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
        optimizer.step()

        # Validation
        model.eval()
        with torch.no_grad():
            validation_logits = model(graph.x, graph.edge_index, graph.edge_type)
            validation_prob = torch.sigmoid(validation_logits[graph.val_mask]).cpu().numpy()
            validation_true = graph.y[graph.val_mask].cpu().numpy().astype(int)
            validation_pred = (validation_prob >= 0.5).astype(int)

            validation_f1 = float(f1_score(validation_true, validation_pred, zero_division=0))
            validation_auc = float(roc_auc_score(validation_true, validation_prob))

        history["train_loss"].append(float(loss.item()))
        history["val_f1"].append(validation_f1)
        history["val_auc"].append(validation_auc)

        if validation_f1 > best_val_f1:
            best_val_f1 = validation_f1
            best_state = copy.deepcopy(model.state_dict())
            best_epoch = epoch
            patience_counter = 0
        else:
            patience_counter += 1

        if verbose and (epoch == 1 or epoch % 20 == 0):
            print(f"Epoch {epoch:03d} | Loss={loss.item():.4f} | Val F1={validation_f1:.4f} | Val AUC={validation_auc:.4f}")

        if patience_counter >= patience:
            if verbose:
                print(f"Early stopping at epoch {epoch} (best epoch was {best_epoch} with Val F1={best_val_f1:.4f})")
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    total_epochs = epoch
    return model, history, best_val_f1, best_epoch, total_epochs
