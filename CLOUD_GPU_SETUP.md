# 클라우드 GPU 환경 설정 가이드

## 🎯 목표
로컬 CPU 환경에서 개발한 FastAPI 서버를 클라우드 GPU 환경에서 테스트하여 실제 AI 모델의 성능을 검증합니다.

## 🌟 추천 플랫폼: Google Colab

### 장점:
- 무료 Tesla T4 GPU (16GB VRAM)
- Jupyter 환경으로 쉬운 테스트
- GitHub 연동 간편
- 웹 인터페이스로 접근 편리

### 제한사항:
- 12시간 연속 사용 제한
- 세션 종료 시 데이터 손실
- 고정 IP 없음

## 📋 Colab 설정 단계

### 1. 환경 준비
```python
# GPU 확인
!nvidia-smi

# 프로젝트 클론
!git clone https://github.com/your-username/Inpaint-Anything.git
%cd Inpaint-Anything

# Python 환경 확인
!python --version
!which python
```

### 2. 의존성 설치
```python
# 기본 의존성 설치
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
!pip install fastapi uvicorn python-multipart
!pip install diffusers transformers accelerate
!pip install "numpy==1.24.4" "opencv-python==4.9.0.80"
!pip install pydantic-settings aiofiles pillow omegaconf

# Segment Anything 설치
!pip install git+https://github.com/facebookresearch/segment-anything.git
```

### 3. 모델 다운로드
```python
# 모델 다운로드 스크립트 실행
!chmod +x scripts/download_models.sh
!./scripts/download_models.sh
```

### 4. GPU 전용 설정
```python
# .env 파일 수정
env_content = '''
# Model Configuration (GPU optimized)
SAM_MODEL_TYPE=vit_h
SAM_CHECKPOINT_PATH=./pretrained_models/sam_vit_h_4b8939.pth
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

# Mock Service (disabled for GPU testing)
USE_MOCK_SERVICE=false
'''

with open('.env', 'w') as f:
    f.write(env_content)
```

### 5. 서버 시작 및 테스트
```python
# 백그라운드에서 서버 시작
import subprocess
import time
import requests
import threading

# 서버 시작 함수
def start_server():
    subprocess.run(['python', '-m', 'uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000'])

# 백그라운드 스레드로 서버 시작
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# 서버 시작 대기
time.sleep(30)

# 헬스체크
response = requests.get('http://localhost:8000/api/v1/health')
print(f"Health check: {response.status_code}")
print(response.json())
```

## 🔧 Colab용 최적화 설정

### 1. 메모리 최적화
```python
# GPU 메모리 최적화
import torch
torch.cuda.empty_cache()

# Mixed precision 사용
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
```

### 2. 빠른 테스트를 위한 경량 설정
```python
# 빠른 테스트용 설정
test_env = '''
SAM_MODEL_TYPE=vit_b
MAX_IMAGE_SIZE=512
USE_MOCK_SERVICE=false
'''
```

### 3. ngrok을 통한 외부 접근 (선택사항)
```python
# ngrok 설치 및 설정
!pip install pyngrok
from pyngrok import ngrok

# 터널 생성
public_url = ngrok.connect(8000)
print(f"Public URL: {public_url}")
```

## 📊 성능 벤치마크 테스트

### 1. 모델 로딩 시간 측정
```python
import time

start_time = time.time()
# 모델 로딩 코드
end_time = time.time()

print(f"Model loading time: {end_time - start_time:.2f} seconds")
```

### 2. API 응답 시간 테스트
```python
import requests
import base64
import time
from PIL import Image
import io
import numpy as np

# 테스트 이미지 생성
def create_test_image():
    img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# API 테스트
test_data = {
    "image_data": f"data:image/png;base64,{create_test_image()}",
    "point_coords": [[256, 256]],
    "point_labels": [1],
    "dilate_kernel_size": 15
}

start_time = time.time()
response = requests.post('http://localhost:8000/api/v1/remove', json=test_data)
end_time = time.time()

print(f"API response time: {end_time - start_time:.2f} seconds")
print(f"Status: {response.status_code}")
```

## 🔄 Kaggle Notebooks 대안

### 장점:
- 더 많은 무료 시간 (30시간/주)
- 데이터셋 영구 저장
- 더 강력한 GPU (P100)

### 설정 방법:
```python
# Kaggle에서 실행
import kaggle
import zipfile
import os

# 데이터셋 업로드 및 다운로드
# (사전에 프로젝트를 Kaggle 데이터셋으로 업로드 필요)
```

## 🚀 RunPod 등 유료 옵션

### 비용 효율적인 GPU 클라우드
- **RunPod**: $0.2-0.5/시간
- **Vast.ai**: $0.1-0.3/시간
- **Lambda Labs**: $0.5-1.0/시간

### 장점:
- 더 강력한 GPU (RTX 4090, A100 등)
- 고정 IP 및 SSH 접근
- 더 긴 세션 시간
- 루트 권한

## 📋 테스트 체크리스트

### Phase 1: 환경 설정 (30분)
- [ ] GPU 확인
- [ ] 프로젝트 클론
- [ ] 의존성 설치
- [ ] 모델 다운로드

### Phase 2: 기본 테스트 (30분)
- [ ] 서버 시작
- [ ] 헬스체크 API
- [ ] 모델 로딩 확인

### Phase 3: 성능 테스트 (60분)
- [ ] 각 API 엔드포인트 테스트
- [ ] 응답 시간 측정
- [ ] 메모리 사용량 모니터링
- [ ] 다양한 이미지 크기 테스트

### Phase 4: 비교 분석 (30분)
- [ ] CPU vs GPU 성능 비교
- [ ] 모델별 성능 차이 분석
- [ ] 최적 설정 도출

## 💡 추천 워크플로우

1. **Google Colab 시작** (무료, 빠른 설정)
2. **기본 기능 검증** (모든 모델 로딩 및 API 테스트)
3. **성능 벤치마크** (응답 시간, 품질 평가)
4. **필요시 유료 플랫폼** (더 긴 테스트나 실제 배포)

## ⚠️ 주의사항

- **세션 유지**: Colab은 90분 비활성 시 종료
- **데이터 백업**: 중요한 결과는 Google Drive에 저장
- **비용 관리**: 유료 플랫폼 사용 시 자동 종료 설정
- **보안**: API 키나 민감한 정보 노출 주의

이 가이드를 따라하면 GPU 환경에서 완전한 기능 테스트를 수행할 수 있습니다!