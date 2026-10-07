from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class BaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

class HealthResponse(BaseSchema):
    status: str = "UP"
    app_name: str
    model_name: str
    device: str
    graph_nodes: int
    graph_edges: int
    relations_count: int
    feature_dimension: int

class ResearchResultsMetrics(BaseSchema):
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

class ModelMetadataResponse(BaseSchema):
    project_name: str
    research_title: str
    model_name: str
    checkpoint_file: str
    device: str
    verified_research_results: Dict[str, ResearchResultsMetrics]
    graph_statistics: Dict[str, int]
    temporal_split: Dict[str, Any]
    explainability: Dict[str, Any]

class PredictionResponse(BaseSchema):
    application_id: str
    node_index: int
    model_name: str
    predicted_status: int = Field(description="0 for Rejected, 1 for Selected")
    predicted_outcome: str = Field(description="Selected or Rejected")
    predicted_probability: float = Field(description="Estimated probability from sigmoid output")
    decision_support_label: str = Field(description="Standardized research decision-support outcome label")
    disclaimer: str

class BatchPredictionRequest(BaseSchema):
    application_ids: List[str]

class BatchPredictionResponse(BaseSchema):
    total_requested: int
    predictions: List[Dict[str, Any]]

class GraphNodeDTO(BaseSchema):
    id: str
    node_index: int
    type: str
    is_center: bool

class GraphLinkDTO(BaseSchema):
    source: str
    source_type: str
    target: str
    target_type: str
    relation: str
    relation_id: int

class NeighborhoodResponse(BaseSchema):
    center_node: Dict[str, Any]
    nodes_count: int
    links_count: int
    nodes: List[GraphNodeDTO]
    links: List[GraphLinkDTO]

class ErrorResponse(BaseSchema):
    error: str
    detail: Optional[str] = None
