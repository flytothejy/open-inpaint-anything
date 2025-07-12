# Claude Code 작업 지시서: Inpaint Anything FastAPI 구현

## 프로젝트 개요
오픈소스 Inpaint-Anything 모델을 FastAPI로 서빙하는 웹 API 서버를 구축합니다.

## 현재 상황
- ✅ private GitHub repository 생성 완료
- ✅ venv 환경 설정 완료
- ✅ 기본 의존성 설치 완료 (torch, segment_anything, lama 등)
- ✅ FastAPI 관련 패키지 설치 완료

## 작업 목표
FastAPI 기반 AI 모델 서빙 API 서버 구현

## 프로젝트 구조

```
your-inpaint-project/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── inpaint.py       # Inpaint 엔드포인트
│   │   └── health.py        # 헬스체크
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py      # Pydantic 모델
│   │   └── responses.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── inpaint_service.py
│   │   └── model_loader.py
│   └── middleware/
│       ├── __init__.py
│       ├── cors.py
│       └── logging.py
├── config/
│   ├── __init__.py
│   └── settings.py          # 설정 관리
├── utils/
│   ├── __init__.py
│   ├── image_utils.py
│   └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
├── scripts/
│   ├── download_models.sh
│   └── start_dev.sh
├── .env.example
└── requirements/
    ├── base.txt
    ├── dev.txt
    └── prod.txt
```

## 구체적 작업 지시사항

### 1단계: 프로젝트 구조 생성
```bash
# 디렉토리 구조 생성
mkdir -p {api,config,utils,tests,docker,scripts}
mkdir -p api/{routes,models,services,middleware}
mkdir -p requirements
```

### 2단계: 핵심 파일 구현

#### A. 설정 관리 (config/settings.py)
- Pydantic BaseSettings 사용
- 환경별 설정 분리 (dev/prod)
- 모델 경로, API 설정, 파일 처리 설정 포함
- 환경 변수 지원

**주요 설정 항목:**
- SAM_MODEL_TYPE, SAM_CHECKPOINT
- LAMA_CONFIG, LAMA_CHECKPOINT  
- MAX_IMAGE_SIZE, MAX_FILE_SIZE
- CORS, Redis 설정

#### B. 예외 처리 (utils/exceptions.py)
- 커스텀 예외 클래스 정의
- ModelNotLoadedException
- InvalidImageException
- ProcessingTimeoutException

#### C. 이미지 처리 유틸리티 (utils/image_utils.py)
- 비동기 Base64 이미지 디코딩/인코딩
- 이미지 크기 조정 및 검증
- 파일 업로드 처리

#### D. Pydantic 모델 (api/models/)
**requests.py:**
- InpaintRequest, RemoveRequest, FillRequest, ReplaceRequest
- 좌표 검증, 텍스트 프롬프트 검증 포함

**responses.py:**
- BaseResponse, InpaintResponse, ErrorResponse, HealthResponse
- 타임스탬프, 메타데이터 포함

#### E. 모델 로더 서비스 (api/services/model_loader.py)
- 비동기 모델 로딩
- SAM 모델과 LaMa 모델 관리
- GPU/CPU 자동 감지
- 싱글톤 패턴으로 전역 인스턴스 관리

#### F. Inpaint 서비스 (api/services/inpaint_service.py)
- remove_object, fill_object, replace_background 메서드
- 비동기 처리 (CPU 집약적 작업은 executor 사용)
- 좌표 검증 및 에러 처리

#### G. API 라우트 (api/routes/)
**health.py:**
- /health, /ready 엔드포인트
- GPU 상태, 메모리 사용량, 모델 로딩 상태 체크

**inpaint.py:**
- POST /remove, /fill, /replace 엔드포인트
- 파일 업로드 처리 (multipart/form-data)
- 에러 핸들링 및 응답 포맷팅

#### H. 메인 애플리케이션 (api/main.py)
- FastAPI 앱 생성 및 설정
- CORS 미들웨어 설정
- lifespan 이벤트로 모델 로딩
- 라우터 등록 및 예외 핸들러

### 3단계: Requirements 파일 정리

#### requirements/base.txt
```
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
transformers>=4.20.0
diffusers>=0.15.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
pillow>=9.0.0
opencv-python-headless>=4.6.0
numpy>=1.21.0
```

