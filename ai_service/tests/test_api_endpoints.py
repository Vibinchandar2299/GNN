import pytest
from fastapi.testclient import TestClient
from ai_service.app.main import app
from ai_service.app.services.inference_service import inference_service

@pytest.fixture(scope="module")
def client():
    """Create a TestClient with lifespan context executed."""
    with TestClient(app) as test_client:
        yield test_client

def test_health_endpoint(client):
    """Verifies GET /health returns operational status and graph dimensions."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["model_name"] == "AMRG-GraphSAGE"
    assert data["device"] == "CPU"
    assert data["graph_nodes"] == 5977
    assert data["graph_edges"] == 43044
    assert data["relations_count"] == 12
    assert data["feature_dimension"] == 82

def test_model_metadata_endpoint(client):
    """Verifies GET /model/metadata returns paper info and verified results."""
    response = client.get("/model/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "AMRG-GraphSAGE"
    assert "AMRG_GraphSAGE" in data["verified_research_results"]
    assert "Standard_GraphSAGE" in data["verified_research_results"]
    assert data["graph_statistics"]["total_nodes"] == 5977
    assert data["graph_statistics"]["total_edges"] == 43044
    assert data["explainability"]["gnnexplainer_active"] is False

def test_predict_application_endpoint_success(client):
    """Verifies POST /predict/application/{id} returns correct prediction for valid application."""
    # Test Application A00001
    response = client.post("/predict/application/A00001")
    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == "A00001"
    assert data["model_name"] == "AMRG-GraphSAGE"
    assert data["predicted_status"] == 1
    assert data["predicted_outcome"] == "Selected"
    assert abs(data["predicted_probability"] - 0.8063023686408997) < 1e-6
    assert "Model-estimated outcome: Selected" in data["decision_support_label"]
    assert "research decision-support estimate" in data["disclaimer"]

    # Test Application A00002
    response2 = client.post("/predict/application/A00002")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["application_id"] == "A00002"
    assert data2["predicted_status"] == 0
    assert data2["predicted_outcome"] == "Rejected"
    assert abs(data2["predicted_probability"] - 0.13230180740356445) < 1e-6

def test_predict_application_not_found(client):
    """Verifies POST /predict/application/{id} returns HTTP 404 for invalid ID."""
    response = client.post("/predict/application/INVALID_ID_99999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_predict_batch_endpoint(client):
    """Verifies POST /predict/batch returns multiple predictions."""
    payload = {
        "application_ids": ["A00001", "A00002", "A00010", "INVALID_APP"]
    }
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_requested"] == 4
    preds = data["predictions"]
    assert len(preds) == 4

    # A00001
    assert preds[0]["application_id"] == "A00001"
    assert preds[0]["predicted_status"] == 1

    # A00002
    assert preds[1]["application_id"] == "A00002"
    assert preds[1]["predicted_status"] == 0

    # A00010
    assert preds[2]["application_id"] == "A00010"
    assert preds[2]["predicted_status"] == 1
    assert abs(preds[2]["predicted_probability"] - 0.9148515462875366) < 1e-6

    # INVALID_APP
    assert preds[3]["application_id"] == "INVALID_APP"
    assert "error" in preds[3]

def test_graph_neighborhood_endpoint_success(client):
    """Verifies GET /graph/neighborhood/{type}/{id} returns connected subgraphs."""
    # Query student S1654
    response = client.get("/graph/neighborhood/student/S1654")
    assert response.status_code == 200
    data = response.json()
    assert data["center_node"]["id"] == "S1654"
    assert data["center_node"]["type"] == "student"
    assert data["nodes_count"] > 1
    assert data["links_count"] > 0
    assert any(n["is_center"] for n in data["nodes"])

def test_graph_neighborhood_invalid_type(client):
    """Verifies GET /graph/neighborhood with invalid type returns 400 Bad Request."""
    response = client.get("/graph/neighborhood/invalid_entity_type/S1654")
    assert response.status_code == 400

def test_graph_neighborhood_not_found(client):
    """Verifies GET /graph/neighborhood with missing entity returns 404 Not Found."""
    response = client.get("/graph/neighborhood/student/NON_EXISTENT_STUDENT")
    assert response.status_code == 404
