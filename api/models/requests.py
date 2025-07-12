from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
import re


class InpaintBaseRequest(BaseModel):
    point_coords: List[List[float]] = Field(
        ..., 
        description="List of point coordinates [[x1, y1], [x2, y2], ...]",
        example=[[100.0, 200.0], [150.0, 250.0]]
    )
    point_labels: List[int] = Field(
        ..., 
        description="List of point labels (1 for foreground, 0 for background)",
        example=[1, 1]
    )
    dilate_kernel_size: Optional[int] = Field(
        None,
        ge=0,
        le=50,
        description="Dilate kernel size for mask processing. Default: None"
    )

    @validator('point_coords')
    def validate_point_coords(cls, v):
        if not v:
            raise ValueError("point_coords cannot be empty")
        
        for i, coord in enumerate(v):
            if len(coord) != 2:
                raise ValueError(f"Point coordinate {i} must have exactly 2 values [x, y]")
            
            x, y = coord
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                raise ValueError(f"Point coordinate {i} values must be numbers")
            
            if x < 0 or y < 0:
                raise ValueError(f"Point coordinate {i} values must be non-negative")
        
        return v

    @validator('point_labels')
    def validate_point_labels(cls, v, values):
        if not v:
            raise ValueError("point_labels cannot be empty")
        
        if 'point_coords' in values:
            coords_len = len(values['point_coords'])
            if len(v) != coords_len:
                raise ValueError(f"Number of labels ({len(v)}) must match number of coordinates ({coords_len})")
        
        for i, label in enumerate(v):
            if label not in [0, 1]:
                raise ValueError(f"Point label {i} must be 0 or 1, got {label}")
        
        return v


class RemoveRequest(InpaintBaseRequest):
    """Request model for object removal"""
    pass


class FillRequest(InpaintBaseRequest):
    """Request model for object filling with text prompt"""
    text_prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt for filling the masked area",
        example="beautiful flower garden"
    )

    @validator('text_prompt')
    def validate_text_prompt(cls, v):
        if not v.strip():
            raise ValueError("text_prompt cannot be empty or only whitespace")
        
        # Basic sanitization - remove potentially harmful patterns
        cleaned = re.sub(r'[<>"\']', '', v.strip())
        if len(cleaned) < 1:
            raise ValueError("text_prompt must contain valid characters")
        
        return cleaned


class ReplaceRequest(InpaintBaseRequest):
    """Request model for object replacement with text prompt"""
    text_prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Text prompt for replacing the masked area",
        example="modern car in street"
    )
    num_inference_steps: Optional[int] = Field(
        50,
        ge=10,
        le=150,
        description="Number of inference steps for Stable Diffusion. Default: 50"
    )

    @validator('text_prompt')
    def validate_text_prompt(cls, v):
        if not v.strip():
            raise ValueError("text_prompt cannot be empty or only whitespace")
        
        # Basic sanitization
        cleaned = re.sub(r'[<>"\']', '', v.strip())
        if len(cleaned) < 1:
            raise ValueError("text_prompt must contain valid characters")
        
        return cleaned


class ImageRequest(BaseModel):
    """Base request model for image data"""
    image_data: Optional[str] = Field(
        None,
        description="Base64 encoded image data (optional if using file upload)"
    )

    @validator('image_data')
    def validate_image_data(cls, v):
        if v is not None:
            # Basic base64 validation
            if not v.strip():
                raise ValueError("image_data cannot be empty")
            
            # Check for data URL format
            if v.startswith('data:image'):
                parts = v.split(',', 1)
                if len(parts) != 2:
                    raise ValueError("Invalid data URL format")
                v = parts[1]
            
            # Basic base64 character validation
            if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', v):
                raise ValueError("Invalid base64 encoding")
        
        return v


class RemoveImageRequest(ImageRequest, RemoveRequest):
    """Combined request for image removal with base64 data"""
    pass


class FillImageRequest(ImageRequest, FillRequest):
    """Combined request for image filling with base64 data"""
    pass


class ReplaceImageRequest(ImageRequest, ReplaceRequest):
    """Combined request for image replacement with base64 data"""
    pass