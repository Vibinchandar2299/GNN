from typing import Dict, Any, List, Optional
import torch
import numpy as np
import pandas as pd
from ai_service.app.core.config import settings
from ai_service.app.core.logging import logger
from ai_service.app.model.amrg_model import AMRGGraphSAGE
from ai_service.app.pipeline.preprocessor import Preprocessor
from ai_service.app.pipeline.graph_builder import build_graph

class InferenceService:
    """
    Singleton inference service that loads the graph and AMRG-GraphSAGE model ONCE during startup.
    Executes in-memory forward inference producing model-estimated outcomes and probabilities.
    """
    def __init__(self):
        self.model: Optional[AMRGGraphSAGE] = None
        self.graph_data = None
        self.node_maps: Dict[str, Dict[str, int]] = {}
        self.relation_to_id: Dict[str, int] = {}
        self.id_to_relation: Dict[int, str] = {}
        self.preprocessor: Optional[Preprocessor] = None
        self.is_initialized: bool = False
        self.device = torch.device(settings.DEVICE)

        # Inverted index: node_id -> (node_type, entity_id)
        self.node_id_to_entity: Dict[int, tuple] = {}

    def initialize(self):
        """Loads dataset, builds graph, and loads frozen model weights."""
        if self.is_initialized:
            logger.info("InferenceService already initialized.")
            return

        logger.info("=" * 60)
        logger.info("Initializing HireGraph AI - AMRG-GraphSAGE Inference Engine")
        logger.info("=" * 60)

        # 1. Initialize preprocessor & check for artifacts
        self.preprocessor = Preprocessor()
        scaler_file = settings.ARTIFACTS_DIR_PATH / "scaler.joblib"
        encoder_file = settings.ARTIFACTS_DIR_PATH / "encoder.joblib"

        xls = pd.ExcelFile(settings.DATASET_PATH)
        df = pd.read_excel(xls, sheet_name="unified_dataset")
        edges_df = pd.read_excel(xls, sheet_name="graph_edges") if "graph_edges" in xls.sheet_names else None

        if scaler_file.exists() and encoder_file.exists():
            logger.info("Loading preprocessors from artifacts...")
            self.preprocessor.load_artifacts(settings.ARTIFACTS_DIR_PATH)
        else:
            logger.info("Artifacts not found, fitting preprocessors on training cycles (2023-2024)...")
            cleaned_df = self.preprocessor.clean_dataset(df)
            self.preprocessor.fit_on_training_cycles(cleaned_df, train_cycles=[2023, 2024])
            self.preprocessor.save_artifacts(settings.ARTIFACTS_DIR_PATH)

        # 2. Build graph matching original research pipeline
        logger.info("Building PyTorch Geometric graph structure...")
        (
            self.graph_data,
            self.node_maps,
            self.relation_to_id,
            self.id_to_relation
        ) = build_graph(df, edges_df, self.preprocessor)

        self.graph_data = self.graph_data.to(self.device)

        # Build reverse index for fast entity lookups
        for ntype, mapping in self.node_maps.items():
            for entity_id, nid in mapping.items():
                self.node_id_to_entity[nid] = (ntype, entity_id)

        # 3. Load Model
        logger.info(f"Loading model checkpoint from {settings.CHECKPOINT_PATH}...")
        self.model = AMRGGraphSAGE(
            in_channels=settings.IN_CHANNELS,
            hidden_channels=settings.HIDDEN_CHANNELS,
            num_relations=settings.NUM_RELATIONS,
            num_layers=settings.NUM_LAYERS,
            dropout=settings.DROPOUT
        )

        state_dict = torch.load(
            settings.CHECKPOINT_PATH,
            map_location=self.device
        )
        self.model.load_state_dict(state_dict)
        self.model.to(self.device)
        self.model.eval()

        self.is_initialized = True

        logger.info("=" * 60)
        logger.info("AMRG-GraphSAGE AI Engine Loaded Successfully")
        logger.info(f"Model: {settings.MODEL_NAME}")
        logger.info(f"Device: {settings.DEVICE.upper()}")
        logger.info(f"Graph nodes: {self.graph_data.num_nodes}")
        logger.info(f"Graph edges: {self.graph_data.num_edges}")
        logger.info(f"Relations: {len(self.relation_to_id)}")
        logger.info(f"Features: {self.graph_data.num_node_features}")
        logger.info(f"Checkpoint: {settings.CHECKPOINT_PATH.name}")
        logger.info("=" * 60)

    def predict_application(self, application_id: str) -> Dict[str, Any]:
        """
        Executes inference for a specific application ID:
        - Maps application_id to node index
        - Evaluates forward pass
        - Returns predicted outcome, probability, and decision-support metadata.
        """
        if not self.is_initialized:
            raise RuntimeError("InferenceService is not initialized.")

        app_id_clean = str(application_id).strip()
        app_map = self.node_maps.get("application", {})

        if app_id_clean not in app_map:
            raise KeyError(f"Application ID '{app_id_clean}' not found in graph.")

        node_idx = app_map[app_id_clean]

        self.model.eval()
        with torch.no_grad():
            logits = self.model(
                self.graph_data.x,
                self.graph_data.edge_index,
                self.graph_data.edge_type
            )
            prob = float(torch.sigmoid(logits[node_idx]).item())

        predicted_status = 1 if prob >= 0.5 else 0
        outcome_label = "Selected" if predicted_status == 1 else "Rejected"

        return {
            "application_id": app_id_clean,
            "node_index": node_idx,
            "model_name": settings.MODEL_NAME,
            "predicted_status": predicted_status,
            "predicted_outcome": outcome_label,
            "predicted_probability": prob,
            "decision_support_label": f"Model-estimated outcome: {outcome_label}",
            "disclaimer": (
                "Model-estimated outcome based on AMRG-GraphSAGE pre-interview graph analysis. "
                "This is a research decision-support estimate, not an autonomous hiring decision."
            )
        }

    def predict_batch(self, application_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Executes full-graph inference and retrieves predictions for a batch of application IDs.
        """
        if not self.is_initialized:
            raise RuntimeError("InferenceService is not initialized.")

        self.model.eval()
        with torch.no_grad():
            logits = self.model(
                self.graph_data.x,
                self.graph_data.edge_index,
                self.graph_data.edge_type
            )
            probs = torch.sigmoid(logits).cpu().numpy()

        results = []
        app_map = self.node_maps.get("application", {})

        for app_id in application_ids:
            app_id_clean = str(app_id).strip()
            if app_id_clean not in app_map:
                results.append({
                    "application_id": app_id_clean,
                    "error": f"Application ID '{app_id_clean}' not found."
                })
                continue

            node_idx = app_map[app_id_clean]
            prob = float(probs[node_idx])
            predicted_status = 1 if prob >= 0.5 else 0
            outcome_label = "Selected" if predicted_status == 1 else "Rejected"

            results.append({
                "application_id": app_id_clean,
                "node_index": node_idx,
                "model_name": settings.MODEL_NAME,
                "predicted_status": predicted_status,
                "predicted_outcome": outcome_label,
                "predicted_probability": prob,
                "decision_support_label": f"Model-estimated outcome: {outcome_label}"
            })

        return results

    def get_all_application_predictions(self) -> Dict[str, float]:
        """
        Executes inference for all 4,000 applications.
        Returns a dict mapping application_id -> predicted_probability.
        """
        if not self.is_initialized:
            raise RuntimeError("InferenceService is not initialized.")

        self.model.eval()
        with torch.no_grad():
            logits = self.model(
                self.graph_data.x,
                self.graph_data.edge_index,
                self.graph_data.edge_type
            )
            probs = torch.sigmoid(logits).cpu().numpy()

        app_map = self.node_maps.get("application", {})
        return {
            app_id: float(probs[idx])
            for app_id, idx in app_map.items()
        }

# Global singleton instance
inference_service = InferenceService()
