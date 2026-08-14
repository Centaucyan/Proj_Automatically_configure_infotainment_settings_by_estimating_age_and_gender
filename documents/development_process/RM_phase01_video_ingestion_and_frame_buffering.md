# 🛠️ Phase 1 개발 실행 가이드 및 소스코드
> **목표:** 개발자가 직접 코드를 따라 작성하거나 이해하며 실행할 수 있도록 `src/config.py`, `src/devices/camera.py`, `src/devices/buffer.py`, 그리고 테스트 코드의 전체 소스코드와 기능별 설명을 제공합니다.

---

## 1. `src/config.py` (전역 시스템 설정)

### 📌 파일 역할
시스템 전체에서 사용하는 설정값(버퍼 크기, 기준 프레임 수, AI 신뢰도, 비디오 경로, 연령대별 제어 정책 등)을 한곳에서 관리합니다.

### 💻 소스코드 (`src/config.py`)
```python
import os

# ==========================================
# 1. 시스템 및 프레임 버퍼 설정
# ==========================================
# 프레임 버퍼 크기 (최근 5개 프레임 유지)
BUFFER_SIZE = 5

# 분석 스타트에 필요한 최소 얼굴 검출 프레임 수 (5개 중 3개 이상)
MIN_DETECTION_COUNT = 3

# AI 추론 나이대 신뢰도(Probability Score) 임계값
CONFIDENCE_THRESHOLD = 0.7

# 30초 동안 얼굴 미검출 시 자동 종료 타임아웃 (초 단위)
INACTIVITY_TIMEOUT_SEC = 30.0

# ==========================================
# 2. 비디오 / 카메라 입력 설정
# ==========================================
# 프로젝트 루트 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 기능 테스트용 기본 동영상 파일 경로 (videos/test_1.mp4)
DEFAULT_VIDEO_PATH = os.path.join(BASE_DIR, "videos", "test_1.mp4")

# USB 카메라 사용 시 디바이스 ID (0번 카메라)
CAMERA_DEVICE_ID = 0

# ==========================================
# 3. 운전석 영역 Bounding Box 좌표 정의
# ==========================================
# 프레임 이미지 내 운전석 비율 영역 (예: 화면 좌측 절반 x: 0.0 ~ 0.5)
DRIVER_SEAT_ROI = {
    "x_min": 0.0,
    "x_max": 0.5,
    "y_min": 0.0,
    "y_max": 1.0
}

# ==========================================
# 4. 연령대별 인포테인먼트 제어 파라미터 매핑
# ==========================================
AGE_CONTROL_POLICY = {
    "SENIOR_70s": {          # 70대 이상
        "volume_percent": 80,
        "speed_rate": 0.8,
        "brightness_percent": 100,
        "message": "70대 이상 맞춤 설정이 적용되었습니다."
    },
    "MIDDLE_50_60s": {       # 50~60대
        "volume_percent": 70,
        "speed_rate": 1.0,
        "brightness_percent": 90,
        "message": "50~60대 맞춤 설정이 적용되었습니다."
    },
    "YOUNG_40s_UNDER": {     # 40대 이하
        "volume_percent": 60,
        "speed_rate": 1.2,
        "brightness_percent": 80,
        "message": "40대 이하 맞춤 설정이 적용되었습니다."
    }
}
```

---

## 2. `src/devices/camera.py` (비디오 & 카메라 스트리머)

### 📌 파일 역할
비디오 파일(`videos/*.mp4`) 또는 USB 카메라에서 프레임을 순차적으로 읽어오고, 하드웨어 신호 정상 여부를 체크합니다.