#### requirements/dev.txt
```
-r base.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
black>=22.0.0
flake8>=4.0.0
jupyter>=1.0.0
```

#### requirements/prod.txt
```
-r base.txt
gunicorn>=21.0.0
redis>=4.0.0
prometheus-client>=0.17.0
structlog>=23.0.0
psutil>=5.9.0
```

### 4단계: 환경 설정 파일

#### .env.example
```
# Model Configuration
SAM_MODEL_TYPE=vit_h
SAM_CHECKPOINT_PATH=./pretrained_models/sam_vit_h_4b8939.pth
LAMA_CONFIG_PATH=./lama/configs/prediction/default.yaml
LAMA_CHECKPOINT_PATH=./pretrained_models/big-lama

# API Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
MAX_IMAGE_SIZE=2048
MAX_FILE_SIZE=10485760

# CORS
ALLOWED_ORIGINS=["*"]

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 5단계: 테스트 파일 작성

#### tests/test_api.py
- FastAPI TestClient 사용
- 각 엔드포인트 테스트
- 파일 업로드 테스트

#### tests/conftest.py
- pytest 설정 및 fixture

### 6단계: 실행 스크립트

#### scripts/start_dev.sh
```bash
#!/bin/bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### scripts/download_models.sh
- SAM 모델 다운로드
- LaMa 모델 다운로드
- pretrained_models 디렉토리 생성

### 7단계: Docker 설정

#### docker/Dockerfile
- PyTorch GPU 베이스 이미지
- 의존성 설치
- 모델 다운로드
- 비root 사용자 설정

#### docker/docker-compose.yml
- API 서버
- Redis 서비스  
- Nginx (선택)
- GPU 지원 설정

#### docker/.dockerignore
- venv, __pycache__, .git 등 제외

## GPU 없는 환경 고려사항

### 로컬 개발 설정
- CPU 모드 자동 감지 및 설정
- 가벼운 모델 사용 (vit_b 대신 vit_h)
- Mock 서비스 구현으로 API 테스트 가능
- 실제 모델 통합은 클라우드에서 진행

### Mock 서비스 구현
```python
# api/services/mock_inpaint_service.py 생성
# 실제 AI 모델 없이도 API 테스트 가능하도록
```

### 환경별 서비스 선택
```python
# settings.py에서 환경에 따라 서비스 선택
USE_MOCK_SERVICE = not torch.cuda.is_available()
```

## 중요한 구현 포인트

### 1. 비동기 처리
- 모델 추론은 CPU 집약적 → `asyncio.get_event_loop().run_in_executor()` 사용
- 파일 I/O는 aiofiles 사용

### 2. 에러 핸들링
- 커스텀 예외를 HTTP 예외로 변환
- 상세한 에러 메시지와 코드 제공

### 3. 성능 최적화
- 모델은 전역 변수로 한 번만 로딩
- 이미지 크기 제한 및 압축

### 4. 보안
- 파일 크기 제한
- 이미지 포맷 검증
- CORS 설정

### 5. 모니터링
- 헬스체크 엔드포인트
- 처리 시간 로깅
- 메모리 사용량 모니터링

## 테스트 방법

### 로컬 실행
```bash
# 개발 서버 실행
uvicorn api.main:app --reload

# 또는 스크립트 사용
./scripts/start_dev.sh
```

### API 테스트
```bash
# 헬스체크
curl http://localhost:8000/api/v1/health

# 객체 제거 테스트
curl -X POST http://localhost:8000/api/v1/remove \
  -F "image=@test_image.jpg" \
  -F 'request={"point_coords": [100, 200], "dilate_kernel_size": 15}'
```

### 자동 API 문서
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## 다음 단계 (Claude Code 작업 완료 후)
1. 실제 모델 integration (SAM, LaMa, Stable Diffusion)
2. 성능 최적화 및 배치 처리
3. 클라우드 배포 설정
4. 프론트엔드 웹 인터페이스 구현

## 주의사항
- 모든 파일에 적절한 타입 힌트 사용
- docstring 작성
- 에러 로깅 포함
- 코드 포맷팅 (black, flake8 준수)
- requirements.txt 버전 명시

이 지시서에 따라 체계적으로 FastAPI 서버를 구현해주세요.