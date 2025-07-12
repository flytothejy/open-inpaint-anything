import asyncio
import numpy as np
from typing import List, Tuple, Optional
import logging
from PIL import Image
import io
import base64

from utils.image_utils import validate_coordinates, validate_point_labels
from utils.exceptions import InvalidImageException

logger = logging.getLogger(__name__)


class MockInpaintService:
    """Mock service for testing API without actual models"""
    
    def __init__(self):
        logger.info("Using Mock Inpaint Service (no actual AI models loaded)")

    async def remove_object(
        self,
        image: np.ndarray,
        point_coords: List[List[float]],
        point_labels: List[int],
        dilate_kernel_size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Mock object removal - returns image with red rectangle removed"""
        try:
            # Validate inputs
            point_coords = validate_coordinates(point_coords, image.shape)
            point_labels = validate_point_labels(point_labels, len(point_coords))
            
            logger.info(f"Mock remove_object: {len(point_coords)} points")
            
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            # Create a simple mock result
            result_image = image.copy()
            mask = np.zeros(image.shape[:2], dtype=bool)
            
            # Create mock mask around first point
            if point_coords:
                x, y = point_coords[0]
                x, y = int(x), int(y)
                # Create a small rectangle around the point
                size = 50
                y1, y2 = max(0, y-size), min(image.shape[0], y+size)
                x1, x2 = max(0, x-size), min(image.shape[1], x+size)
                
                # Fill the area with average color (simulating inpainting)
                avg_color = np.mean(image, axis=(0, 1))
                result_image[y1:y2, x1:x2] = avg_color
                mask[y1:y2, x1:x2] = True
                
            return result_image, mask
            
        except Exception as e:
            logger.error(f"Error in mock remove_object: {str(e)}")
            raise

    async def fill_object(
        self,
        image: np.ndarray,
        point_coords: List[List[float]],
        point_labels: List[int],
        text_prompt: str,
        dilate_kernel_size: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Mock object filling - returns image with colored rectangle"""
        try:
            # Validate inputs
            point_coords = validate_coordinates(point_coords, image.shape)
            point_labels = validate_point_labels(point_labels, len(point_coords))
            
            if not text_prompt.strip():
                raise InvalidImageException("Text prompt cannot be empty")
            
            logger.info(f"Mock fill_object: '{text_prompt}' at {len(point_coords)} points")
            
            # Simulate processing delay
            await asyncio.sleep(1.0)
            
            # Create a simple mock result
            result_image = image.copy()
            mask = np.zeros(image.shape[:2], dtype=bool)
            
            # Create mock mask and fill with color based on prompt
            if point_coords:
                x, y = point_coords[0]
                x, y = int(x), int(y)
                size = 50
                y1, y2 = max(0, y-size), min(image.shape[0], y+size)
                x1, x2 = max(0, x-size), min(image.shape[1], x+size)
                
                # Choose color based on text prompt
                if "red" in text_prompt.lower():
                    color = [255, 0, 0]
                elif "blue" in text_prompt.lower():
                    color = [0, 0, 255]
                elif "green" in text_prompt.lower():
                    color = [0, 255, 0]
                elif "flower" in text_prompt.lower():
                    color = [255, 192, 203]  # Pink
                elif "sky" in text_prompt.lower():
                    color = [135, 206, 235]  # Sky blue
                else:
                    color = [128, 128, 128]  # Gray
                
                result_image[y1:y2, x1:x2] = color
                mask[y1:y2, x1:x2] = True
                
            return result_image, mask
            
        except Exception as e:
            logger.error(f"Error in mock fill_object: {str(e)}")
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
        """Mock background replacement - returns image with gradient background"""
        try:
            # Validate inputs
            point_coords = validate_coordinates(point_coords, image.shape)
            point_labels = validate_point_labels(point_labels, len(point_coords))
            
            if not text_prompt.strip():
                raise InvalidImageException("Text prompt cannot be empty")
            
            logger.info(f"Mock replace_background: '{text_prompt}' at {len(point_coords)} points, steps={num_inference_steps}")
            
            # Simulate processing delay (more steps = longer delay)
            await asyncio.sleep(num_inference_steps / 100.0)
            
            # Create a simple mock result
            result_image = image.copy()
            mask = np.zeros(image.shape[:2], dtype=bool)
            
            # Create mock mask and replace with gradient
            if point_coords:
                x, y = point_coords[0]
                x, y = int(x), int(y)
                size = 80
                y1, y2 = max(0, y-size), min(image.shape[0], y+size)
                x1, x2 = max(0, x-size), min(image.shape[1], x+size)
                
                # Create gradient based on text prompt
                height, width = y2 - y1, x2 - x1
                
                if "sunset" in text_prompt.lower():
                    # Orange to red gradient
                    gradient = np.zeros((height, width, 3), dtype=np.uint8)
                    for i in range(height):
                        ratio = i / height
                        gradient[i, :] = [255, int(165 * (1-ratio)), 0]
                elif "ocean" in text_prompt.lower():
                    # Blue gradient
                    gradient = np.zeros((height, width, 3), dtype=np.uint8)
                    for i in range(height):
                        ratio = i / height
                        gradient[i, :] = [0, int(100 + 100 * ratio), 255]
                else:
                    # Default gradient (gray)
                    gradient = np.zeros((height, width, 3), dtype=np.uint8)
                    for i in range(height):
                        val = int(100 + 100 * i / height)
                        gradient[i, :] = [val, val, val]
                
                result_image[y1:y2, x1:x2] = gradient
                mask[y1:y2, x1:x2] = True
                
            return result_image, mask
            
        except Exception as e:
            logger.error(f"Error in mock replace_background: {str(e)}")
            raise


# Global service instance
mock_inpaint_service = MockInpaintService()