import os
import sys
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_base.agent_mcp_server import AgentMCPServer
from core.agent_result import AgentResult

logger = logging.getLogger("SensesMCP")
senses_server = AgentMCPServer("senses_mcp", "Hardware, Vision & Awareness Sensor Hub")
mcp = senses_server.mcp

_YOLO_MODEL = None

def _get_yolo():
    global _YOLO_MODEL
    if _YOLO_MODEL is None:
        try:
            from ultralytics import YOLO
            weights_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "yolov8n.pt")
            if os.path.exists(weights_path):
                _YOLO_MODEL = YOLO(weights_path)
            else:
                _YOLO_MODEL = YOLO("yolov8n.pt")
        except Exception as e:
            logger.warning(f"Could not load YOLO model: {e}")
            _YOLO_MODEL = None
    return _YOLO_MODEL

def scan_physical_environment(confidence_threshold: float = 0.5) -> str:
    """
    Scans the real-world environment via webcam using offline YOLOv8.
    Returns detected objects (e.g., person, laptop, cell phone, cup) with confidence.
    """
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=["webcam"],
                answer="",
                needs_verification=True,
                errors=["Webcam could not be opened or is in use by another application."]
            ).to_json()

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=["webcam"],
                answer="",
                needs_verification=True,
                errors=["Failed to capture frame from webcam."]
            ).to_json()

        model = _get_yolo()
        if not model:
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=["yolov8"],
                answer="",
                needs_verification=True,
                errors=["YOLOv8 weights or dependencies not initialized."]
            ).to_json()

        results = model(frame, verbose=False)
        detected = []
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf >= confidence_threshold:
                    cls_id = int(box.cls[0])
                    name = model.names[cls_id]
                    detected.append(f"{name} ({int(conf * 100)}%)")

        if not detected:
            summary = "No prominent objects detected above the confidence threshold."
        else:
            summary = "Detected physical objects: " + ", ".join(list(set(detected)))

        return AgentResult(
            status="success",
            confidence=0.9,
            sources=["offline_yolov8_webcam"],
            answer=summary,
            needs_verification=False,
            errors=[]
        ).to_json()

    except Exception as e:
        return AgentResult(
            status="error",
            confidence=0.0,
            sources=["offline_yolov8_webcam"],
            answer="",
            needs_verification=True,
            errors=[f"Environment scan error: {str(e)}"]
        ).to_json()

def check_user_presence() -> str:
    """
    Checks if a user is currently seated in front of the camera using OpenCV face detection.
    Useful for presence-aware greetings and automatic screen idle adjustments.
    """
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return AgentResult(status="error", confidence=0.0, sources=["webcam"], answer="", needs_verification=True, errors=["Webcam unavailable."]).to_json()

        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return AgentResult(status="error", confidence=0.0, sources=["webcam"], answer="", needs_verification=True, errors=["Failed to capture camera frame."]).to_json()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        is_present = len(faces) > 0
        status_text = f"User is present ({len(faces)} face(s) visible)." if is_present else "User is away (no faces detected in front of screen)."

        return AgentResult(
            status="success",
            confidence=0.85,
            sources=["opencv_face_detection"],
            answer=status_text,
            needs_verification=False,
            errors=[]
        ).to_json()
    except Exception as e:
        return AgentResult(
            status="error",
            confidence=0.0,
            sources=["opencv_face_detection"],
            answer="",
            needs_verification=True,
            errors=[f"Presence check error: {str(e)}"]
        ).to_json()

if mcp:
    mcp.tool()(scan_physical_environment)
    mcp.tool()(check_user_presence)

if __name__ == "__main__":
    senses_server.run()