### 💻 소스코드 (`src/devices/camera.py`)
```python
import cv2

class VideoStreamReader:
    """비디오 파일 또는 USB 카메라 신호를 수집하고 헬스체크를 수행하는 클래스"""
    
    def __init__(self, source=None):
        """
        :param source: 비디오 파일 경로(str) 또는 카메라 장치 번호(int)
        """
        self.source = source
        self.cap = None

    def open(self) -> bool:
        """스트림을 열고 기기/파일 상태 점검"""
        if self.source is None:
            from src.config import DEFAULT_VIDEO_PATH
            self.source = DEFAULT_VIDEO_PATH

        self.cap = cv2.VideoCapture(self.source)
        return self.cap.isOpened()

    def check_health(self) -> bool:
        """카메라 물리적 연결 및 영상 신호 수신 상태 검증"""
        if self.cap is None or not self.cap.isOpened():
            return False
        # 첫 프레임을 읽어 신호가 정상 들어오는지 테스트
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False
        # 테스트 읽기 후 프레임 포인터를 처음 위치(0)로 원복 (비디오 파일인 경우)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        return True

    def read_frame(self):
        """
        다음 영상 프레임을 읽어서 반환
        :return: (is_success: bool, frame_image: numpy.ndarray)
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        return self.cap.read()

    def get_fps(self) -> float:
        """영상 프레임 레이트(FPS) 반환"""
        if self.cap and self.cap.isOpened():
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            return fps if fps > 0 else 30.0
        return 30.0

    def release(self):
        """카메라 및 영상 메모리 자원 해제"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
```

---

## 3. `src/devices/buffer.py` (프레임 버퍼 관리자)

### 📌 파일 역할
최근 5개의 프레임 분석 결과를 `collections.deque`로 유지하며, 5개 중 3개 이상 동일인/얼굴이 검출되었는지 판별합니다.

### 💻 소스코드 (`src/devices/buffer.py`)
```python
from collections import deque
from typing import List, Dict, Any

class FrameBufferManager:
    """최근 N개 프레임의 검출 결과를 저장하고 시작 조건(M개 이상 검출)을 판단하는 클래스"""

    def __init__(self, buffer_size: int = 5, min_detect_count: int = 3):
        """
        :param buffer_size: 버퍼 유지 프레임 수 (기본 5)
        :param min_detect_count: 시스템 가동에 필요한 최소 검출 프레임 수 (기본 3)
        """
        self.buffer_size = buffer_size
        self.min_detect_count = min_detect_count
        # maxlen을 지정하여 N개 초과 시 자동으로 가장 오래된 항목 pop
        self.buffer = deque(maxlen=self.buffer_size)

    def push_frame_result(self, detected_faces: List[Dict[str, Any]]):
        """
        프레임별 얼굴 검출 정보 리스트를 버퍼에 추가
        :param detected_faces: 해당 프레임에서 감지된 얼굴 객체 리스트
        """
        has_face = len(detected_faces) > 0
        record = {
            "has_face": has_face,
            "faces": detected_faces,
            "face_count": len(detected_faces)
        }
        self.buffer.append(record)

    def is_start_condition_met(self) -> bool:
        """
        최근 버퍼 항목 중 3개 이상에서 얼굴이 검출되었는지 확인
        """
        if len(self.buffer) < self.min_detect_count:
            return False  # 아직 최소 프레임 데이터가 쌓이지 않음

        # 최근 버퍼 항목 중 has_face가 True인 프레임 개수 카운트
        detected_frames_count = sum(1 for rec in self.buffer if rec["has_face"])
        
        # 설정된 최소 기준 이상이면 시작 조건 충족 (True)
        return detected_frames_count >= self.min_detect_count

    def get_latest_detected_faces(self) -> List[Dict[str, Any]]:
        """가장 최근 프레임에서 검출된 얼굴 객체 리스트 반환"""
        if self.buffer and self.buffer[-1]["has_face"]:
            return self.buffer[-1]["faces"]
        return []

    def clear(self):
        """버퍼 초기화"""
        self.buffer.clear()
    
    def __len__(self):
        return len(self.buffer)
```

---

## 4. `tests/test_buffer.py` (Phase 1 단위 테스트)

### 📌 파일 역할
`pytest`를 이용하여 프레임 버퍼가 설정된 기준 이상 검출 시 정상적으로 `True`를 반환하는지 자동으로 검증합니다.

