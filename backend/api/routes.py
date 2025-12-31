"""
API routes for the IT Support Assistant
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict
import uuid
from loguru import logger

from .models import (
    ChatRequest, ChatResponse, AnalyzeRequest, AnalyzeResponse,
    FeedbackRequest, FeedbackResponse, SolutionSearchRequest,
    SolutionSearchResponse
)
from services.rag_service import RAGService
from services.llm_service import LLMService
from services.reasoning_engine import ReasoningEngine
from services.safety_checker import SafetyChecker

router = APIRouter()

# Session storage (in production, use Redis or similar)
sessions: Dict[str, list] = {}


def get_rag_service(request: Request) -> RAGService:
    """Get RAG service from app state"""
    from .main import rag_service
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service not available")
    return rag_service


def get_llm_service(request: Request) -> LLMService:
    """Get LLM service from app state"""
    from .main import llm_service
    if llm_service is None:
        raise HTTPException(status_code=503, detail="LLM service not available")
    return llm_service


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Main chat endpoint for conversational IT support
    """
    try:
        # Generate or use existing session ID
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get or create conversation history
        if session_id not in sessions:
            sessions[session_id] = []
        
        conversation_history = sessions[session_id]
        
        # Initialize reasoning engine
        reasoning_engine = ReasoningEngine(rag_service, llm_service)
        
        # Process the request
        response = await reasoning_engine.diagnose_and_solve(
            user_problem=request.message,
            conversation_history=conversation_history,
            device_info=request.device_info,
            technical_level=request.technical_level
        )
        
        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": request.message
        })
        conversation_history.append({
            "role": "assistant",
            "content": response["response"]
        })
        sessions[session_id] = conversation_history[-20:]  # Keep last 20 messages
        
        # Add session ID to response
        response["session_id"] = session_id
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_problem(
    request: AnalyzeRequest,
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Analyze a problem without providing full solution
    """
    try:
        reasoning_engine = ReasoningEngine(rag_service, llm_service)
        analysis = await reasoning_engine.analyze_problem(
            problem_description=request.problem_description,
            device_info=request.device_info
        )
        
        return AnalyzeResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/solutions/search", response_model=SolutionSearchResponse)
async def search_solutions(
    request: SolutionSearchRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Search for specific solutions in the knowledge base
    """
    try:
        # Build filter based on request
        filter_dict = {}
        if request.problem_category:
            filter_dict["category"] = request.problem_category
        if request.device_type:
            filter_dict["device_type"] = request.device_type
        
        # Retrieve solutions
        results = await rag_service.retrieve_solutions(
            query=request.query,
            top_k=request.limit,
            filter_dict=filter_dict if filter_dict else None
        )
        
        return SolutionSearchResponse(
            solutions=results,
            total_results=len(results)
        )
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on a solution
    """
    try:
        # In production, store this in a database
        logger.info(f"Feedback received for session {request.session_id}: "
                   f"Rating={request.rating}, Solved={request.solved}")
        
        # Store feedback (placeholder - implement database storage)
        feedback_data = {
            "session_id": request.session_id,
            "rating": request.rating,
            "solved": request.solved,
            "comment": request.comment
        }
        
        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in feedback endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session_history(session_id: str):
    """
    Get conversation history for a session
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": sessions[session_id]
    }


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a conversation session
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session cleared successfully"}
    
    raise HTTPException(status_code=404, detail="Session not found")
