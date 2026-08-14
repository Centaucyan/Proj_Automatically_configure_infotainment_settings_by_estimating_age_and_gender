# 🚀 On-Device 연령/성별 추정 기반 인포테인먼트 자동 제어 시스템 개발 로드맵

## 1. 프로젝트 개요 (Project Overview)
* **프로젝트명:** On-Device 연령/성별 추정 기반 인포테인먼트 자동 제어 시스템
* **목적:** 차량 내부 카메라(DMS/ADAS)를 활용해 탑승자의 얼굴을 인식하고 연령/성별을 추론하여, 고령 운전자 등 탑승자 맞춤형 인포테인먼트 환경(안내 볼륨, 안내 속도, 화면 밝기)을 자동으로 설정하고 변경 내역을 음성으로 안내함.
* **현재 개발 및 테스트 환경 (Environment Constraints):**
  1. **영상 입력 (Video Input):** 추후 USB 카메라가 설치될 예정이나, 현재 기능 개발 및 검증 단계에서는 준비된 **동영상 파일(`videos/test_1.mp4` ~ `test_8.mp4`)을 입력 스트림으로 활용**함. (USB 카메라 연동으로 쉽게 전환 가능하도록 입력 모듈 추상화)
  2. **제어 대상 (Target Device):** 차량 인포테인먼트 장치가 아직 확정되지 않았으므로, 현재 **개발 PC(Linux/Ubuntu)의 실제 스피커 볼륨, 화면 밝기 제어 API/명령어 및 PC 스피커 TTS 음성 안내로 직접 연동**함. (추후 차량 CAN/Ethernet/REST API 연동 인터페이스 구조 적용)
* **관련 명세서:** `documents/SCN-ADAS-INFO-001.md` (23단계 정상 동작 시나리오)

---

## 2. 개발 방법론 및 핵심 아키텍처 (Development Methodology)

### 2.1. 모듈화 및 레이어드 아키텍처 (Layered Architecture)
기존 탐색적 코드(`test_from_video.ipynb`)를 독립적이고 재사용 가능한 모듈형 파이썬 패키지(`src/`) 구조로 재설계합니다.

```
Proj_Automatically_configure_infotainment_settings_by_estimating_age_and_gender/
├── documents/
│   ├── SCN-ADAS-INFO-001.md            # 시나리오 명세서
│   ├── Prom_nomal_scenario.txt         # 전문가 프롬프트
│   └── development_process/
│       └── development_roadmap.md      # 본 개발 로드맵 문서
├── images/                             # 샘플 이미지
├── videos/                             # 테스트용 동영상 (test_1.mp4 ~ test_8.mp4)
├── src/                                # 핵심 시스템 소스코드
│   ├── config.py                       # 시스템 전역 임계값 및 PC 제어 관련 설정
│   ├── devices/                        # 카메라 수집 및 프레임 버퍼링 모듈
│   │   ├── camera.py                   # 비디오 파일 Streamer (추후 USB 카메라 VideoCapture 0 지원)
│   │   └── buffer.py                   # 5프레임 중 3프레임 동일인 검출 버퍼 로직
│   ├── ai/                             # AI 추론 및 사생활 보호 모듈
│   │   ├── privacy.py                  # 얼굴 ROI 추출 및 원본 이미지 메모리 폐기
│   │   └── estimator.py                # DeepFace 기반 연령/성별/신뢰도 추론
│   ├── policy/                         # 정책 결정 엔진
│   │   └── decision.py                 # 신뢰도(0.7), 운전석 좌표/다수결, 연령대 파라미터 매핑
│   ├── controllers/                    # 인포테인먼트 및 PC 시스템 제어 모듈
│   │   ├── base.py                     # 제어기 추상 클래스 (Interface)
│   │   └── pc_controller.py            # PC 스피커 볼륨(amixer/pulseaudio), 모니터 밝기(xrandr/brightnessctl), TTS 음성알림
│   └── logger/                         # 감사 및 이력 로깅 모듈
│       └── audit_logger.py             # 비식별 JSON 로거
├── tests/                              # 단위 테스트 및 통합 테스트
│   ├── test_buffer.py
│   ├── test_policy.py
│   └── test_pc_controller.py
├── main.py                             # 메인 파이프라인 엔트리포인트 (비디오 테스트 실행)
└── README.md
```

### 2.2. 핵심 설계 원칙
1. **입력 유연성 (Input Flexibility):** 현재 동영상 파일 기반 분석 기능 검증 $\rightarrow$ 추후 USB 카메라 실시간 입력으로 소스 변경 없이 파라미터 전환 가능
2. **제어기 추상화 (Controller Abstraction):** PC 시스템 제어기(`PCInfotainmentController`) 구현 후, 차후 차량 전용 제어기(`VehicleInfotainmentController`) 확장 구조 적용
3. **실제 PC 제어 & 음성 알림 (Real PC Control & TTS):** Linux PC 볼륨 및 밝기 조절 제어기 연동 + TTS/음성 출력을 이용해 변경 완료 고지 (*"운전자 맞춤 설정이 완료되었습니다. 볼륨 80%, 밝기 100%로 변경되었습니다."*)
4. **사생활 보호 최우선 (Privacy-First):** 얼굴 ROI 수치 추출 직후 원본 영상 프레임 메모리 즉시 삭제 (`Step 9~10`)
5. **온디바이스 성능 (Latency $\le 2.5$s):** 입력~추론~PC제어~음성안내 지연시간 2.5초 이내 달성

