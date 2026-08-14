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