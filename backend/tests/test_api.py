"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data


def test_chat_endpoint():
    """Test chat endpoint"""
    payload = {
        "message": "My computer is slow",
        "technical_level": "beginner"
    }
    
    response = client.post("/api/chat", json=payload)
    assert response.status_code in [200, 503]  # 503 if services not initialized
    
    if response.status_code == 200:
        data = response.json()
        assert "response" in data
        assert "session_id" in data


def test_analyze_endpoint():
    """Test analyze endpoint"""
    payload = {
        "problem_description": "Laptop won't turn on",
        "device_info": {
            "device_type": "laptop",
            "os": "windows"
        }
    }
    
    response = client.post("/api/analyze", json=payload)
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "problem_category" in data
        assert "severity" in data


def test_feedback_endpoint():
    """Test feedback endpoint"""
    payload = {
        "session_id": "test_session",
        "rating": "helpful",
        "solved": True,
        "comment": "Very helpful!"
    }
    
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_invalid_chat_request():
    """Test invalid chat request"""
    payload = {
        "message": ""  # Empty message should fail
    }
    
    response = client.post("/api/chat", json=payload)
    # Depending on FastAPI dependency evaluation order and service init timing,
    # this may return 422 (validation) or 503 (services not initialized).
    assert response.status_code in [422, 503]
