"""
Tests for Reasoning Engine
"""
import pytest
import asyncio
import pytest_asyncio
from services.reasoning_engine import ReasoningEngine
from services.rag_service import RAGService
from services.llm_service import LLMService
from api.models import DeviceInfo


@pytest_asyncio.fixture
async def services():
    """Fixture for services"""
    rag = RAGService()
    await rag.initialize()
    llm = LLMService()
    engine = ReasoningEngine(rag, llm)
    
    yield engine, rag
    
    await rag.close()


@pytest.mark.asyncio
async def test_diagnose_simple_problem(services):
    """Test diagnosing a simple problem"""
    engine, _ = services
    
    result = await engine.diagnose_and_solve(
        user_problem="My Wi-Fi won't connect",
        conversation_history=[],
        device_info=DeviceInfo(device_type="laptop", os="windows"),
        technical_level="beginner"
    )
    
    assert 'response' in result
    assert 'problem_understanding' in result
    assert 'likely_causes' in result
    assert 'solution_steps' in result
    assert isinstance(result['likely_causes'], list)
    assert isinstance(result['solution_steps'], list)


@pytest.mark.asyncio
async def test_analyze_problem(services):
    """Test problem analysis"""
    engine, _ = services
    
    result = await engine.analyze_problem(
        problem_description="Computer is very slow",
        device_info=DeviceInfo(device_type="desktop", os="windows")
    )
    
    assert 'problem_category' in result
    assert 'severity' in result
    assert 'likely_causes' in result
    assert 'estimated_complexity' in result


@pytest.mark.asyncio
async def test_rephrase_query(services):
    """Test query rephrasing"""
    engine, _ = services

    # Test Wi-Fi issue
    result = await engine._rephrase_query(
        "wifi doesn't work",
        DeviceInfo(device_type="laptop")
    )
    assert "wi-fi" in result.lower() or "wifi" in result.lower()


@pytest.mark.asyncio
async def test_categorize_problem(services):
    """Test problem categorization"""
    engine, _ = services

    category = engine._categorize_problem("My printer won't print", [])
    assert category == "peripherals"

    category = engine._categorize_problem("Computer freezes", [])
    assert category == "performance"
