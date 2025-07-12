from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import JSONResponse
import time
import logging
from typing import Optional
import json

from api.models.requests import (
    RemoveRequest, FillRequest, ReplaceRequest,
    RemoveImageRequest, FillImageRequest, ReplaceImageRequest
)
from api.models.responses import InpaintResponse, ErrorResponse
from api.services.inpaint_service import inpaint_service
from utils.image_utils import (
    decode_base64_image, encode_image_to_base64, load_image_from_file
)
from utils.exceptions import (
    InpaintException, ModelNotLoadedException, InvalidImageException,
    ProcessingTimeoutException, FileTooLargeException, UnsupportedImageFormatException
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_image_from_request(
    image: Optional[UploadFile] = File(None),
    image_data: Optional[str] = None
):
    """Helper to get image from either file upload or base64 data"""
    if image is not None:
        # Handle file upload
        if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise InvalidImageException(f"Unsupported image type: {image.content_type}")
        
        contents = await image.read()
        return await load_image_from_file(contents)
    
    elif image_data is not None:
        # Handle base64 data
        return await decode_base64_image(image_data)
    
    else:
        raise InvalidImageException("Either image file or image_data must be provided")


@router.post("/remove", response_model=InpaintResponse)
async def remove_object(
    image: Optional[UploadFile] = File(None),
    request: Optional[str] = Form(None),
    # Alternative: accept JSON body
    body: Optional[RemoveImageRequest] = None
):
    """Remove object from image using point coordinates"""
    start_time = time.time()
    
    try:
        # Parse request data
        if body is not None:
            # JSON body request
            req_data = body
            img_array = await get_image_from_request(image_data=body.image_data)
        else:
            # Form data request
            if request is None:
                raise InvalidImageException("Request data is required")
            
            req_dict = json.loads(request)
            req_data = RemoveRequest(**req_dict)
            img_array = await get_image_from_request(image=image)
        
        # Process image
        result_image, mask = await inpaint_service.remove_object(
            image=img_array,
            point_coords=req_data.point_coords,
            point_labels=req_data.point_labels,
            dilate_kernel_size=req_data.dilate_kernel_size
        )
        
        # Encode results
        result_b64 = await encode_image_to_base64(result_image)
        mask_b64 = await encode_image_to_base64((mask * 255).astype('uint8'))
        
        processing_time = time.time() - start_time
        
        return InpaintResponse(
            message="Object removed successfully",
            result_image=result_b64,
            mask_image=mask_b64,
            processing_time=processing_time,
            metadata={
                "point_coords": req_data.point_coords,
                "point_labels": req_data.point_labels,
                "dilate_kernel_size": req_data.dilate_kernel_size
            }
        )
        
    except InpaintException as e:
        logger.warning(f"Inpaint exception in remove_object: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in remove_object: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/fill", response_model=InpaintResponse)
async def fill_object(
    image: Optional[UploadFile] = File(None),
    request: Optional[str] = Form(None),
    # Alternative: accept JSON body
    body: Optional[FillImageRequest] = None
):
    """Fill object region using text prompt"""
    start_time = time.time()
    
    try:
        # Parse request data
        if body is not None:
            # JSON body request
            req_data = body
            img_array = await get_image_from_request(image_data=body.image_data)
        else:
            # Form data request
            if request is None:
                raise InvalidImageException("Request data is required")
            
            req_dict = json.loads(request)
            req_data = FillRequest(**req_dict)
            img_array = await get_image_from_request(image=image)
        
        # Process image
        result_image, mask = await inpaint_service.fill_object(
            image=img_array,
            point_coords=req_data.point_coords,
            point_labels=req_data.point_labels,
            text_prompt=req_data.text_prompt,
            dilate_kernel_size=req_data.dilate_kernel_size
        )
        
        # Encode results
        result_b64 = await encode_image_to_base64(result_image)
        mask_b64 = await encode_image_to_base64((mask * 255).astype('uint8'))
        
        processing_time = time.time() - start_time
        
        return InpaintResponse(
            message="Object filled successfully",
            result_image=result_b64,
            mask_image=mask_b64,
            processing_time=processing_time,
            metadata={
                "point_coords": req_data.point_coords,
                "point_labels": req_data.point_labels,
                "text_prompt": req_data.text_prompt,
                "dilate_kernel_size": req_data.dilate_kernel_size
            }
        )
        
    except InpaintException as e:
        logger.warning(f"Inpaint exception in fill_object: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in fill_object: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/replace", response_model=InpaintResponse)
async def replace_object(
    image: Optional[UploadFile] = File(None),
    request: Optional[str] = Form(None),
    # Alternative: accept JSON body
    body: Optional[ReplaceImageRequest] = None
):
    """Replace object using text prompt"""
    start_time = time.time()
    
    try:
        # Parse request data
        if body is not None:
            # JSON body request
            req_data = body
            img_array = await get_image_from_request(image_data=body.image_data)
        else:
            # Form data request
            if request is None:
                raise InvalidImageException("Request data is required")
            
            req_dict = json.loads(request)
            req_data = ReplaceRequest(**req_dict)
            img_array = await get_image_from_request(image=image)
        
        # Process image
        result_image, mask = await inpaint_service.replace_background(
            image=img_array,
            point_coords=req_data.point_coords,
            point_labels=req_data.point_labels,
            text_prompt=req_data.text_prompt,
            dilate_kernel_size=req_data.dilate_kernel_size,
            num_inference_steps=req_data.num_inference_steps
        )
        
        # Encode results
        result_b64 = await encode_image_to_base64(result_image)
        mask_b64 = await encode_image_to_base64((mask * 255).astype('uint8'))
        
        processing_time = time.time() - start_time
        
        return InpaintResponse(
            message="Object replaced successfully",
            result_image=result_b64,
            mask_image=mask_b64,
            processing_time=processing_time,
            metadata={
                "point_coords": req_data.point_coords,
                "point_labels": req_data.point_labels,
                "text_prompt": req_data.text_prompt,
                "dilate_kernel_size": req_data.dilate_kernel_size,
                "num_inference_steps": req_data.num_inference_steps
            }
        )
        
    except InpaintException as e:
        logger.warning(f"Inpaint exception in replace_object: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in replace_object: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Inpaint API is working", "timestamp": time.time()}