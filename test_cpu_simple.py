#!/usr/bin/env python3
"""
Simple CPU test for basic functionality
"""

import requests
import json
import base64
import time
from PIL import Image
import io
import numpy as np

# Test configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_IMAGE_SIZE = (200, 150)  # Smaller for CPU testing

def create_simple_test_image():
    """Create a very simple test image"""
    # Create RGB image with simple pattern
    img = np.zeros((*TEST_IMAGE_SIZE[::-1], 3), dtype=np.uint8)
    
    # Add a simple red square in the center
    h, w = img.shape[:2]
    center_h, center_w = h // 2, w // 2
    size = 30
    
    img[center_h-size:center_h+size, center_w-size:center_w+size] = [255, 0, 0]  # Red square
    img[10:40, 10:40] = [0, 255, 0]  # Green square (top-left)
    img[h-40:h-10, w-40:w-10] = [0, 0, 255]  # Blue square (bottom-right)
    
    # Convert to PIL and then base64
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    buffer.seek(0)
    
    b64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_string}"

def test_health_endpoint():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Device: {result.get('device', 'unknown')}")
            
            models = result.get('models_loaded', {})
            print(f"   Models loaded:")
            for model, loaded in models.items():
                status = "✅" if loaded else "❌"
                print(f"     {model}: {status}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_cpu_performance():
    """Test basic CPU performance with simple operations"""
    print("\n⚡ Testing CPU Performance...")
    
    # Test simple remove operation (should work even if models fail)
    try:
        image_data = create_simple_test_image()
        
        # Very simple request
        payload = {
            "image_data": image_data,
            "point_coords": [[100, 75]],  # Center of 200x150 image
            "point_labels": [1],
            "dilate_kernel_size": 5
        }
        
        print(f"   Sending request to /remove...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/remove",
            json=payload,
            timeout=60  # Longer timeout for CPU
        )
        
        duration = time.time() - start_time
        print(f"   Response time: {duration:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Remove operation successful")
            print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"   Result image size: {len(result.get('result_image', ''))} chars")
            return True
        else:
            print(f"❌ Remove operation failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ CPU performance test error: {e}")
        return False

def main():
    """Main test function"""
    print("🖥️  CPU Testing for Inpaint Anything API")
    print("=" * 50)
    print(f"API Base: {API_BASE}")
    print(f"Test Image Size: {TEST_IMAGE_SIZE}")
    print()
    
    # Wait a moment for server
    print("⏳ Waiting for server...")
    time.sleep(3)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("CPU Performance", test_cpu_performance),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All CPU tests passed!")
    elif passed > 0:
        print("⚠️  Partial success - some functionality working")
    else:
        print("❌ All tests failed - check server logs")
    
    return passed > 0

if __name__ == "__main__":
    main()