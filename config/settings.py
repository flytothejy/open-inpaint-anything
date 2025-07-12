from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import torch
from pathlib import Path


class Settings(BaseSettings):
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    sam_model_type: str = Field(default="vit_h", env="SAM_MODEL_TYPE")
    sam_checkpoint_path: str = Field(
        default="./pretrained_models/sam_vit_h_4b8939.pth",
        env="SAM_CHECKPOINT_PATH"
    )
    
    lama_config_path: str = Field(
        default="./lama/configs/prediction/default.yaml",
        env="LAMA_CONFIG_PATH"
    )
    lama_checkpoint_path: str = Field(
        default="./pretrained_models/big-lama",
        env="LAMA_CHECKPOINT_PATH"
    )
    
    sd_model_name: str = Field(
        default="stabilityai/stable-diffusion-2-inpainting",
        env="SD_MODEL_NAME"
    )
    
    max_image_size: int = Field(default=2048, env="MAX_IMAGE_SIZE")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    allowed_origins: str = Field(default="*", env="ALLOWED_ORIGINS")
    
    device: str = Field(default="auto", env="DEVICE")
    
    # CPU Optimization
    omp_num_threads: Optional[int] = Field(default=None, env="OMP_NUM_THREADS")
    torch_num_threads: Optional[int] = Field(default=None, env="TORCH_NUM_THREADS")
    
    use_mock_service: bool = Field(default=False, env="USE_MOCK_SERVICE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            
        # Apply CPU optimizations
        if self.device == "cpu":
            if self.omp_num_threads:
                torch.set_num_threads(self.omp_num_threads)
                print(f"Set PyTorch threads to {self.omp_num_threads}")
            
        if not torch.cuda.is_available() and not self.use_mock_service:
            print("Warning: CUDA not available. Using CPU mode with optimizations.")


settings = Settings()