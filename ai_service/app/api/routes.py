from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import List, Dict, Any
from ai_service.app.core.config import settings
from ai_service.app.core.logging import logger
from ai_service.app.services.inference_service import inference_service
from ai_service.app.services.graph_service import graph_service
from ai_service.app.api.schemas import (
    HealthResponse,
    ModelMetadataResponse,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    NeighborhoodResponse,
    ErrorResponse
)

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check and Engine Status",
    tags=["System"]
)
def get_health():
    """Returns the operational status and graph dimensions of the AI inference engine."""
    if not inference_service.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference Engine is initializing or unavailable."
        )

    return HealthResponse(
        status="UP",
        app_name=settings.APP_NAME,
        model_name=settings.MODEL_NAME,
        device=settings.DEVICE.upper(),
        graph_nodes=int(inference_service.graph_data.num_nodes),
        graph_edges=int(inference_service.graph_data.num_edges),
        relations_count=len(inference_service.relation_to_id),
        feature_dimension=int(inference_service.graph_data.num_node_features)
    )

@router.get(
    "/model/metadata",
    response_model=ModelMetadataResponse,
    summary="Verified Research Model Metadata",
    tags=["Model"]
)
def get_model_metadata():
    """Returns verified research results, paper details, and model specifications."""
    if not inference_service.is_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference Engine is initializing."
        )

    return ModelMetadataResponse(
        project_name="HireGraph AI",
        research_title="An Explainable AMRG-GraphSAGE Framework for Hiring Pattern Analysis under Evolving Job Requirements",
        model_name=settings.MODEL_NAME,
        checkpoint_file=settings.CHECKPOINT_PATH.name,
        device=settings.DEVICE.upper(),
        verified_research_results={
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
        graph_statistics={
            "total_nodes": int(inference_service.graph_data.num_nodes),
            "application_nodes": len(inference_service.node_maps.get("application", {})),
            "student_nodes": len(inference_service.node_maps.get("student", {})),
            "company_nodes": len(inference_service.node_maps.get("company", {})),
            "job_nodes": len(inference_service.node_maps.get("job", {})),
            "skill_nodes": len(inference_service.node_maps.get("skill", {})),
            "total_edges": int(inference_service.graph_data.num_edges),
            "relation_types_count": len(inference_service.relation_to_id),
            "feature_dimension": int(inference_service.graph_data.num_node_features)
        },
        temporal_split={
            "training_cycles": [2023, 2024],
            "validation_cycle": [2025],
            "test_cycle": [2026]
        },
        explainability={
            "gnnexplainer_active": False,
            "status_note": (
                "GNNExplainer encountered PyTorch Geometric edge-gradient compatibility limitations "
                "with RelationAwareWeightedSAGEConv. Preserved as an extensible component "
                "without synthetic explanation fabrication."
            )
        }
    )

@router.post(
    "/predict/application/{application_id}",
    response_model=PredictionResponse,
    summary="Run AMRG-GraphSAGE Inference for Application",
    responses={404: {"model": ErrorResponse}},
    tags=["Inference"]
)
def predict_application(
    application_id: str = Path(..., description="Application identifier (e.g. A00001, A00010)")
):
    """
    Executes AMRG-GraphSAGE forward inference for the requested application:
    - Resolves application ID to exact node index in PyG graph
    - Computes logit and sigmoid probability
    - Returns model-estimated outcome and estimated probability
    """
    try:
        result = inference_service.predict_application(application_id)
        return PredictionResponse(**result)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction failed for application {application_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )

@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Run Batch AMRG-GraphSAGE Inference",
    tags=["Inference"]
)
def predict_batch(request: BatchPredictionRequest):
    """
    Executes full-graph inference and retrieves predictions for a list of application IDs.
    """
    try:
        results = inference_service.predict_batch(request.application_ids)
        return BatchPredictionResponse(
            total_requested=len(request.application_ids),
            predictions=results
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference error: {str(e)}"
        )

@router.get(
    "/graph/neighborhood/{type}/{id}",
    response_model=NeighborhoodResponse,
    summary="Query 1-Hop Graph Neighborhood",
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    tags=["Graph"]
)
def get_graph_neighborhood(
    type: str = Path(..., description="Node entity type (application, student, company, job, skill)"),
    id: str = Path(..., description="Node entity identifier (e.g. S1654, C014, J0263, SK_13, A00001)"),
    max_neighbors: int = Query(50, ge=1, le=200, description="Maximum neighbors to return")
):
    """
    Retrieves the 1-hop connected neighborhood for a given node for graph visualizer rendering.
    """
    try:
        result = graph_service.get_node_neighborhood(type, id, max_neighbors)
        return NeighborhoodResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error querying graph neighborhood for {type}/{id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph query error: {str(e)}"
        )
