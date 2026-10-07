from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib
from pathlib import Path
from ai_service.app.core.config import settings
from ai_service.app.core.logging import logger

ID_COLUMNS: List[str] = [
    "application_id",
    "student_id",
    "company_id",
    "job_id",
]

TEMPORAL_COLUMN: str = "recruitment_cycle"
TARGET_COLUMN: str = "final_status"

NUMERIC_FEATURES: List[str] = [
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
    "role_experience_match",
]

CATEGORICAL_FEATURES: List[str] = [
    "department",
    "industry",
    "company_size",
    "job_title",
    "job_domain",
]

NODE_TYPE_NAMES: List[str] = [
    "application",
    "student",
    "company",
    "job",
    "skill",
]

class Preprocessor:
    """
    Exact data cleaning, feature scaling and categorical encoding pipeline
    matching Python.py from the research codebase.
    """
    def __init__(self):
        self.scaler: StandardScaler = StandardScaler()
        self.encoder: OneHotEncoder = OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )
        self.is_fitted: bool = False

    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply the exact data cleaning rules from Python.py Section 7."""
        cleaned_df = df.copy()

        # Remove duplicate rows
        if cleaned_df.duplicated().sum() > 0:
            cleaned_df = cleaned_df.drop_duplicates().copy()

        # Remove duplicate application IDs
        if cleaned_df["application_id"].duplicated().sum() > 0:
            cleaned_df = cleaned_df.drop_duplicates(
                subset=["application_id"],
                keep="first"
            ).copy()

        # Drop rows with nulls if any
        if cleaned_df.isna().sum().sum() > 0:
            cleaned_df = cleaned_df.dropna().reset_index(drop=True)

        return cleaned_df

    def fit_on_training_cycles(self, df: pd.DataFrame, train_cycles: List[int] = [2023, 2024]):
        """
        Fits StandardScaler and OneHotEncoder STRICTLY on training recruitment cycles (2023 + 2024).
        Never fit on val (2025) or test (2026) cycles to preserve research pipeline guarantees.
        """
        train_df = df[df[TEMPORAL_COLUMN].isin(train_cycles)].copy()
        logger.info(f"Fitting preprocessors on {len(train_df)} training rows (cycles {train_cycles})...")

        self.scaler.fit(train_df[NUMERIC_FEATURES])
        self.encoder.fit(train_df[CATEGORICAL_FEATURES])
        self.is_fitted = True

        cat_feature_dim = len(self.encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        logger.info(f"Scaler fitted for {len(NUMERIC_FEATURES)} numeric features.")
        logger.info(f"OneHotEncoder fitted for {len(CATEGORICAL_FEATURES)} categorical features -> {cat_feature_dim} dimensions.")
        logger.info(f"Total base feature dimension: {len(NUMERIC_FEATURES) + cat_feature_dim}")

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms a dataframe into normalized and encoded application feature matrix."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted or loaded before transform.")

        X_num = self.scaler.transform(df[NUMERIC_FEATURES])
        X_cat = self.encoder.transform(df[CATEGORICAL_FEATURES])
        X_app = np.hstack([X_num, X_cat]).astype(np.float32)
        return X_app

    def save_artifacts(self, artifacts_dir: Path):
        """Save fitted scaler and encoder as joblib files."""
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.scaler, artifacts_dir / "scaler.joblib")
        joblib.dump(self.encoder, artifacts_dir / "encoder.joblib")
        logger.info(f"Saved scaler.joblib and encoder.joblib to {artifacts_dir}")

    def load_artifacts(self, artifacts_dir: Path):
        """Load fitted scaler and encoder from joblib files."""
        scaler_path = artifacts_dir / "scaler.joblib"
        encoder_path = artifacts_dir / "encoder.joblib"

        if not scaler_path.exists() or not encoder_path.exists():
            raise FileNotFoundError(f"Artifacts not found in {artifacts_dir}")

        self.scaler = joblib.load(scaler_path)
        self.encoder = joblib.load(encoder_path)
        self.is_fitted = True
        logger.info(f"Loaded scaler.joblib and encoder.joblib from {artifacts_dir}")