### 💻 소스코드 (`tests/test_buffer.py`)
```python
import pytest
from src.devices.buffer import FrameBufferManager

def test_buffer_initialization():
    """버퍼 초기화 및 초기 상태 테스트"""
    buf = FrameBufferManager(buffer_size=5, min_detect_count=3)
    assert len(buf) == 0
    assert buf.is_start_condition_met() is False

def test_buffer_start_condition_success():
    """5개 프레임 중 3개 이상 검출 시 시작 조건 충족 (True) 테스트"""
    buf = FrameBufferManager(buffer_size=5, min_detect_count=3)
    
    # 5개 프레임 중 3개 프레임에 얼굴 존재
    buf.push_frame_result([{"box": [10, 10, 50, 50]}]) # 1번째 (성공)
    buf.push_frame_result([])                         # 2번째 (실패)
    buf.push_frame_result([{"box": [12, 12, 52, 52]}]) # 3번째 (성공)
    buf.push_frame_result([])                         # 4번째 (실패)
    buf.push_frame_result([{"box": [15, 15, 55, 55]}]) # 5번째 (성공)
    
    # 총 3회 성공 -> 시작 조건 True이어야 함
    assert buf.is_start_condition_met() is True

def test_buffer_start_condition_failure():
    """5개 프레임 중 2개 이하 검출 시 시작 조건 미달 (False) 테스트"""
    buf = FrameBufferManager(buffer_size=5, min_detect_count=3)
    
    buf.push_frame_result([{"box": [10, 10, 50, 50]}]) # 1번째 (성공)
    buf.push_frame_result([])                         # 2번째 (실패)
    buf.push_frame_result([])                         # 3번째 (실패)
    buf.push_frame_result([])                         # 4번째 (실패)
    buf.push_frame_result([{"box": [15, 15, 55, 55]}]) # 5번째 (성공)
    
    # 총 2회 성공 -> 시작 조건 False이어야 함
    assert buf.is_start_condition_met() is False
```

---

## 5. Phase 1 통합 검증 실행 스크립트 (`run_phase1_test.py`)

### 📌 파일 역할
실제 `videos/test_1.mp4` 파일에서 프레임을 읽어와 OpenCV 기본 얼굴 검출기(Haar Cascade)로 프레임 버퍼에 밀어 넣고, 검출 조건이 발동되는지 터미널 화면에 시각적으로 보여주는 데모 스크립트입니다.

### 💻 소스코드 (`run_phase1_test.py`)
```python
import cv2
import time
from src.config import DEFAULT_VIDEO_PATH
from src.devices.camera import VideoStreamReader
from src.devices.buffer import FrameBufferManager

def main():
    print("🚀 Phase 1: 비디오 스트림 수집 및 버퍼링 테스트를 시작합니다...")
    
    # 1. 비디오 스트리머 오픈 및 헬스체크
    reader = VideoStreamReader(DEFAULT_VIDEO_PATH)
    if not reader.open() or not reader.check_health():
        print("❌ [경고] 비디오 파일 신호 점검 실패! 기기 이상 경고를 송출합니다.")
        return

    print(f"✅ [정상] 비디오 파일 연결 성공: {DEFAULT_VIDEO_PATH}")
    
    # 2. 프레임 버퍼 생성 (5프레임 중 3프레임 검출 조건)
    buffer_mgr = FrameBufferManager(buffer_size=5, min_detect_count=3)
    
    # 가벼운 OpenCV 얼굴 검출기 사용 (Phase 1 테스트용)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    frame_count = 0
    start_triggered = False

    while True:
        ret, frame = reader.read_frame()
        if not ret or frame is None:
            print("🎬 비디오 재생이 완료되었습니다.")
            break

        frame_count += 1
        
        # 회색조 변환 후 얼굴 검출
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        detected_list = [{"box": (x, y, w, h)} for (x, y, w, h) in faces]
        
        # 3. 버퍼에 결과 수집
        buffer_mgr.push_frame_result(detected_list)
        
        # 4. 검출 가동 조건 확인
        if buffer_mgr.is_start_condition_met():
            if not start_triggered:
                print(f"🎉 [시작 조건 충족!] 프레임 #{frame_count}: 최근 5개 프레임 중 3개 이상에서 얼굴 검출 성공! AI 분석 프로세스를 시작합니다.")
                start_triggered = True
        else:
            if start_triggered:
                print(f"⚠️ 프레임 #{frame_count}: 얼굴 미검출로 가동 대기 중...")
                start_triggered = False

    reader.release()
    print("✅ Phase 1 테스트가 성공적으로 종료되었습니다.")

if __name__ == "__main__":
    main()
```
