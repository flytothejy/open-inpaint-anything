# GPU 없는 환경에서의 테스트 가이드

## 🎯 현재 상황 (2025-07-12 20:50)

### ✅ 성공적으로 작동하는 것들:
- FastAPI 서버 구동 (CPU 모드)
- SAM ViT-B 모델 로딩 
- 헬스체크 API
- NumPy 호환성 문제 해결
- CPU 최적화 설정 (8 스레드)

### ⚠️ 부분적으로 작동하는 것들:
- 서버 응답은 되지만 모델 로딩이 완전하지 않음
- SAM은 로딩되었지만 LaMa와 Stable Diffusion은 아직 문제

## 🛠️ CPU 환경 최적화 전략

### 1. 경량 모델 사용
```bash
# 현재 설정 (이미 적용됨)
SAM_MODEL_TYPE=vit_b  # 가장 작은 SAM 모델 (350MB)
# 대신 Mobile SAM 사용 고려 (40MB)
```

### 2. 메모리 최적화
```bash
# .env 파일에 추가할 설정들
PYTORCH_CPU_ALLOC_CONF=max_split_size_mb:128
OMP_NUM_THREADS=8
TORCH_NUM_THREADS=8
```

### 3. 단계별 테스트 전략

#### Phase 1: SAM만 먼저 테스트
- Mock 서비스에서 SAM만 실제 모델로 교체
- 간단한 세그멘테이션 테스트

#### Phase 2: LaMa 설정 수정
- 설정 파일 경로 확인 및 수정
- CPU 전용 LaMa 설정

#### Phase 3: Stable Diffusion 대체
- 경량 모델 사용 또는 Mock 유지
- CPU에서는 너무 느려서 현실적이지 않음

## 🔧 즉시 적용 가능한 개선사항

### 1. Mobile SAM 사용
```bash
# Mobile SAM은 40MB로 훨씬 가벼움
SAM_MODEL_TYPE=mobile_sam
SAM_CHECKPOINT_PATH=./weights/mobile_sam.pt
```

### 2. 하이브리드 모드 구현
- SAM: 실제 모델 (CPU에서도 괜찮음)
- LaMa: 실제 모델 (CPU에서 가능)  
- Stable Diffusion: Mock 서비스 (CPU에서 너무 느림)

### 3. Progressive Loading
- 서버 시작 시 모든 모델을 동시에 로딩하지 않고
- 요청이 있을 때 필요한 모델만 로딩

## 🚀 현실적 테스트 방법

### Option 1: 부분 실제 + 부분 Mock
```python
# CPU에서 현실적인 설정
USE_REAL_SAM=true          # SAM은 CPU에서도 괜찮음
USE_REAL_LAMA=true         # LaMa도 CPU에서 가능
USE_MOCK_SD=true           # SD만 Mock으로
```

### Option 2: 클라우드 서비스 활용
- Google Colab (무료 GPU)
- Kaggle Notebooks (무료 GPU)
- GitHub Codespaces (유료)
- AWS/GCP 무료 티어

### Option 3: 로컬 CPU 최적화
- 이미지 크기 제한 (512x512 이하)
- 배치 크기 1로 제한
- 추론 스텝 수 감소

## 📋 다음 단계 우선순위

### High Priority (지금 당장 가능)
1. **Mobile SAM으로 교체** - 즉시 성능 향상
2. **LaMa 설정 수정** - 누락된 키 문제 해결
3. **하이브리드 모드 구현** - 현실적 조합

### Medium Priority (시간 투자 필요)
1. **클라우드 환경 설정** - 실제 GPU 테스트
2. **Progressive Loading** - 성능 최적화
3. **이미지 크기 제한** - CPU 부하 감소

### Low Priority (나중에)
1. **Docker 컨테이너** - 배포 환경
2. **분산 처리** - 복잡한 최적화

## 🎯 추천 방향

현재 상황에서는 **Option 1 (부분 실제 + 부분 Mock)** 이 가장 현실적입니다:

1. **SAM**: 실제 모델 (Mobile SAM 사용)
2. **LaMa**: 실제 모델 (설정 수정 후)
3. **Stable Diffusion**: Mock 서비스 유지

이렇게 하면 API 구조와 실제 AI 처리 파이프라인을 모두 테스트할 수 있으면서도 CPU 환경에서 현실적인 성능을 얻을 수 있습니다.

## 💡 클라우드 GPU 옵션

### 무료 옵션:
- **Google Colab**: 무료 GPU (T4), 12시간 제한
- **Kaggle**: 무료 GPU (P100), 30시간/주
- **Paperspace Gradient**: 무료 GPU (M4000), 제한적

### 유료 옵션:
- **RunPod**: $0.2-0.5/시간
- **Vast.ai**: $0.1-0.3/시간  
- **Lambda Labs**: $0.5-1.0/시간

실제 프로덕션 테스트를 위해서는 클라우드 GPU를 추천하지만, 개발과 API 테스트는 현재 CPU 환경에서도 충분히 가능합니다.