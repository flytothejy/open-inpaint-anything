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
import threading
from pathlib import Path

# Global configuration
PROJECT_NAME = "open-inpaint-anything"
REPO_URL = "https://github.com/flytothejy/open-inpaint-anything.git"
PROJECT_DIR = None

def run_command(command, description="", cwd=None):
    """Run shell command and print status"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
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
    """Check if GPU is available"""
    print("\n🔍 Checking GPU availability...")
    
    # Check NVIDIA GPU
    success, output, _ = run_command("nvidia-smi", "GPU status check")
    if not success:
        print("❌ No GPU detected!")
        return False
    
    print("✅ GPU detected!")
    # Extract GPU info from nvidia-smi output
    lines = output.split('\n')
    for line in lines:
        if 'Tesla' in line or 'RTX' in line or 'GTX' in line or 'V100' in line or 'A100' in line:
            print(f"   GPU: {line.strip()}")
            break
    
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

def clone_repository():
    """Clone the repository"""
    global PROJECT_DIR
    print("\n📁 Setting up project...")
    
    # Check if already cloned
    if os.path.exists(PROJECT_NAME):
        print("✅ Repository already exists")
        success, _, _ = run_command("git pull", "Updating repository", cwd=PROJECT_NAME)
        if not success:
            print("⚠️  Git pull failed, continuing with existing files")
    else:
        # Clone repository
        success, _, _ = run_command(f"git clone {REPO_URL}", "Cloning repository")
        if not success:
            print("❌ Failed to clone repository")
            print("📝 Manual setup required:")
            print("   1. Check repository URL")
            print("   2. Verify repository is public")
            return False
    
    # Set project directory
    PROJECT_DIR = os.path.abspath(PROJECT_NAME)
    print(f"📂 Project directory: {PROJECT_DIR}")
    return True

def install_dependencies():
    """Install all required dependencies"""
    print("\n📦 Installing dependencies...")
    
    if not PROJECT_DIR:
        print("❌ Project directory not set!")
        return False
    
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
        cwd = PROJECT_DIR if "requirements/" in command else None
        success, _, _ = run_command(command, description, cwd=cwd)
        if not success:
            print(f"⚠️  Failed to install: {description}")
            return False
    
    return True

def create_colab_env():
    """Create Colab-optimized environment file"""
    print("\n⚙️  Creating Colab environment configuration...")
    
    if not PROJECT_DIR:
        print("❌ Project directory not set!")
        return False
    
    env_content = """# Model Configuration (GPU optimized for Colab)
SAM_MODEL_TYPE=vit_b
SAM_CHECKPOINT_PATH=./pretrained_models/sam_vit_b_01ec64.pth
LAMA_CONFIG_PATH=./lama/configs/prediction/default.yaml
LAMA_CHECKPOINT_PATH=./pretrained_models/big-lama

# Environment Settings
USE_MOCK_SERVICE=false
DEVICE=cuda
LOG_LEVEL=INFO

# Performance Settings
SAM_DEVICE=cuda
LAMA_DEVICE=cuda
STABLE_DIFFUSION_DEVICE=cuda

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    
    env_file_path = os.path.join(PROJECT_DIR, '.env')
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print("✅ Environment file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create environment file: {e}")
        return False

def download_models():
    """Download AI models"""
    print("\n🤖 Downloading AI models...")
    
    if not PROJECT_DIR:
        print("❌ Project directory not set!")
        return False
    
    # Make scripts executable
    run_command("chmod +x scripts/download_models.sh", 
                "Making download script executable", cwd=PROJECT_DIR)
    
    # Check if models already exist
    sam_model_path = os.path.join(PROJECT_DIR, 'pretrained_models/sam_vit_b_01ec64.pth')
    if os.path.exists(sam_model_path):
        print("✅ SAM models already downloaded")
    else:
        print("📥 Downloading models (this may take 5-10 minutes)...")
        success, _, _ = run_command("./scripts/download_models.sh", 
                                   "Downloading models", cwd=PROJECT_DIR)
        if not success:
            print("❌ Model download failed")
            return False
    
    return True

def verify_setup():
    """Verify the setup"""
    print("\n🔍 Verifying setup...")
    
    if not PROJECT_DIR:
        print("❌ Project directory not set!")
        return False
    
    success, _, _ = run_command("python scripts/verify_models.py", 
                               "Verifying models", cwd=PROJECT_DIR)
    return success

def start_server_test():
    """Start server for testing"""
    print("\n🚀 Starting FastAPI server test...")
    
    if not PROJECT_DIR:
        print("❌ Project directory not set!")
        return False
    
    def run_server():
        """Run the FastAPI server"""
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=PROJECT_DIR)
    
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
    if not start_server_test():
        print("❌ Setup completed but server test failed")
        print("🔧 Troubleshooting:")
        print("   1. Check server logs")
        print("   2. Verify model downloads")
        print("   3. Check GPU memory usage")
        return False
    
    # Step 8: Setup ngrok (optional)
    setup_ngrok()
    
    print("\n🎉 Setup completed successfully!")
    print("🔗 FastAPI server running at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    print(f"📁 Project directory: {PROJECT_DIR}")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All done! You can now test the Inpaint Anything API.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)