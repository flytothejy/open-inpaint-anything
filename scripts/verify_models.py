#!/usr/bin/env python3
"""
Model verification script for Inpaint Anything
"""

import os
import sys
from pathlib import Path
import torch
from omegaconf import OmegaConf

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_file_exists(path: str, description: str) -> bool:
    """Check if file exists and report status"""
    if os.path.exists(path):
        size = os.path.getsize(path) / (1024**3)  # Size in GB
        print(f"✅ {description}: {path} ({size:.2f} GB)")
        return True
    else:
        print(f"❌ {description}: {path} (missing)")
        return False

def verify_sam_models():
    """Verify SAM model files"""
    print("\n🔍 Checking SAM Models:")
    print("=" * 50)
    
    sam_models = [
        ("pretrained_models/sam_vit_h_4b8939.pth", "SAM ViT-H (default)"),
        ("pretrained_models/sam_vit_l_0b3195.pth", "SAM ViT-L (optional)"),
        ("pretrained_models/sam_vit_b_01ec64.pth", "SAM ViT-B (optional)"),
        ("weights/mobile_sam.pt", "Mobile SAM (optional)")
    ]
    
    results = []
    for path, desc in sam_models:
        results.append(check_file_exists(path, desc))
    
    # At least one SAM model should exist
    if not any(results[:3]):  # Check main SAM models
        print("⚠️  Warning: No main SAM models found!")
        return False
    
    return True

def verify_lama_model():
    """Verify LaMa model files"""
    print("\n🎨 Checking LaMa Model:")
    print("=" * 50)
    
    # Check LaMa directory
    lama_dir = "pretrained_models/big-lama"
    if not os.path.exists(lama_dir):
        print(f"❌ LaMa directory: {lama_dir} (missing)")
        return False
    
    # Check for checkpoint files (.pth or .ckpt)
    checkpoint_files = list(Path(lama_dir).glob("**/*.pth")) + list(Path(lama_dir).glob("**/*.ckpt"))
    if checkpoint_files:
        print(f"✅ LaMa model: {lama_dir} ({len(checkpoint_files)} checkpoint files)")
        for ckpt in checkpoint_files[:3]:  # Show first 3 files
            size = ckpt.stat().st_size / (1024**2)  # Size in MB
            print(f"   - {ckpt.name} ({size:.1f} MB)")
    else:
        print(f"❌ LaMa model: {lama_dir} (no checkpoint files found)")
        return False
    
    # Check LaMa config
    config_path = "lama/configs/prediction/default.yaml"
    if check_file_exists(config_path, "LaMa config"):
        try:
            config = OmegaConf.load(config_path)
            print(f"   - Config loaded successfully")
        except Exception as e:
            print(f"   - ⚠️  Config load error: {e}")
    
    return True

def verify_dependencies():
    """Verify Python dependencies"""
    print("\n📦 Checking Dependencies:")
    print("=" * 50)
    
    dependencies = [
        ("torch", "PyTorch"),
        ("torchvision", "TorchVision"),
        ("segment_anything", "Segment Anything"),
        ("diffusers", "Diffusers"),
        ("fastapi", "FastAPI"),
        ("omegaconf", "OmegaConf"),
        ("PIL", "Pillow")
    ]
    
    missing = []
    for module, name in dependencies:
        try:
            if module == "PIL":
                import PIL
                version = PIL.__version__
            else:
                mod = __import__(module)
                version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {name}: {version}")
        except ImportError:
            print(f"❌ {name}: not installed")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements/base.txt")
        return False
    
    return True

def check_cuda():
    """Check CUDA availability"""
    print("\n🚀 Checking CUDA:")
    print("=" * 50)
    
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device()
        device_name = torch.cuda.get_device_name(current_device)
        memory = torch.cuda.get_device_properties(current_device).total_memory / (1024**3)
        
        print(f"✅ CUDA available: {device_count} device(s)")
        print(f"   - Current device: {current_device}")
        print(f"   - Device name: {device_name}")
        print(f"   - Memory: {memory:.1f} GB")
        
        return True
    else:
        print("❌ CUDA not available (will use CPU)")
        print("   - Model loading will be slower")
        print("   - Consider setting USE_MOCK_SERVICE=true for testing")
        return False

def test_model_loading():
    """Test basic model loading"""
    print("\n🧪 Testing Model Loading:")
    print("=" * 50)
    
    try:
        # Test SAM model import
        from segment_anything import sam_model_registry
        print("✅ SAM model registry imported")
        
        # Test basic SAM model creation (without checkpoint)
        if os.path.exists("pretrained_models/sam_vit_h_4b8939.pth"):
            print("✅ SAM checkpoint file accessible")
        
        # Test LaMa imports
        sys.path.insert(0, str(project_root / "lama"))
        try:
            from saicinpainting.training.trainers import load_checkpoint
            print("✅ LaMa modules imported")
        except ImportError as e:
            print(f"❌ LaMa import error: {e}")
            return False
        
        # Test Stable Diffusion
        from diffusers import StableDiffusionInpaintPipeline
        print("✅ Stable Diffusion pipeline imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 Inpaint Anything - Model Verification")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(project_root)
    print(f"📁 Working directory: {os.getcwd()}")
    
    results = []
    
    # Run all checks
    results.append(verify_dependencies())
    results.append(verify_sam_models())
    results.append(verify_lama_model())
    results.append(check_cuda())
    results.append(test_model_loading())
    
    # Summary
    print("\n📊 Verification Summary:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All checks passed! Your setup is ready.")
        print("\n💡 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Run: ./scripts/start_dev.sh")
        print("3. Test API at: http://localhost:8000/docs")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed. Please fix the issues above.")
        if passed < 3:
            print("\n🛠️  Quick fixes:")
            print("- Run: ./scripts/download_models.sh")
            print("- Run: pip install -r requirements/base.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())