# 🚀 Google Colab 빠른 시작 가이드

## 📋 단계별 실행 방법

### 1. Google Colab 준비
1. [Google Colab](https://colab.research.google.com) 접속
2. 새 노트북 생성
3. **런타임 → 런타임 유형 변경 → GPU** 선택

### 2. 자동 설정 실행 (한 번에 완료)
새 셀에 아래 코드를 복사하여 실행하세요:

```python
# Colab용 Inpaint Anything 자동 설정 스크립트
!wget -q https://raw.githubusercontent.com/hllj/Inpaint-Anything/api-implement/colab_setup.py
!python colab_setup.py
```

### 3. 수동 설정 (위 자동 설정이 실패할 경우)

#### 3.1 GPU 확인
```python
!nvidia-smi
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
```

#### 3.2 프로젝트 설정
```python
# 프로젝트 클론
!git clone https://github.com/hllj/Inpaint-Anything.git
%cd Inpaint-Anything

# 의존성 설치
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install fastapi uvicorn python-multipart aiofiles
!pip install diffusers transformers accelerate
!pip install "numpy==1.24.4" "opencv-python==4.9.0.80"
!pip install pydantic-settings pillow omegaconf
!pip install git+https://github.com/facebookresearch/segment-anything.git
```

#### 3.3 Colab 전용 환경 설정
```python
# .env 파일 생성
env_content = '''# Model Configuration (GPU optimized for Colab)
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
'''

with open('.env', 'w') as f:
    f.write(env_content)

print("✅ Environment configuration created")
```

#### 3.4 모델 다운로드
```python
# 모델 다운로드 스크립트 실행
!chmod +x scripts/download_models.sh
!./scripts/download_models.sh
```

#### 3.5 서버 시작 및 테스트
```python
# 백그라운드에서 서버 시작
import subprocess
import time
import requests
import threading
import sys

def start_server():
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])

# 서버 시작
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# 서버 시작 대기
print("⏳ Waiting for server to start...")
time.sleep(20)

# 헬스체크
try:
    response = requests.get('http://localhost:8000/api/v1/health', timeout=10)
    print(f"✅ Health check: {response.status_code}")
    print(response.json())
except Exception as e:
    print(f"❌ Health check failed: {e}")
```

### 4. API 테스트
```python
# 간단한 API 테스트
import requests
import base64
import numpy as np
from PIL import Image
import io

# 테스트 이미지 생성
def create_test_image():
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# API 테스트 요청
test_data = {
    "image_data": f"data:image/png;base64,{create_test_image()}",
    "point_coords": [[256, 256]],
    "point_labels": [1],
    "dilate_kernel_size": 15
}

start_time = time.time()
response = requests.post('http://localhost:8000/api/v1/remove', json=test_data)
end_time = time.time()

print(f"🚀 API response time: {end_time - start_time:.2f} seconds")
print(f"📊 Status: {response.status_code}")

if response.status_code == 200:
    print("✅ API test successful!")
    result = response.json()
    print(f"📏 Result image size: {len(result.get('result_image', ''))} characters")
else:
    print(f"❌ API test failed: {response.text}")
```

### 5. 외부 접근 설정 (선택사항)
```python
# ngrok 설치 및 설정
!pip install pyngrok
from pyngrok import ngrok

# 터널 생성 (ngrok 계정 필요)
public_url = ngrok.connect(8000)
print(f"🌐 Public URL: {public_url}")
print(f"📖 API Documentation: {public_url}/docs")
```

## 📊 성능 벤치마크

### GPU vs CPU 성능 비교
```python
import time

# SAM 세그멘테이션 성능 측정
def benchmark_sam():
    start_time = time.time()
    # SAM 처리 코드 (위의 API 테스트 재사용)
    response = requests.post('http://localhost:8000/api/v1/remove', json=test_data)
    end_time = time.time()
    
    return end_time - start_time, response.status_code

# 5회 테스트 평균
times = []
for i in range(5):
    elapsed, status = benchmark_sam()
    if status == 200:
        times.append(elapsed)
    print(f"Test {i+1}: {elapsed:.2f}s (Status: {status})")

if times:
    avg_time = sum(times) / len(times)
    print(f"\n📊 Average response time: {avg_time:.2f}s")
    print(f"🔥 GPU acceleration working!")
else:
    print("❌ All tests failed")
```

## 🔧 문제 해결

### 메모리 부족 에러
```python
# GPU 메모리 정리
import torch
torch.cuda.empty_cache()

# 메모리 사용량 확인
!nvidia-smi
```

### 모델 로딩 실패
```python
# 모델 파일 확인
!ls -la pretrained_models/
!du -sh pretrained_models/*
```

### 서버 시작 실패
```python
# 로그 확인
!tail -20 server.log

# 포트 사용 확인
!netstat -tlnp | grep :8000
```

## 📋 체크리스트

### 설정 완료 확인
- [ ] GPU 활성화 확인 (`nvidia-smi` 성공)
- [ ] 프로젝트 클론 완료
- [ ] 의존성 설치 완료 (특히 NumPy 1.24.4)
- [ ] 모델 다운로드 완료 (SAM, LaMa)
- [ ] 환경 설정 파일 (.env) 생성
- [ ] 서버 시작 성공
- [ ] 헬스체크 API 응답 확인

### 기능 테스트 완료
- [ ] `/api/v1/health` 엔드포인트
- [ ] `/api/v1/remove` 객체 제거 API
- [ ] `/api/v1/fill` 영역 채우기 API
- [ ] `/api/v1/replace` 객체 교체 API

### 성능 측정 완료
- [ ] API 응답 시간 측정
- [ ] GPU 메모리 사용량 확인
- [ ] CPU vs GPU 성능 비교

## 🎯 예상 결과

### GPU 환경에서 기대되는 성능:
- **SAM 세그멘테이션**: 2-5초
- **LaMa 인페인팅**: 3-8초
- **Stable Diffusion**: 10-30초

### CPU 대비 성능 향상:
- **SAM**: 5-10배 빠름
- **전체 파이프라인**: 10-20배 빠름

## 📞 문제 발생 시

1. **자동 설정 스크립트 사용**: `colab_setup.py` 실행
2. **단계별 수동 설정**: 위의 3번 항목 참조
3. **로그 확인**: 서버 로그와 에러 메시지 분석
4. **메모리 정리**: `torch.cuda.empty_cache()` 실행

이 가이드를 따라하면 Google Colab에서 완전한 GPU 가속 Inpaint Anything API를 테스트할 수 있습니다!