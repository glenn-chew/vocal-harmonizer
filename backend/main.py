from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any

from config import settings
from models.schemas import (
    AnalysisRequest, AnalysisResponse, VerificationRequest, 
    VerificationResponse, HealthResponse, ErrorResponse, RiskItem, RiskLevel
)
from agents.risk_analysis_agent import RiskAnalysisAgent
from agents.verification_agent import VerificationAgent
from vector_store.supabase_store import SupabaseVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Architecture Security Analysis API",
    description="Agentic backend for analyzing and verifying cloud architecture security",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents and services
risk_agent = RiskAnalysisAgent()
verification_agent = VerificationAgent()
vector_store = SupabaseVectorStore()

# Dependency to check if services are healthy
def get_healthy_services() -> Dict[str, str]:
    """Check health of all services"""
    services = {}
    
    try:
        # Check OpenAI (by making a simple call)
        risk_agent._call_openai([{"role": "user", "content": "test"}])
        services["openai"] = "healthy"
    except Exception as e:
        services["openai"] = f"unhealthy: {str(e)}"
    
    try:
        # Check Supabase
        if vector_store.health_check():
            services["supabase"] = "healthy"
        else:
            services["supabase"] = "unhealthy"
    except Exception as e:
        services["supabase"] = f"unhealthy: {str(e)}"
    
    return services

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = get_healthy_services()
    
    # Determine overall status
    unhealthy_services = [k for k, v in services.items() if "unhealthy" in v]
    status = "healthy" if not unhealthy_services else "degraded"
    
    return HealthResponse(
        status=status,
        services=services
    )

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_architecture(request: AnalysisRequest):
    """Analyze architecture diagram for security risks"""
    try:
        logger.info("Starting architecture analysis")
        
        # Perform risk analysis
        analysis_result = risk_agent.process(request.diagram)
        
        # Generate verification (corrected diagram)
        verification_result = verification_agent.process(
            request.diagram, 
            analysis_result.risks
        )
        
        return AnalysisResponse(
            analysis=analysis_result,
            verification=verification_result
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/verify", response_model=VerificationResponse)
async def verify_architecture(request: VerificationRequest):
    """Generate corrected architecture based on risk analysis"""
    try:
        logger.info("Starting architecture verification")
        
        # Convert risk dictionaries to RiskItem objects
        risk_items = []
        for risk_dict in request.risks:
            risk_item = RiskItem(
                id=risk_dict.get("id", ""),
                level=RiskLevel(risk_dict["level"]),
                title=risk_dict["title"],
                description=risk_dict["description"],
                service_affected=risk_dict.get("service_affected"),
                recommendation=risk_dict["recommendation"],
                compliance_rule=risk_dict.get("compliance_rule")
            )
            risk_items.append(risk_item)
        
        result = verification_agent.process(
            request.original_diagram,
            risk_items
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@app.post("/api/analyze-and-verify", response_model=AnalysisResponse)
async def analyze_and_verify(request: AnalysisRequest):
    """Combined endpoint for analysis and verification"""
    try:
        logger.info("Starting combined analysis and verification")
        
        # Perform risk analysis
        analysis_result = risk_agent.process(request.diagram)
        
        # Generate verification (corrected diagram)
        verification_result = verification_agent.process(
            request.diagram, 
            analysis_result.risks
        )
        
        return AnalysisResponse(
            analysis=analysis_result,
            verification=verification_result
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Combined analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Combined analysis failed: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred",
            code="INTERNAL_ERROR"
        ).dict()
    )

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting up Architecture Security Analysis API")
    
    # Initialize vector store
    try:
        vector_store.initialize_database()
        logger.info("Vector store initialized")
    except Exception as e:
        logger.warning(f"Vector store initialization failed: {str(e)}")
    
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Architecture Security Analysis API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "dev"
    )
