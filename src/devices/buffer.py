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