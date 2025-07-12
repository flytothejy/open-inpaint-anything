#!/usr/bin/env python3
"""
Simple API test script for Inpaint Anything FastAPI server
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
TEST_IMAGE_SIZE = (300, 200)

def create_test_image():
    """Create a simple test image"""
    # Create a gradient image
    img = np.zeros((*TEST_IMAGE_SIZE[::-1], 3), dtype=np.uint8)
    
    # Add some patterns
    for i in range(TEST_IMAGE_SIZE[1]):
        for j in range(TEST_IMAGE_SIZE[0]):
            img[i, j] = [
                int(255 * i / TEST_IMAGE_SIZE[1]),  # Red gradient
                int(255 * j / TEST_IMAGE_SIZE[0]),  # Green gradient
                128  # Blue constant
            ]
    
    # Convert to PIL Image
    pil_img = Image.fromarray(img)
    
    # Convert to base64
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    buffer.seek(0)
    
    b64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_string}"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_remove_api():
    """Test remove object API"""
    print("\nTesting /remove endpoint...")
    try:
        # Create test data
        image_data = create_test_image()
        
        payload = {
            "image_data": image_data,
            "point_coords": [[100, 100], [150, 120]],
            "point_labels": [1, 1],
            "dilate_kernel_size": 15
        }
        
        response = requests.post(
            f"{API_BASE}/remove",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"Result image length: {len(result['result_image'])}")
            print(f"Mask image length: {len(result['mask_image'])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_fill_api():
    """Test fill object API"""
    print("\nTesting /fill endpoint...")
    try:
        # Create test data
        image_data = create_test_image()
        
        payload = {
            "image_data": image_data,
            "point_coords": [[100, 100]],
            "point_labels": [1],
            "text_prompt": "beautiful red flower",
            "dilate_kernel_size": 10
        }
        
        response = requests.post(
            f"{API_BASE}/fill",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"Result image length: {len(result['result_image'])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_replace_api():
    """Test replace object API"""
    print("\nTesting /replace endpoint...")
    try:
        # Create test data
        image_data = create_test_image()
        
        payload = {
            "image_data": image_data,
            "point_coords": [[150, 100]],
            "point_labels": [1],
            "text_prompt": "sunset ocean background",
            "num_inference_steps": 20
        }
        
        response = requests.post(
            f"{API_BASE}/replace",
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"Result image length: {len(result['result_image'])}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Inpaint Anything API Test")
    print("=" * 50)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Remove Object", test_remove_api()))
    results.append(("Fill Object", test_fill_api()))
    results.append(("Replace Object", test_replace_api()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs.")
    
    return passed == len(results)

if __name__ == "__main__":
    main()