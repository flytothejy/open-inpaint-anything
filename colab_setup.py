#!/usr/bin/env python3
"""
Google Colab Setup Script for Inpaint Anything GPU Testing
Run this in a Colab cell to set up the entire environment
"""

import subprocess
import sys
import os
import time
import requests
import json
from pathlib import Path

def run_command(command, description=""):
    """Run shell command and print status"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr.strip()[:200]}...")
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False, "", str(e)

def check_gpu():
    """Check GPU availability"""
    print("🔍 Checking GPU availability...")
    
    success, stdout, stderr = run_command("nvidia-smi", "GPU status check")
    if success:
        print("✅ GPU detected!")
        # Extract GPU info
        lines = stdout.split('\n')
        for line in lines:
            if 'Tesla' in line or 'RTX' in line or 'GTX' in line:
                print(f"   GPU: {line.strip()}")
                break
    else:
        print("❌ No GPU detected. Make sure Runtime > Change runtime type > GPU is selected")
        return False
    
    # Check PyTorch CUDA
    try:
        import torch
        print(f"   PyTorch CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU count: {torch.cuda.device_count()}")
            print(f"   Current device: {torch.cuda.current_device()}")
            print(f"   Device name: {torch.cuda.get_device_name()}")
        return torch.cuda.is_available()
    except ImportError:
        print("   PyTorch not installed yet")
        return True  # GPU is available, PyTorch will be installed later

def install_dependencies():
    """Install all required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Change to project directory first
    os.chdir('open-inpaint-anything')
    
    commands = [
        ("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121", 
         "Installing PyTorch with CUDA 12.1"),
        ("pip install -r requirements/base.txt", 
         "Installing base requirements"),
        ("pip install 'numpy==1.24.4' 'opencv-python==4.9.0.80'", 
         "Installing compatible NumPy and OpenCV versions"),
        ("pip install git+https://github.com/facebookresearch/segment-anything.git", 
         "Installing Segment Anything"),
    ]
    
    for command, description in commands:
        success, _, _ = run_command(command, description)
        if not success:
            print(f"⚠️  Failed to install: {description}")
            return False
    
    return True

def clone_repository():
    """Clone the repository"""
    print("\n📁 Setting up project...")
    
    # Check if already cloned
    if os.path.exists('open-inpaint-anything'):
        print("✅ Repository already exists")
        run_command("cd open-inpaint-anything && git pull", "Updating repository")
    else:
        # Clone from our working repository with API implementation
        repo_url = "https://github.com/flytothejy/open-inpaint-anything.git"
        success, _, _ = run_command(f"git clone {repo_url}", "Cloning repository")
        if not success:
            print("❌ Failed to clone repository")
            print("📝 Manual setup required:")
            print("   1. Check repository URL")
            print("   2. Verify repository is public")
            return False
    
    return True

def create_colab_env():
    """Create Colab-optimized environment file"""
    print("\n⚙️  Creating Colab environment configuration...")
    
    # Change to project directory
    os.chdir('open-inpaint-anything')
    
    env_content = """# Model Configuration (GPU optimized for Colab)
SAM_MODEL_TYPE=vit_b
SAM_CHECKPOINT_PATH=./pretrained_models/sam_vit_b_01ec64.pth
LAMA_CONFIG_PATH=./lama/configs/prediction/default.yaml
LAMA_CHECKPOINT_PATH=./pretrained_models/big-lama
SD_MODEL_NAME=stabilityai/stable-diffusion-2-inpainting

# API Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
DEBUG=true
MAX_IMAGE_SIZE=1024
MAX_FILE_SIZE=10485760

# CORS
ALLOWED_ORIGINS=*

# Device (GPU)
DEVICE=cuda

# GPU Optimization
TORCH_NUM_THREADS=4

# Mock Service (disabled for GPU testing)
USE_MOCK_SERVICE=false
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file created")
    return True

def download_models():
    """Download AI models"""
    print("\n🤖 Downloading AI models...")
    
    # Change to project directory
    os.chdir('open-inpaint-anything')
    
    # Make scripts executable
    run_command("chmod +x scripts/download_models.sh", "Making download script executable")
    
    # Check if models already exist
    if os.path.exists('pretrained_models/sam_vit_b_01ec64.pth'):
        print("✅ SAM models already downloaded")
    else:
        print("📥 Downloading models (this may take 5-10 minutes)...")
        success, _, _ = run_command("./scripts/download_models.sh", "Downloading models")
        if not success:
            print("❌ Model download failed")
            return False
    
    return True

def verify_setup():
    """Verify the setup"""
    print("\n🔍 Verifying setup...")
    
    # Change to project directory
    os.chdir('open-inpaint-anything')
    
    success, _, _ = run_command("python scripts/verify_models.py", "Verifying models")
    return success

def start_server_test():
    """Start server for testing"""
    print("\n🚀 Starting FastAPI server test...")
    
    # Change to project directory
    os.chdir('open-inpaint-anything')
    
    # Start server in background
    import threading
    import subprocess
    
    def run_server():
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(15)
    
    # Test health endpoint
    try:
        response = requests.get('http://localhost:8000/api/v1/health', timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Server is running!")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Device: {result.get('device', 'unknown')}")
            
            models = result.get('models_loaded', {})
            print("   Models loaded:")
            for model, loaded in models.items():
                status = "✅" if loaded else "❌"
                print(f"     {model}: {status}")
            
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def setup_ngrok():
    """Set up ngrok for external access (optional)"""
    print("\n🌐 Setting up ngrok (optional)...")
    
    try:
        run_command("pip install pyngrok", "Installing pyngrok")
        
        print("🔗 To use ngrok:")
        print("   1. Get your authtoken from https://ngrok.com/")
        print("   2. Run: from pyngrok import ngrok")
        print("   3. Run: ngrok.set_auth_token('your_token')")
        print("   4. Run: public_url = ngrok.connect(8000)")
        print("   5. Print public_url to get external access URL")
        
    except Exception as e:
        print(f"⚠️  ngrok setup failed: {e}")

def main():
    """Main setup function"""
    print("🚀 Inpaint Anything GPU Setup for Google Colab")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Step 1: Check GPU
    if not check_gpu():
        return False
    
    # Step 2: Clone repository
    if not clone_repository():
        return False
    
    # Step 3: Install dependencies
    if not install_dependencies():
        return False
    
    # Step 4: Create environment
    if not create_colab_env():
        return False
    
    # Step 5: Download models
    if not download_models():
        return False
    
    # Step 6: Verify setup
    if not verify_setup():
        print("⚠️  Setup verification had issues, but continuing...")
    
    # Step 7: Test server
    if start_server_test():
        print("\n🎉 Setup completed successfully!")
        print("=" * 60)
        print("📋 Next steps:")
        print("   1. Test the API endpoints")
        print("   2. Run performance benchmarks")
        print("   3. Compare with CPU results")
        print("\n🔗 API Documentation: http://localhost:8000/docs")
        
        # Setup ngrok
        setup_ngrok()
        
        return True
    else:
        print("\n❌ Setup completed but server test failed")
        print("📋 Troubleshooting:")
        print("   1. Check server logs")
        print("   2. Verify model downloads")
        print("   3. Check GPU memory usage")
        return False

if __name__ == "__main__":
    main()