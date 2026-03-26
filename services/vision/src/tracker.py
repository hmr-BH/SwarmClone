"""
面部追踪模块
"""

import time
from typing import Optional

import numpy as np
from loguru import logger

try:
    import cv2

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import mediapipe as mp

    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


class FaceTracker:
    """面部追踪器"""

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
    ):
        if not MEDIAPIPE_AVAILABLE:
            logger.warning("mediapipe未安装，面部追踪将不可用")
            self._available = False
            return

        self._available = True
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
        )

        self._last_result: Optional[dict] = None

    def process(self, image: np.ndarray) -> Optional[dict]:
        """
        处理图像并检测面部

        Args:
            image: BGR格式的图像

        Returns:
            面部数据字典
        """
        if not self._available:
            return None

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0]
        h, w = image.shape[:2]

        data = self._extract_features(landmarks, w, h)
        self._last_result = data

        return data

    def _extract_features(self, landmarks, width: int, height: int) -> dict:
        """提取面部特征"""
        points = []
        for lm in landmarks.landmark:
            points.append(
                {
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                }
            )

        left_eye = self._get_eye_openness(points, "left")
        right_eye = self._get_eye_openness(points, "right")
        mouth_open = self._get_mouth_openness(points)

        return {
            "timestamp": time.time(),
            "landmarks": points[:468],
            "eye_left": {
                "openness": left_eye,
                "blink": left_eye < 0.2,
            },
            "eye_right": {
                "openness": right_eye,
                "blink": right_eye < 0.2,
            },
            "mouth": {
                "openness": mouth_open,
                "open": mouth_open > 0.3,
            },
        }

    def _get_eye_openness(self, points: list, side: str) -> float:
        """计算眼睛开合度"""
        if side == "left":
            upper = points[159]
            lower = points[145]
        else:
            upper = points[386]
            lower = points[374]

        return abs(upper["y"] - lower["y"])

    def _get_mouth_openness(self, points: list) -> float:
        """计算嘴巴开合度"""
        upper = points[13]
        lower = points[14]
        return abs(upper["y"] - lower["y"])

    def close(self) -> None:
        """关闭追踪器"""
        if self._available:
            self.face_mesh.close()

    @property
    def is_available(self) -> bool:
        return self._available


class CameraCapture:
    """摄像头捕获"""

    def __init__(
        self,
        device: int = 0,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
    ):
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps

        self.cap: Optional[cv2.VideoCapture] = None
        self._running = False

    def start(self) -> bool:
        """启动摄像头"""
        if not CV2_AVAILABLE:
            logger.warning("opencv未安装，摄像头捕获将不可用")
            return False

        self.cap = cv2.VideoCapture(self.device)

        if not self.cap.isOpened():
            logger.error(f"无法打开摄像头: {self.device}")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self._running = True
        logger.info(f"摄像头已启动: {self.width}x{self.height} @ {self.fps}fps")
        return True

    def stop(self) -> None:
        """停止摄像头"""
        self._running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info("摄像头已停止")

    def read(self) -> Optional[np.ndarray]:
        """读取一帧"""
        if not self._running or not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    @property
    def is_running(self) -> bool:
        return self._running
