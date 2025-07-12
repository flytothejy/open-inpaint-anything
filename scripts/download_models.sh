#!/bin/bash

# Model Download Script for Inpaint Anything

set -e  # Exit on any error

echo "🚀 Starting model download for Inpaint Anything..."

# Create directories
echo "📁 Creating directories..."
mkdir -p pretrained_models
mkdir -p weights

# SAM Model Download
echo "🔍 Downloading SAM models..."

# SAM ViT-H (default)
if [ ! -f "pretrained_models/sam_vit_h_4b8939.pth" ]; then
    echo "📥 Downloading SAM ViT-H model..."
    wget -O pretrained_models/sam_vit_h_4b8939.pth \
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth"
    echo "✅ SAM ViT-H model downloaded"
else
    echo "✅ SAM ViT-H model already exists"
fi

# SAM ViT-L (optional, lighter)
if [ ! -f "pretrained_models/sam_vit_l_0b3195.pth" ]; then
    echo "📥 Downloading SAM ViT-L model..."
    wget -O pretrained_models/sam_vit_l_0b3195.pth \
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth"
    echo "✅ SAM ViT-L model downloaded"
else
    echo "✅ SAM ViT-L model already exists"
fi

# SAM ViT-B (optional, smallest)
if [ ! -f "pretrained_models/sam_vit_b_01ec64.pth" ]; then
    echo "📥 Downloading SAM ViT-B model..."
    wget -O pretrained_models/sam_vit_b_01ec64.pth \
        "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    echo "✅ SAM ViT-B model downloaded"
else
    echo "✅ SAM ViT-B model already exists"
fi

# Mobile SAM (lightweight alternative)
if [ ! -f "weights/mobile_sam.pt" ]; then
    echo "📥 Downloading Mobile SAM model..."
    wget -O weights/mobile_sam.pt \
        "https://github.com/ChaoningZhang/MobileSAM/blob/master/weights/mobile_sam.pt?raw=true"
    echo "✅ Mobile SAM model downloaded"
else
    echo "✅ Mobile SAM model already exists"
fi

# LaMa Model Download
echo "🎨 Setting up LaMa model..."

if [ ! -d "pretrained_models/big-lama" ]; then
    echo "📥 Downloading LaMa model..."
    mkdir -p pretrained_models/big-lama
    
    # Download from the official LaMa repository
    wget -O pretrained_models/big-lama.zip \
        "https://huggingface.co/smartywu/big-lama/resolve/main/big-lama.zip"
    
    # Extract
    cd pretrained_models
    unzip -q big-lama.zip
    rm big-lama.zip
    cd ..
    
    echo "✅ LaMa model downloaded and extracted"
else
    echo "✅ LaMa model already exists"
fi

# Verify downloads
echo "🔍 Verifying downloaded models..."

# Check SAM models
if [ -f "pretrained_models/sam_vit_h_4b8939.pth" ]; then
    size=$(du -h pretrained_models/sam_vit_h_4b8939.pth | cut -f1)
    echo "✅ SAM ViT-H: $size"
else
    echo "❌ SAM ViT-H model missing"
fi

if [ -f "pretrained_models/sam_vit_l_0b3195.pth" ]; then
    size=$(du -h pretrained_models/sam_vit_l_0b3195.pth | cut -f1)
    echo "✅ SAM ViT-L: $size"
fi

if [ -f "pretrained_models/sam_vit_b_01ec64.pth" ]; then
    size=$(du -h pretrained_models/sam_vit_b_01ec64.pth | cut -f1)
    echo "✅ SAM ViT-B: $size"
fi

if [ -f "weights/mobile_sam.pt" ]; then
    size=$(du -h weights/mobile_sam.pt | cut -f1)
    echo "✅ Mobile SAM: $size"
fi

# Check LaMa model
if [ -d "pretrained_models/big-lama" ]; then
    files=$(find pretrained_models/big-lama -name "*.pth" | wc -l)
    echo "✅ LaMa model: $files checkpoint files found"
else
    echo "❌ LaMa model directory missing"
fi

# Check LaMa config
if [ -f "lama/configs/prediction/default.yaml" ]; then
    echo "✅ LaMa config file exists"
else
    echo "❌ LaMa config file missing - check lama directory"
fi

echo ""
echo "📊 Download Summary:"
echo "==================="
total_size=$(du -sh pretrained_models weights 2>/dev/null | awk '{sum+=$1} END {print sum "GB"}' || echo "Unknown")
echo "Total model size: $total_size"
echo ""
echo "🎉 Model download completed!"
echo ""
echo "💡 Next steps:"
echo "1. Copy .env.example to .env if you haven't already"
echo "2. Run: ./scripts/start_dev.sh"
echo "3. Test the API at: http://localhost:8000/docs"