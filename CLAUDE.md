# Claude Code 작업 지침서

> **이 파일은 Claude Code가 프로젝트 컨텍스트를 빠르게 파악하기 위한 지침서입니다.**

## 🎯 프로젝트 핵심 정보

### 프로젝트 목표
오픈소스 Inpaint-Anything 모델을 FastAPI로 서빙하는 웹 API 서버 구축

### 현재 브랜치
- **Main**: `main`
- **Working**: `api-implement`

### 환경 설정
- **Python**: 3.10.12 (venv 사용)
- **Virtual Environment**: `./venv`
- **Environment File**: `.env` (from `.env.example`)
- **Current Mode**: Mock Service (USE_MOCK_SERVICE=true)

## 📋 필수 읽을 파일들

### 1차 우선순위 (세션 시작 시 필수)
1. **`PROJECT_PROGRESS.md`** - 전체 진행상황과 타임라인
2. **`claude_code_instructions.md`** - 원본 프로젝트 지시서
3. **`.env`** - 현재 환경 설정

### 2차 우선순위 (작업 전 참고)
1. **`api/main.py`** - FastAPI 메인 앱
2. **`config/settings.py`** - 설정 관리
3. **Current git status** - `git status && git branch`

## 🚀 빠른 시작 가이드

### 1. 환경 체크
```bash
# 현재 위치 확인
pwd  # /home/jiyong/github/Inpaint-Anything

# Git 상태 확인
git status && git branch

# 가상환경 활성화
source venv/bin/activate

# 현재 설정 확인
cat .env | grep USE_MOCK_SERVICE
```

### 2. 서버 실행 테스트
```bash
# 통합 테스트 (추천)
./scripts/test_with_server.sh

# 또는 개별 실행
timeout 10s ./scripts/start_dev.sh

# API 테스트
python test_cpu_simple.py    # CPU 전용 테스트 (추천)
python test_api.py           # 원본 테스트
```

### 3. 주요 명령어
```bash
# 모델 검증
python scripts/verify_models.py

# 개발 서버 시작
./scripts/start_dev.sh

# 모델 다운로드 (필요시)
./scripts/download_models.sh
```

## 🗂️ 프로젝트 구조 요약

```
/home/jiyong/github/Inpaint-Anything/
├── api/                    # FastAPI 애플리케이션
│   ├── main.py            # 메인 앱
│   ├── routes/            # API 엔드포인트
│   ├── services/          # 비즈니스 로직 (+ mock_inpaint_service.py)
│   ├── models/            # Pydantic 모델
│   └── middleware/        # CORS, 로깅
├── config/                # 설정 관리
├── utils/                 # 유틸리티 (exceptions, image_utils)
├── scripts/               # 실행 스크립트
├── pretrained_models/     # 다운로드된 AI 모델들
├── requirements/          # 의존성 파일
├── PROJECT_PROGRESS.md    # 📋 진행상황 문서
├── CLAUDE.md             # 📖 이 파일
└── test_api.py           # API 테스트
```

## ⚠️ 현재 상황 및 이슈

### 현재 상태 (2025-07-12 20:55)
- ✅ FastAPI 서버 구현 완료
- ✅ 모든 AI 모델 다운로드 완료  
- ✅ NumPy 호환성 문제 해결 (1.24.4로 다운그레이드)
- ✅ SAM 모델 CPU에서 로딩 성공 (ViT-B)
- ✅ CPU 최적화 설정 적용 (8 스레드)
- ✅ 통합 테스트 환경 구축

### 주요 이슈
1. **LaMa 모델 설정**: `training_model` 키 누락 문제
2. **Stable Diffusion**: CPU에서 로딩 느림 (실용성 낮음)
3. **API 요청 형식**: 일부 테스트에서 요청 파라미터 문제

### 해결 완료
1. ✅ NumPy 2.0 호환성 문제 해결
2. ✅ CPU 환경 최적화 완료
3. ✅ 실제 모델 (SAM) 로딩 성공

## 🔧 작업 패턴

### 세션 시작 시
1. `PROJECT_PROGRESS.md` 읽고 마지막 상황 파악
2. Git 상태 확인 및 브랜치 체크
3. 가상환경 활성화
4. 간단한 서버 테스트로 현재 상태 확인

### 작업 중
1. 각 단계마다 작업 내용을 `PROJECT_PROGRESS.md`에 기록
2. 중요한 변경사항은 즉시 문서화
3. 새로운 이슈 발견 시 문서에 추가

### 세션 종료 시
1. `PROJECT_PROGRESS.md` 업데이트
2. Git commit으로 변경사항 저장
3. 다음 세션 작업 계획 문서에 기록

## 📡 API 엔드포인트

### 기본 정보
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api/v1`
- **Documentation**: `/docs` (Swagger UI)

### 주요 엔드포인트
- `GET /api/v1/health` - 서비스 상태
- `POST /api/v1/remove` - 객체 제거
- `POST /api/v1/fill` - 영역 채우기 (텍스트 프롬프트)
- `POST /api/v1/replace` - 객체 교체

## 🎯 다음 단계 우선순위

### High Priority
1. **LaMa 모델 설정 수정** - `training_model` 키 문제
2. **Mobile SAM 적용** - 성능 향상 (40MB)
3. **하이브리드 모드** - 실제 SAM+LaMa + Mock SD

### Medium Priority  
1. **API 요청 형식 개선** - 파일 업로드 지원
2. **클라우드 GPU 테스트** - Google Colab/Kaggle
3. **Docker 컨테이너화** - CPU/GPU 버전

### Low Priority
1. **프론트엔드 구현**
2. **성능 최적화** - 배치 처리
3. **배포 자동화** - CI/CD

---

**이 문서는 Claude Code의 효율적인 작업을 위한 빠른 참조용입니다.**  
**상세한 진행상황은 `PROJECT_PROGRESS.md`를 참조하세요.**