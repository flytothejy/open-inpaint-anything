from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = Field(default=False)
    error_code: Optional[str] = Field(None, description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class InpaintResponse(BaseResponse):
    """Response model for inpainting operations"""
    success: bool = Field(default=True)
    result_image: str = Field(..., description="Base64 encoded result image")
    mask_image: Optional[str] = Field(None, description="Base64 encoded mask image")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional metadata about the operation"
    )


class HealthResponse(BaseResponse):
    """Health check response model"""
    success: bool = Field(default=True)
    status: str = Field(..., description="Service status")
    models_loaded: Dict[str, bool] = Field(
        ..., 
        description="Status of loaded models"
    )
    device: str = Field(..., description="Current device (cpu/cuda)")
    memory_usage: Optional[Dict[str, Any]] = Field(
        None, 
        description="Memory usage statistics"
    )
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")


class ModelStatusResponse(BaseResponse):
    """Model status response"""
    success: bool = Field(default=True)
    models: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Detailed status of each model"
    )


class BatchResponse(BaseResponse):
    """Batch operation response"""
    success: bool = Field(default=True)
    results: List[Dict[str, Any]] = Field(..., description="List of operation results")
    total_items: int = Field(..., description="Total number of items processed")
    successful_items: int = Field(..., description="Number of successfully processed items")
    failed_items: int = Field(..., description="Number of failed items")
    errors: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="List of errors for failed items"
    )