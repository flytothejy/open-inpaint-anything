import asyncio
import numpy as np
import torch
from typing import List, Tuple, Optional
import logging
from PIL import Image

from api.services.model_loader import model_loader
from utils.exceptions import ModelNotLoadedException, ProcessingTimeoutException, InvalidImageException
from utils.image_utils import validate_coordinates, validate_point_labels
from utils import dilate_mask
from config.settings import settings

# Import existing functions
from sam_segment import predict_masks_with_sam
from lama_inpaint import inpaint_img_with_lama, inpaint_img_with_builded_lama
from stable_diffusion_inpaint import fill_img_with_sd, replace_img_with_sd

logger = logging.getLogger(__name__)


class InpaintService:
    def __init__(self):
        self.model_loader = model_loader

    async def remove_object(
        self,
        image: np.ndarray,
        point_coords: List[List[float]],
        point_labels: List[int],
        dilate_kernel_size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Remove object from image using SAM + LaMa"""
        try:
            # Validate inputs
            point_coords = validate_coordinates(point_coords, image.shape)
            point_labels = validate_point_labels(point_labels, len(point_coords))
            
            # Get models
            sam_predictor = self.model_loader.get_sam_predictor()
            lama_model, lama_config = self.model_loader.get_lama_model()
            
            if sam_predictor is None:
                raise ModelNotLoadedException("SAM model not loaded")
            if lama_model is None:
                raise ModelNotLoadedException("LaMa model not loaded")
            
            # Generate mask with SAM
            logger.info("Generating mask with SAM")
            masks, scores, logits = await self._predict_masks_async(
                image, point_coords, point_labels, sam_predictor
            )
            
            # Select best mask (highest score)
            mask = masks[np.argmax(scores)]
            
            # Dilate mask if specified
            if dilate_kernel_size:
                mask = dilate_mask(mask, dilate_kernel_size)
            
            # Inpaint with LaMa
            logger.info("Inpainting with LaMa")
            inpainted_image = await self._inpaint_with_lama_async(
                image, mask, lama_model, lama_config
            )
            
            return inpainted_image, mask
            
        except Exception as e:
            logger.error(f"Error in remove_object: {str(e)}")
            raise

    async def fill_object(
        self,
        image: np.ndarray,
        point_coords: List[List[float]],
        point_labels: List[int],
        text_prompt: str,
        dilate_kernel_size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Fill object region with Stable Diffusion"""
        try:
            # Validate inputs
            point_coords = validate_coordinates(point_coords, image.shape)
            point_labels = validate_point_labels(point_labels, len(point_coords))
            
            if not text_prompt.strip():
                raise InvalidImageException("Text prompt cannot be empty")
            
            # Get models
            sam_predictor = self.model_loader.get_sam_predictor()
            sd_pipeline = self.model_loader.get_sd_pipeline()
            
            if sam_predictor is None:
                raise ModelNotLoadedException("SAM model not loaded")
            if sd_pipeline is None:
                raise ModelNotLoadedException("Stable Diffusion model not loaded")
            
            # Generate mask with SAM
            logger.info("Generating mask with SAM")
            masks, scores, logits = await self._predict_masks_async(
                image, point_coords, point_labels, sam_predictor
            )
            
            # Select best mask
            mask = masks[np.argmax(scores)]
            
            # Dilate mask if specified
            if dilate_kernel_size:
                mask = dilate_mask(mask, dilate_kernel_size)
            
            # Fill with Stable Diffusion
            logger.info("Filling with Stable Diffusion")
            filled_image = await self._fill_with_sd_async(
                image, mask, text_prompt, sd_pipeline
            )
            
            return filled_image, mask
            
        except Exception as e:
            logger.error(f"Error in fill_object: {str(e)}")
            raise

    async def replace_background(
        self,
        image: np.ndarray,
        point_coords: List[List[float]],
        point_labels: List[int],
        text_prompt: str,
        dilate_kernel_size: Optional[int] = None,
        num_inference_steps: int = 50
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Replace background using Stable Diffusion"""
        try:
            # Validate inputs
            point_coords = validate_coordinates(point_coords, image.shape)
            point_labels = validate_point_labels(point_labels, len(point_coords))
            
            if not text_prompt.strip():
                raise InvalidImageException("Text prompt cannot be empty")
            
            # Get models
            sam_predictor = self.model_loader.get_sam_predictor()
            sd_pipeline = self.model_loader.get_sd_pipeline()
            
            if sam_predictor is None:
                raise ModelNotLoadedException("SAM model not loaded")
            if sd_pipeline is None:
                raise ModelNotLoadedException("Stable Diffusion model not loaded")
            
            # Generate mask with SAM
            logger.info("Generating mask with SAM")
            masks, scores, logits = await self._predict_masks_async(
                image, point_coords, point_labels, sam_predictor
            )
            
            # Select best mask
            mask = masks[np.argmax(scores)]
            
            # Dilate mask if specified
            if dilate_kernel_size:
                mask = dilate_mask(mask, dilate_kernel_size)
            
            # Replace with Stable Diffusion
            logger.info("Replacing with Stable Diffusion")
            replaced_image = await self._replace_with_sd_async(
                image, mask, text_prompt, sd_pipeline, num_inference_steps
            )
            
            return replaced_image, mask
            
        except Exception as e:
            logger.error(f"Error in replace_background: {str(e)}")
            raise

    async def _predict_masks_async(
        self,
        image: np.ndarray,
        point_coords: List[List[float]],
        point_labels: List[int],
        sam_predictor
    ):
        """Predict masks asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Set image (this needs to be done in main thread)
        sam_predictor.set_image(image)
        
        # Run prediction in executor
        result = await loop.run_in_executor(
            None,
            self._predict_masks_sync,
            sam_predictor,
            np.array(point_coords),
            np.array(point_labels)
        )
        
        return result

    def _predict_masks_sync(self, sam_predictor, point_coords, point_labels):
        """Synchronous mask prediction"""
        masks, scores, logits = sam_predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True,
        )
        return masks, scores, logits

    async def _inpaint_with_lama_async(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        lama_model,
        lama_config
    ):
        """Inpaint with LaMa asynchronously"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            self._inpaint_with_lama_sync,
            image,
            mask,
            lama_model,
            lama_config
        )
        
        return result

    def _inpaint_with_lama_sync(self, image, mask, lama_model, lama_config):
        """Synchronous LaMa inpainting"""
        # Use the built model instead of loading each time
        return inpaint_img_with_builded_lama(
            lama_model, lama_config, image, mask, device=settings.device
        )

    async def _fill_with_sd_async(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        text_prompt: str,
        sd_pipeline
    ):
        """Fill with Stable Diffusion asynchronously"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            fill_img_with_sd,
            image,
            mask,
            text_prompt,
            settings.device
        )
        
        return result

    async def _replace_with_sd_async(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        text_prompt: str,
        sd_pipeline,
        num_inference_steps: int
    ):
        """Replace with Stable Diffusion asynchronously"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            None,
            replace_img_with_sd,
            image,
            mask,
            text_prompt,
            num_inference_steps,
            settings.device
        )
        
        return result


# Global service instance
inpaint_service = InpaintService()