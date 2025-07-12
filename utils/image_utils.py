import asyncio
import base64
import io
import numpy as np
from PIL import Image
from typing import Tuple, Union
import aiofiles

from utils.exceptions import InvalidImageException, FileTooLargeException, UnsupportedImageFormatException
from config.settings import settings


async def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 string to numpy array asynchronously"""
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Check file size
        if len(image_data) > settings.max_file_size:
            raise FileTooLargeException(f"Image size {len(image_data)} exceeds limit {settings.max_file_size}")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Validate image format
        if image.format not in ['JPEG', 'PNG', 'WebP']:
            raise UnsupportedImageFormatException(f"Unsupported image format: {image.format}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large
        if max(image.size) > settings.max_image_size:
            ratio = settings.max_image_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        return np.array(image)
        
    except Exception as e:
        if isinstance(e, (FileTooLargeException, UnsupportedImageFormatException)):
            raise
        raise InvalidImageException(f"Failed to decode base64 image: {str(e)}")


async def encode_image_to_base64(image: np.ndarray, format: str = "PNG") -> str:
    """Encode numpy array to base64 string asynchronously"""
    try:
        # Convert numpy array to PIL Image
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        pil_image = Image.fromarray(image)
        
        # Convert to bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        buffer.seek(0)
        
        # Encode to base64
        image_data = buffer.getvalue()
        base64_string = base64.b64encode(image_data).decode('utf-8')
        
        return f"data:image/{format.lower()};base64,{base64_string}"
        
    except Exception as e:
        raise InvalidImageException(f"Failed to encode image to base64: {str(e)}")


async def load_image_from_file(file_content: bytes) -> np.ndarray:
    """Load image from file content asynchronously"""
    try:
        # Check file size
        if len(file_content) > settings.max_file_size:
            raise FileTooLargeException(f"File size {len(file_content)} exceeds limit {settings.max_file_size}")
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(file_content))
        
        # Validate image format
        if image.format not in ['JPEG', 'PNG', 'WebP']:
            raise UnsupportedImageFormatException(f"Unsupported image format: {image.format}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large
        if max(image.size) > settings.max_image_size:
            ratio = settings.max_image_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        return np.array(image)
        
    except Exception as e:
        if isinstance(e, (FileTooLargeException, UnsupportedImageFormatException)):
            raise
        raise InvalidImageException(f"Failed to load image from file: {str(e)}")


def validate_coordinates(coords: list, image_shape: Tuple[int, int]) -> list:
    """Validate point coordinates"""
    height, width = image_shape[:2]
    
    validated_coords = []
    for coord in coords:
        if len(coord) != 2:
            raise InvalidImageException("Each coordinate must have exactly 2 values [x, y]")
        
        x, y = coord
        if not (0 <= x <= width and 0 <= y <= height):
            raise InvalidImageException(f"Coordinate ({x}, {y}) is outside image bounds ({width}, {height})")
        
        validated_coords.append([float(x), float(y)])
    
    return validated_coords


def validate_point_labels(labels: list, coords_count: int) -> list:
    """Validate point labels"""
    if len(labels) != coords_count:
        raise InvalidImageException(f"Number of labels ({len(labels)}) must match number of coordinates ({coords_count})")
    
    for label in labels:
        if label not in [0, 1]:
            raise InvalidImageException(f"Point labels must be 0 or 1, got {label}")
    
    return [int(label) for label in labels]


async def resize_image_if_needed(image: np.ndarray, max_size: int = None) -> np.ndarray:
    """Resize image if it exceeds maximum size"""
    if max_size is None:
        max_size = settings.max_image_size
    
    height, width = image.shape[:2]
    if max(height, width) <= max_size:
        return image
    
    # Calculate new dimensions
    if height > width:
        new_height = max_size
        new_width = int(width * max_size / height)
    else:
        new_width = max_size
        new_height = int(height * max_size / width)
    
    # Resize using PIL for better quality
    pil_image = Image.fromarray(image)
    resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return np.array(resized_image)