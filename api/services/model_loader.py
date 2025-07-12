import asyncio
import torch
from typing import Optional
from pathlib import Path
import logging

from segment_anything import SamPredictor, sam_model_registry
from diffusers import StableDiffusionInpaintPipeline
from omegaconf import OmegaConf
import sys
import os

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "lama"))
from saicinpainting.training.trainers import load_checkpoint

from config.settings import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    _instance: Optional['ModelLoader'] = None
    _sam_predictor: Optional[SamPredictor] = None
    _lama_model = None
    _lama_config = None
    _sd_pipeline: Optional[StableDiffusionInpaintPipeline] = None
    _device: str = settings.device

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def load_sam_model(self) -> SamPredictor:
        """Load SAM model asynchronously"""
        if self._sam_predictor is not None:
            return self._sam_predictor
            
        logger.info(f"Loading SAM model: {settings.sam_model_type}")
        
        if not Path(settings.sam_checkpoint_path).exists():
            raise FileNotFoundError(f"SAM checkpoint not found: {settings.sam_checkpoint_path}")
        
        # Run in executor for CPU-intensive model loading
        loop = asyncio.get_event_loop()
        sam, predictor = await loop.run_in_executor(
            None, 
            self._load_sam_sync
        )
        
        self._sam_predictor = predictor
        logger.info("SAM model loaded successfully")
        return self._sam_predictor

    def _load_sam_sync(self):
        """Synchronous SAM model loading"""
        sam = sam_model_registry[settings.sam_model_type](
            checkpoint=settings.sam_checkpoint_path
        )
        sam.to(device=self._device)
        predictor = SamPredictor(sam)
        return sam, predictor

    async def load_lama_model(self):
        """Load LaMa model asynchronously"""
        if self._lama_model is not None:
            return self._lama_model, self._lama_config
            
        logger.info("Loading LaMa model")
        
        if not Path(settings.lama_config_path).exists():
            raise FileNotFoundError(f"LaMa config not found: {settings.lama_config_path}")
        if not Path(settings.lama_checkpoint_path).exists():
            raise FileNotFoundError(f"LaMa checkpoint not found: {settings.lama_checkpoint_path}")
        
        # Run in executor for CPU-intensive model loading  
        loop = asyncio.get_event_loop()
        model, config = await loop.run_in_executor(
            None,
            self._load_lama_sync
        )
        
        self._lama_model = model
        self._lama_config = config
        logger.info("LaMa model loaded successfully")
        return self._lama_model, self._lama_config

    def _load_lama_sync(self):
        """Synchronous LaMa model loading"""
        config = OmegaConf.load(settings.lama_config_path)
        config.model.path = settings.lama_checkpoint_path
        
        model = load_checkpoint(config, settings.lama_checkpoint_path, strict=False, map_location='cpu')
        model.freeze()
        model.to(self._device)
        
        return model, config

    async def load_sd_pipeline(self) -> StableDiffusionInpaintPipeline:
        """Load Stable Diffusion pipeline asynchronously"""
        if self._sd_pipeline is not None:
            return self._sd_pipeline
            
        logger.info(f"Loading Stable Diffusion model: {settings.sd_model_name}")
        
        # Run in executor for CPU-intensive model loading
        loop = asyncio.get_event_loop()
        pipeline = await loop.run_in_executor(
            None,
            self._load_sd_sync
        )
        
        self._sd_pipeline = pipeline
        logger.info("Stable Diffusion model loaded successfully")
        return self._sd_pipeline

    def _load_sd_sync(self):
        """Synchronous SD pipeline loading"""
        pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            settings.sd_model_name,
            torch_dtype=torch.float32 if self._device == "cpu" else torch.float16,
        ).to(self._device)
        return pipeline

    async def load_all_models(self):
        """Load all models concurrently"""
        logger.info("Loading all models...")
        
        tasks = [
            self.load_sam_model(),
            self.load_lama_model(),
            self.load_sd_pipeline(),
        ]
        
        await asyncio.gather(*tasks)
        logger.info("All models loaded successfully")

    def get_sam_predictor(self) -> Optional[SamPredictor]:
        """Get loaded SAM predictor"""
        return self._sam_predictor

    def get_lama_model(self):
        """Get loaded LaMa model and config"""
        return self._lama_model, self._lama_config

    def get_sd_pipeline(self) -> Optional[StableDiffusionInpaintPipeline]:
        """Get loaded SD pipeline"""
        return self._sd_pipeline

    def is_ready(self) -> bool:
        """Check if all models are loaded"""
        return (
            self._sam_predictor is not None and
            self._lama_model is not None and
            self._sd_pipeline is not None
        )

    def get_device(self) -> str:
        """Get current device"""
        return self._device

    def get_memory_usage(self) -> dict:
        """Get memory usage statistics"""
        if self._device == "cuda":
            return {
                "device": self._device,
                "allocated": torch.cuda.memory_allocated(),
                "cached": torch.cuda.memory_reserved(),
                "max_allocated": torch.cuda.max_memory_allocated(),
            }
        else:
            return {
                "device": self._device,
                "allocated": 0,
                "cached": 0,
                "max_allocated": 0,
            }


# Global instance
model_loader = ModelLoader()