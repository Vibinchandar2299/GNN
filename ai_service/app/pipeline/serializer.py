import json
from pathlib import Path
import pandas as pd
from ai_service.app.core.config import settings
from ai_service.app.core.logging import logger
from ai_service.app.pipeline.preprocessor import Preprocessor
from ai_service.app.pipeline.graph_builder import build_graph

def export_artifacts(output_dir: Path = settings.ARTIFACTS_DIR_PATH):
    """
    Executes the research data processing pipeline and serializes:
    - scaler.joblib
    - encoder.joblib
    - node_maps.json
    - relation_maps.json
    - metadata.json
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Exporting artifacts to {output_dir}...")

    # 1. Load Excel sheets
    logger.info(f"Reading dataset from {settings.DATASET_PATH}...")
    xls = pd.ExcelFile(settings.DATASET_PATH)
    df = pd.read_excel(xls, sheet_name="unified_dataset")
    edges_df = pd.read_excel(xls, sheet_name="graph_edges") if "graph_edges" in xls.sheet_names else None

    # 2. Fit preprocessor strictly on training cycles
    preprocessor = Preprocessor()
    cleaned_df = preprocessor.clean_dataset(df)
    preprocessor.fit_on_training_cycles(cleaned_df, train_cycles=[2023, 2024])
    preprocessor.save_artifacts(output_dir)

    # 3. Build graph & extract mappings
    data, node_maps, relation_to_id, id_to_relation = build_graph(cleaned_df, edges_df, preprocessor)

    # 4. Save node_maps.json
    with open(output_dir / "node_maps.json", "w", encoding="utf-8") as f:
        json.dump(node_maps, f, indent=2)
    logger.info("Saved node_maps.json")

    # 5. Save relation_maps.json
    relation_maps = {
        "relation_to_id": relation_to_id,
        "id_to_relation": id_to_relation
    }
    with open(output_dir / "relation_maps.json", "w", encoding="utf-8") as f:
        json.dump(relation_maps, f, indent=2)
    logger.info("Saved relation_maps.json")

    # 6. Save metadata.json
    metadata = {
        "project_name": "HireGraph AI",
        "research_title": "An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements",
        "model_name": settings.MODEL_NAME,
        "model_checkpoint": str(settings.CHECKPOINT_PATH.name),
        "device": settings.DEVICE,
        "verified_research_results": {
            "Standard_GraphSAGE": {
                "accuracy": 0.8387,
                "precision": 0.8443,
                "recall": 0.8699,
                "f1": 0.8569,
                "roc_auc": 0.9140
            },
            "AMRG_GraphSAGE": {
                "accuracy": 0.8427,
                "precision": 0.8493,
                "recall": 0.8714,
                "f1": 0.8602,
                "roc_auc": 0.9142
            }
        },
        "graph_statistics": {
            "total_nodes": int(data.num_nodes),
            "application_nodes": len(node_maps["application"]),
            "student_nodes": len(node_maps["student"]),
            "company_nodes": len(node_maps["company"]),
            "job_nodes": len(node_maps["job"]),
            "skill_nodes": len(node_maps["skill"]),
            "total_edges": int(data.num_edges),
            "relation_types_count": len(relation_to_id),
            "feature_dimension": int(data.num_node_features)
        },
        "temporal_split": {
            "training_cycles": [2023, 2024],
            "validation_cycle": [2025],
            "test_cycle": [2026]
        },
        "explainability": {
            "gnnexplainer_active": False,
            "status_note": (
                "GNNExplainer encountered PyTorch Geometric edge-gradient compatibility limitations "
                "with custom RelationAwareWeightedSAGEConv. Preserved as an extensible component "
                "without synthetic explanation fabrication."
            )
        }
    }
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata.json")

    logger.info("Artifact generation completed successfully.")

if __name__ == "__main__":
    export_artifacts()