---

## 3. 단계별 개발 계획 (Phase-by-Phase Plan)

### 📍 Phase 01: 비디오 스트림 수집 & 프레임 버퍼링 모듈 구축 (1~2일차)
* **주요 목표:** 동영상 파일 기반 입력 수집 및 5프레임 중 3프레임 검출 로직 구현
* **구현 세부사항:**
  - `src/config.py`: PC 제어 명령, 버퍼 크기(5), 기준 횟수(3), 신뢰도(0.7), 운전석 좌표 범위 정의
  - `src/devices/camera.py`: `videos/*.mp4` 비디오 파일 스트리머 구현 (USB 카메라 전환 모드 포함)
  - `src/devices/buffer.py`: 최근 5개 프레임 버퍼 관리 및 3개 이상 검출 시 가동 플래그 전달 (`Step 6~8`)

---

### 📍 Phase 02: AI 추론 & 연령대 정책 결정 모듈 개발 (3~4일차)
* **주요 목표:** DeepFace 추론, 사생활 보호 ROI 처리, 연령대별 제어값 산출
* **구현 세부사항:**
  - `src/ai/privacy.py`: 얼굴 Bounding Box 텐서 추출 후 원본 프레임 즉시 삭제 (`Step 9~10`)
  - `src/ai/estimator.py`: DeepFace 연동 연령/성별 추정 및 신뢰도 스코어 산출 (`Step 11~13`)
  - `src/policy/decision.py`: (`Step 14~19`)
    - 신뢰도 점수 $\ge 0.7$ 필터링
    - 운전석 영역 좌표 1순위 지정 및 공석 시 다수결 나이대 선택
    - 연령대별 PC 제어 파라미터 매핑 (70대 이상 / 50~60대 / 40대 이하)

---

### 📍 Phase 03: PC 제어기 (볼륨/밝기/TTS) & 비식별 로거 개발 (5일차)
* **주요 목표:** Linux PC 실시간 스피커 볼륨/밝기 조절, TTS 음성 안내 및 JSON 로깅
* **구현 세부사항:**
  - `src/controllers/pc_controller.py`: (`Step 20~22`)
    - **PC 볼륨 제어:** Linux `amixer` / `pulseaudio` 명령을 통한 실제 스피커 볼륨(60%/70%/80%) 조절
    - **PC 밝기 제어:** `xrandr` / `brightnessctl` 모니터 밝기(80%/90%/100%) 조절
    - **TTS 음성 알림:** PC 스피커로 변경 완료 내역 음성 고지 (*"운전자 맞춤 설정이 완료되었습니다. 볼륨 80%, 밝기 100%로 변경되었습니다."*)
    - **이상 경고 음성:** 비정상 상황 시 경고 음성 송출 후 자원 해제 (`Step 3~4`)
  - `src/logger/audit_logger.py`: 타임스탬프, 연령대, 신뢰도 점수, 파라미터 값 비식별 JSON 로깅 (`Step 23`)

---

### 📍 Phase 04: 메인 파이프라인 통합 & 기능/성능 검증 (6~7일차)
* **주요 목표:** 비디오 테스트셋을 통한 메인 파이프라인 실행 및 종합 검증
* **구현 세부사항:**
  - `main.py`: `python main.py --video videos/test_1.mp4` 형태로 동영상 분석 테스트 실행
  - **기능 검증:** PC 스피커 볼륨 및 화면 밝기가 영상 속 인물 연령대에 맞게 실제 변경되고 안내 음성이 나오는지 테스트
  - **성능/품질 검증:** 처리 지연시간 2.5초 이내 달성 확인, 원본 이미지 미저장 검증, 단위 테스트(`pytest`) 수행

---

## 4. 검증 및 테스트 계획 (Verification & Testing)

### 4.1. 기능 및 단위 테스트 (Unit Tests)
- `test_buffer.py`: 5개 프레임 중 3개 검출 동작 조건 테스트
- `test_policy.py`: 0.7 미만 신뢰도 미적용, 운전석 우선순위 및 다수결 알고리즘 테스트
- `test_pc_controller.py`: PC 볼륨/밝기 조절 명령어 수신 및 실행 검증

### 4.2. 통합 테스트 (Integration Verification)
- 동영상 샘플 8종(`test_1.mp4`~`test_8.mp4`)을 입력으로 통합 이벤트 루프 테스트 진행
- 영상 재생 시 2.5초 이내 PC 볼륨/밝기가 자동 변경되고 음성 안내 멘트가 정상 송출되는지 확인
- `logs/audit_log.json`에 원본 이미지 없이 비식별 텍스트 데이터만 기록되는지 확인
