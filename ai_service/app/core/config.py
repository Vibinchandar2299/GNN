import os
from pathlib import Path
from pydantic import BaseModel

# Path configuration
AI_SERVICE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = AI_SERVICE_DIR.parent
CODEBASE_DIR = PROJECT_ROOT / "Codebase"
DATASET_DIR = PROJECT_ROOT / "Dataset"
ARTIFACTS_DIR = AI_SERVICE_DIR / "artifacts"

class Settings(BaseModel):
    # App Settings
    APP_NAME: str = "HireGraph AI - Inference Engine"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = ""
    HOST: str = os.getenv("HIREGRAPH_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("HIREGRAPH_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("HIREGRAPH_LOG_LEVEL", "INFO")

    # Model Settings
    MODEL_NAME: str = "AMRG-GraphSAGE"
    IN_CHANNELS: int = 82
    HIDDEN_CHANNELS: int = 128
    NUM_RELATIONS: int = 12
    NUM_LAYERS: int = 2
    DROPOUT: float = 0.20
    DEVICE: str = os.getenv("HIREGRAPH_DEVICE", "cpu")

    # Paths
    CHECKPOINT_PATH: Path = CODEBASE_DIR / "AMRG_GraphSAGE_model.pt"
    DATASET_PATH: Path = DATASET_DIR / "GNN_Placement_Dataset.xlsx"
    PREDICTIONS_CSV_PATH: Path = CODEBASE_DIR / "AMRG_GraphSAGE_predictions.csv"
    COMPARISON_CSV_PATH: Path = CODEBASE_DIR / "GraphSAGE_model_comparison.csv"
    ARTIFACTS_DIR_PATH: Path = ARTIFACTS_DIR

settings = Settings()
