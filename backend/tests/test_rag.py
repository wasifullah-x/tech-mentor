"""
Tests for RAG Service
"""
import pytest
import asyncio
import pytest_asyncio
from services.rag_service import RAGService


@pytest_asyncio.fixture
async def rag_service():
    """Fixture for RAG service"""
    service = RAGService()
    await service.initialize()
    yield service
    await service.close()


@pytest.mark.asyncio
async def test_rag_initialization(rag_service):
    """Test RAG service initialization"""
    assert rag_service.initialized is True
    assert rag_service.collection is not None
    assert rag_service.embedding_model is not None


@pytest.mark.asyncio
async def test_retrieve_solutions(rag_service):
    """Test solution retrieval"""
    query = "Wi-Fi not working"
    results = await rag_service.retrieve_solutions(query, top_k=3)
    
    assert isinstance(results, list)
    assert len(results) <= 3
    
    if results:
        result = results[0]
        assert 'id' in result
        assert 'similarity' in result
        assert 'problem' in result


@pytest.mark.asyncio
async def test_retrieve_with_filter(rag_service):
    """Test retrieval with device type filter"""
    query = "slow computer"
    results = await rag_service.retrieve_solutions(
        query,
        top_k=5,
        filter_dict={"device_type": "laptop"}
    )
    
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_add_document(rag_service):
    """Test adding a new document"""
    doc_id = "test_doc_1"
    content = "Test troubleshooting content"
    metadata = {
        "problem": "Test problem",
        "category": "test",
        "device_type": "test_device"
    }
    
    await rag_service.add_document(doc_id, content, metadata)
    
    # Verify it can be retrieved
    results = await rag_service.retrieve_solutions("test troubleshooting")
    assert len(results) > 0
