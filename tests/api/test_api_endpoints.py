"""
Tests for Layer 9: API Endpoints, Validation, and Error Handling.
"""

from __future__ import annotations


def test_health_endpoint(test_client):
    res = test_client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_generate_strategy_endpoint(test_client, sample_analytics_result):
    payload = {
        "brand_id": "api_test_brand",
        "platform": "youtube",
        "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "objective": "Accelerate community growth",
        "analytics_result": sample_analytics_result.model_dump(),
    }
    res = test_client.post("/api/v1/strategy/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "strategy" in data
    assert data["strategy"]["brand_id"] == "api_test_brand"
    strat_id = data["strategy"]["strategy_id"]

    # Test retrieval
    get_res = test_client.get(f"/api/v1/strategy/{strat_id}")
    assert get_res.status_code == 200
    assert get_res.json()["strategy_id"] == strat_id

    # Test history
    hist_res = test_client.get("/api/v1/strategy/history?brand_id=api_test_brand")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1


def test_generate_strategy_with_real_dates(test_client):
    payload = {
        "brand_id": "api_dates_brand",
        "platform": "youtube",
        "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "objective": "Test real date parsing",
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2026-09-30T00:00:00Z",
    }
    res = test_client.post("/api/v1/strategy/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "strategy" in data
    assert data["strategy"]["brand_id"] == "api_dates_brand"


def test_generate_strategy_invalid_date_order(test_client):
    payload = {
        "brand_id": "api_dates_brand",
        "platform": "youtube",
        "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "start_date": "2026-09-30T00:00:00Z",
        "end_date": "2026-09-01T00:00:00Z",
    }
    res = test_client.post("/api/v1/strategy/generate", json=payload)
    assert res.status_code == 400
    data = res.json()
    assert "start_date cannot be after end_date" in data["detail"]


def test_strategy_outcome_endpoint(test_client, sample_analytics_result):
    # 1. Generate strategy first
    payload = {
        "brand_id": "api_outcome_brand",
        "platform": "youtube",
        "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "objective": "Test Outcome Loop",
        "analytics_result": sample_analytics_result.model_dump(),
    }
    gen_res = test_client.post("/api/v1/strategy/generate", json=payload)
    strat_id = gen_res.json()["strategy"]["strategy_id"]

    # 2. Record outcome with explicit analytics_result
    outcome_payload = {
        "strategy_id": strat_id,
        "analytics_result": sample_analytics_result.model_dump(),
    }
    out_res = test_client.post("/api/v1/strategy/outcome", json=outcome_payload)
    assert out_res.status_code == 201
    out_data = out_res.json()
    assert "outcome" in out_data
    assert out_data["hindsight_memory_id"] is not None


def test_strategy_outcome_auto_run_analytics(test_client, sample_analytics_result):
    # 1. Generate strategy first
    payload = {
        "brand_id": "api_auto_outcome_brand",
        "platform": "youtube",
        "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
        "objective": "Test Auto Outcome Loop",
        "analytics_result": sample_analytics_result.model_dump(),
    }
    gen_res = test_client.post("/api/v1/strategy/generate", json=payload)
    strat_id = gen_res.json()["strategy"]["strategy_id"]

    # 2. Record outcome omitting analytics_result
    outcome_payload = {
        "strategy_id": strat_id,
        "platform": "youtube",
        "account_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    }
    out_res = test_client.post("/api/v1/strategy/outcome", json=outcome_payload)
    assert out_res.status_code == 201
    out_data = out_res.json()
    assert "outcome" in out_data
    assert out_data["hindsight_memory_id"] is not None


def test_memory_inspection_endpoint(test_client):
    res = test_client.get("/api/v1/memory/test_bank?query=engagement")
    assert res.status_code == 200
    data = res.json()
    assert data["bank_id"] == "test_bank"
    assert "memories" in data


def test_not_found_strategy_error(test_client):
    res = test_client.get("/api/v1/strategy/non_existent_strat_id")
    assert res.status_code == 404
    data = res.json()
    assert data["error"] == "NotFoundError"


def test_invalid_payload_validation_error(test_client):
    # Missing required 'platform' field
    res = test_client.post("/api/v1/strategy/generate", json={"brand_id": "missing_platform"})
    assert res.status_code == 422
    data = res.json()
    assert data["error"] == "ValidationError"
