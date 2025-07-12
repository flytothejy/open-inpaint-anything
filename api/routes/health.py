from fastapi import APIRouter, HTTPException
from datetime import datetime
import time
import psutil
import logging

from api.models.responses import HealthResponse, ModelStatusResponse
from api.services.model_loader import model_loader
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Store startup time
_startup_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    try:
        # Check if models are loaded
        models_status = {
            "sam": model_loader.get_sam_predictor() is not None,
            "lama": model_loader.get_lama_model()[0] is not None,
            "stable_diffusion": model_loader.get_sd_pipeline() is not None,
        }
        
        # Get memory usage
        memory_info = model_loader.get_memory_usage()
        
        # Add system memory info
        system_memory = psutil.virtual_memory()
        memory_info.update({
            "system_total": system_memory.total,
            "system_available": system_memory.available,
            "system_percent": system_memory.percent
        })
        
        # Calculate uptime
        uptime = time.time() - _startup_time
        
        status = "healthy" if all(models_status.values()) else "partial"
        
        return HealthResponse(
            message="Service is running",
            status=status,
            models_loaded=models_status,
            device=model_loader.get_device(),
            memory_usage=memory_info,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check - returns 200 only if all models are loaded"""
    try:
        if not model_loader.is_ready():
            raise HTTPException(
                status_code=503, 
                detail="Service not ready - models still loading"
            )
        
        models_status = {
            "sam": True,
            "lama": True,
            "stable_diffusion": True,
        }
        
        return HealthResponse(
            message="Service is ready",
            status="ready",
            models_loaded=models_status,
            device=model_loader.get_device(),
            memory_usage=model_loader.get_memory_usage(),
            uptime=time.time() - _startup_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Readiness check failed")


@router.get("/models", response_model=ModelStatusResponse)
async def model_status():
    """Detailed model status endpoint"""
    try:
        sam_predictor = model_loader.get_sam_predictor()
        lama_model, lama_config = model_loader.get_lama_model()
        sd_pipeline = model_loader.get_sd_pipeline()
        
        models_info = {
            "sam": {
                "loaded": sam_predictor is not None,
                "model_type": settings.sam_model_type if sam_predictor else None,
                "checkpoint_path": settings.sam_checkpoint_path if sam_predictor else None,
                "device": model_loader.get_device() if sam_predictor else None
            },
            "lama": {
                "loaded": lama_model is not None,
                "config_path": settings.lama_config_path if lama_model else None,
                "checkpoint_path": settings.lama_checkpoint_path if lama_model else None,
                "device": model_loader.get_device() if lama_model else None
            },
            "stable_diffusion": {
                "loaded": sd_pipeline is not None,
                "model_name": settings.sd_model_name if sd_pipeline else None,
                "device": model_loader.get_device() if sd_pipeline else None,
                "torch_dtype": str(sd_pipeline.dtype) if sd_pipeline else None
            }
        }
        
        return ModelStatusResponse(
            message="Model status retrieved",
            models=models_info
        )
        
    except Exception as e:
        logger.error(f"Model status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Model status check failed")


@router.get("/metrics")
async def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        memory_info = model_loader.get_memory_usage()
        system_memory = psutil.virtual_memory()
        
        metrics = [
            f"# HELP inpaint_models_loaded Number of loaded models",
            f"# TYPE inpaint_models_loaded gauge",
            f"inpaint_models_loaded{{model=\"sam\"}} {1 if model_loader.get_sam_predictor() else 0}",
            f"inpaint_models_loaded{{model=\"lama\"}} {1 if model_loader.get_lama_model()[0] else 0}",
            f"inpaint_models_loaded{{model=\"stable_diffusion\"}} {1 if model_loader.get_sd_pipeline() else 0}",
            "",
            f"# HELP inpaint_memory_bytes Memory usage in bytes",
            f"# TYPE inpaint_memory_bytes gauge",
            f"inpaint_memory_bytes{{type=\"allocated\",device=\"{memory_info['device']}\"}} {memory_info['allocated']}",
            f"inpaint_memory_bytes{{type=\"cached\",device=\"{memory_info['device']}\"}} {memory_info['cached']}",
            f"inpaint_memory_bytes{{type=\"system_total\"}} {system_memory.total}",
            f"inpaint_memory_bytes{{type=\"system_available\"}} {system_memory.available}",
            "",
            f"# HELP inpaint_uptime_seconds Service uptime in seconds",
            f"# TYPE inpaint_uptime_seconds counter",
            f"inpaint_uptime_seconds {time.time() - _startup_time}",
        ]
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")