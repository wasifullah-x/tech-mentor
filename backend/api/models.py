"""
Pydantic models for API requests and responses
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class DeviceInfo(BaseModel):
    """Device information for better diagnostics"""
    device_type: Optional[str] = Field(None, description="laptop, desktop, phone, tablet")
    os: Optional[str] = Field(None, description="windows, macos, linux, android, ios")
    os_version: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None


class ChatMessage(BaseModel):
    """Single chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Main chat endpoint request"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    device_info: Optional[DeviceInfo] = None
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    technical_level: Optional[Literal["beginner", "intermediate", "advanced"]] = "beginner"


class SolutionStep(BaseModel):
    """Individual solution step"""
    step_number: int
    action: str
    explanation: str
    risk_level: Literal["safe", "caution", "risky"]
    expected_outcome: Optional[str] = None
    troubleshooting_tips: Optional[List[str]] = None


class Cause(BaseModel):
    """Potential cause of the problem"""
    cause: str
    likelihood: Literal["high", "medium", "low"]
    explanation: str


class ChatResponse(BaseModel):
    """Main chat endpoint response"""
    response: str
    reasoning_type: str = Field(..., description="Which reasoning route produced this response")
    session_id: str
    problem_understanding: str
    likely_causes: List[Cause]
    solution_steps: List[SolutionStep]
    next_steps: str
    follow_up_question: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    requires_professional_help: bool = False
    sources: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    """Problem analysis only request"""
    problem_description: str = Field(..., min_length=1, max_length=2000)
    device_info: Optional[DeviceInfo] = None


class AnalyzeResponse(BaseModel):
    """Problem analysis response"""
    problem_category: str
    severity: Literal["low", "medium", "high", "critical"]
    likely_causes: List[Cause]
    estimated_complexity: Literal["simple", "moderate", "complex", "expert"]
    requires_data_backup: bool
    safe_to_attempt: bool


class FeedbackRequest(BaseModel):
    """User feedback on solution"""
    session_id: str
    message_id: Optional[str] = None
    rating: Literal["helpful", "not_helpful", "partially_helpful"]
    solved: bool
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback submission response"""
    success: bool
    message: str


class SolutionSearchRequest(BaseModel):
    """Search for specific solutions"""
    query: str
    problem_category: Optional[str] = None
    device_type: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)


class SolutionSearchResponse(BaseModel):
    """Solution search results"""
    solutions: List[Dict[str, Any]]
    total_results: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    vector_db_status: str
    llm_status: str
    uptime_seconds: float
