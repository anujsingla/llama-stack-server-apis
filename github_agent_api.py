import os
import uuid
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

from github_agent import GitHubProjectAnalyst

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GitHub Project Analyst Agent API",
    description="REST API for the GitHub Project Analyst Agent using Llama Stack",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_instance: Optional[GitHubProjectAnalyst] = None

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "my-session-123",
                "message": "Analyze the repository facebook/react"
            }
        }

class ChatResponse(BaseModel):
    session_id: str
    message: str
    response: str
    success: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    agent_initialized: bool
    github_token_configured: bool
    llama_stack_url: str

class SessionResponse(BaseModel):
    session_id: str
    success: bool
    message: str

@app.on_event("startup")
async def startup_event():
    """Initialize the GitHub agent on startup"""
    global agent_instance
    try:
        logger.info("Initializing GitHub Project Analyst Agent...")
        agent_instance = GitHubProjectAnalyst()
        logger.info("GitHub Project Analyst Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {str(e)}")
        agent_instance = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    github_token_configured = bool(os.getenv("GITHUB_TOKEN"))
    llama_stack_url = os.getenv("LLAMA_STACK_URL", "http://localhost:8321")
    
    return HealthResponse(
        status="healthy" if agent_instance else "unhealthy",
        agent_initialized=agent_instance is not None,
        github_token_configured=github_token_configured,
        llama_stack_url=llama_stack_url
    )

@app.post("/sessions", response_model=SessionResponse)
async def create_session(session_name: Optional[str] = None):
    """Create a new chat session"""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        if not session_name:
            session_name = f"api_session_{uuid.uuid4().hex[:8]}"
        
        session_id = agent_instance.create_session(session_name)
        
        return SessionResponse(
            session_id=session_id,
            success=True,
            message=f"Session '{session_name}' created successfully"
        )
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Send a message to the GitHub agent and get response"""
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        session_id = request.session_id
        if not session_id:
            session_id = agent_instance.create_session(f"auto_session_{uuid.uuid4().hex[:8]}")
            logger.info(f"Created new session: {session_id}")
        
        logger.info(f"Processing message in session {session_id}: {request.message[:100]}...")
        response = agent_instance._chat(request.message, session_id)
        
        return ChatResponse(
            session_id=session_id,
            message=request.message,
            response=response,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            session_id=request.session_id or "unknown",
            message=request.message,
            response="",
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print("************************************************")
    print(f"Starting GitHub Project Analyst Agent API on {host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/health")
    print("************************************************")
    uvicorn.run(app, host=host, port=port)
