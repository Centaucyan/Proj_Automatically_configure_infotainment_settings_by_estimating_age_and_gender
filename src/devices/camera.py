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