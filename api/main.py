from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio

from config.settings import settings
from api.routes import health, inpaint
from api.middleware.cors import setup_cors
from api.middleware.logging import setup_logging, LoggingMiddleware
from utils.exceptions import InpaintException

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting Inpaint API server...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Device: {settings.device}")
    
    if settings.use_mock_service:
        logger.info("Using mock service (models not loaded)")
    else:
        try:
            # Import model loader only when needed
            from api.services.model_loader import model_loader
            
            # Load models on startup
            logger.info("Loading AI models...")
            await model_loader.load_all_models()
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            if settings.environment == "production":
                raise
            else:
                logger.warning("Continuing without models (development mode)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Inpaint API server...")


# Create FastAPI app
app = FastAPI(
    title="Inpaint Anything API",
    description="FastAPI server for AI-powered image inpainting using SAM, LaMa, and Stable Diffusion",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Exception handlers
@app.exception_handler(InpaintException)
async def inpaint_exception_handler(request, exc: InpaintException):
    """Handle custom inpaint exceptions"""
    logger.warning(f"Inpaint exception: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": str(exc),
            "error_code": exc.__class__.__name__
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": "HTTPException"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "InternalServerError"
        }
    )


# Include routers
app.include_router(
    health.router,
    prefix=settings.api_prefix,
    tags=["health"]
)

app.include_router(
    inpaint.router,
    prefix=settings.api_prefix,
    tags=["inpaint"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Inpaint Anything API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health"
    }


@app.get("/info")
async def info():
    """API information endpoint"""
    return {
        "title": "Inpaint Anything API",
        "version": "1.0.0",
        "environment": settings.environment,
        "device": settings.device,
        "models": {
            "sam_model_type": settings.sam_model_type,
            "sd_model_name": settings.sd_model_name
        },
        "endpoints": {
            "health": f"{settings.api_prefix}/health",
            "ready": f"{settings.api_prefix}/ready",
            "models": f"{settings.api_prefix}/models",
            "remove": f"{settings.api_prefix}/remove",
            "fill": f"{settings.api_prefix}/fill", 
            "replace": f"{settings.api_prefix}/replace"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )