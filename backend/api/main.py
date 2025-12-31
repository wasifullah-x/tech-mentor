"""
Main FastAPI application
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
from loguru import logger

from .config import settings
from .routes import router
from services.rag_service import RAGService
from services.llm_service import LLMService

# Application startup time
START_TIME = time.time()

# Global service instances
rag_service: RAGService = None
llm_service: LLMService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    global rag_service, llm_service
    
    logger.info("Starting IT Support Technical Assistant API...")
    
    # Initialize services
    try:
        logger.info("Initializing RAG service...")
        rag_service = RAGService()
        await rag_service.initialize()
        
        logger.info("Initializing LLM service...")
        llm_service = LLMService()
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    if rag_service:
        await rag_service.close()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="IT Support Technical Assistant API",
    description="AI-powered IT support system with RAG and multi-step reasoning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(f"Request {request_id} failed: {e}")
        raise


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


# Include routers
app.include_router(router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "IT Support Technical Assistant API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


# Health check
@app.get("/health")
async def health_check():
    uptime = time.time() - START_TIME
    
    # Check vector DB status
    vector_db_status = "operational"
    try:
        if rag_service:
            # Simple check - try to get collection count
            rag_service.collection.count()
    except Exception as e:
        vector_db_status = f"error: {str(e)}"
    
    # Check LLM status
    llm_status = "operational" if llm_service else "not initialized"
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "vector_db_status": vector_db_status,
        "llm_status": llm_status,
        "uptime_seconds": uptime
    }


def get_rag_service() -> RAGService:
    """Dependency to get RAG service"""
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    return rag_service


def get_llm_service() -> LLMService:
    """Dependency to get LLM service"""
    if llm_service is None:
        raise HTTPException(status_code=503, detail="LLM service not initialized")
    return llm_service
