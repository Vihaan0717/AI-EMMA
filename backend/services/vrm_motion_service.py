import asyncio
import cv2
import mediapipe as mp
import mediapipe.python.solutions.pose as mp_pose
import websockets
import json
import math
import numpy as np
import yt_dlp
import logging

logger = logging.getLogger("VRMMotionService")
logger.setLevel(logging.INFO)

class VRMMotionService:
    def __init__(self, port=8001):
        self.port = port
        self.mp_pose = mp_pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.clients = set()
        self.is_running = False

    async def register(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, data):
        if not self.clients:
            return
        message = json.dumps(data)
        await asyncio.gather(*[client.send(message) for client in self.clients], return_exceptions=True)

    async def start_server(self):
        async with websockets.serve(self.register, "localhost", self.port):
            logger.info(f"VRM Motion WebSocket Server running on ws://localhost:{self.port}")
            await asyncio.Future()  # Run forever

    def _get_youtube_stream_url(self, url: str) -> str:
        ydl_opts = {'format': 'best[ext=mp4]', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url']

    def _calculate_quaternion_from_vectors(self, v1, v2):
        """Calculates rotation quaternion from v1 to v2"""
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)
        axis = np.cross(v1, v2)
        axis_norm = np.linalg.norm(axis)
        if axis_norm < 1e-5:
            return {"x": 0, "y": 0, "z": 0, "w": 1}
        axis = axis / axis_norm
        angle = np.arccos(np.clip(np.dot(v1, v2), -1.0, 1.0))
        
        sin_half = np.sin(angle / 2)
        return {
            "x": axis[0] * sin_half,
            "y": axis[1] * sin_half,
            "z": axis[2] * sin_half,
            "w": np.cos(angle / 2)
        }

    def _landmarks_to_vrm(self, landmarks):
        """Map MediaPipe landmarks to VRM bone quaternions (Simplified DigiHuman math)"""
        bones = {}
        
        # Helper to get numpy array of a landmark
        def get_lm(idx):
            lm = landmarks.landmark[idx]
            # MediaPipe origin is top-left, VRM is usually bottom-up.
            # We map X, Y, Z. Z is depth.
            return np.array([lm.x, -lm.y, -lm.z])

        try:
            # 1. Left Arm (Shoulder -> Elbow -> Wrist)
            l_shoulder = get_lm(self.mp_pose.PoseLandmark.LEFT_SHOULDER.value)
            l_elbow = get_lm(self.mp_pose.PoseLandmark.LEFT_ELBOW.value)
            l_wrist = get_lm(self.mp_pose.PoseLandmark.LEFT_WRIST.value)
            
            upper_arm_vec = l_elbow - l_shoulder
            lower_arm_vec = l_wrist - l_elbow
            
            # Default T-pose vector for left arm is [1, 0, 0]
            bones['leftUpperArm'] = self._calculate_quaternion_from_vectors(np.array([1, 0, 0]), upper_arm_vec)
            bones['leftLowerArm'] = self._calculate_quaternion_from_vectors(upper_arm_vec, lower_arm_vec)

            # 2. Right Arm (Shoulder -> Elbow -> Wrist)
            r_shoulder = get_lm(self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
            r_elbow = get_lm(self.mp_pose.PoseLandmark.RIGHT_ELBOW.value)
            r_wrist = get_lm(self.mp_pose.PoseLandmark.RIGHT_WRIST.value)
            
            # Default T-pose vector for right arm is [-1, 0, 0]
            upper_arm_vec_r = r_elbow - r_shoulder
            lower_arm_vec_r = r_wrist - r_elbow
            
            bones['rightUpperArm'] = self._calculate_quaternion_from_vectors(np.array([-1, 0, 0]), upper_arm_vec_r)
            bones['rightLowerArm'] = self._calculate_quaternion_from_vectors(upper_arm_vec_r, lower_arm_vec_r)

            # 3. Head/Neck Rotation (Nose & Ears)
            nose = get_lm(self.mp_pose.PoseLandmark.NOSE.value)
            l_ear = get_lm(self.mp_pose.PoseLandmark.LEFT_EAR.value)
            r_ear = get_lm(self.mp_pose.PoseLandmark.RIGHT_EAR.value)
            
            head_dir = (l_ear + r_ear) / 2.0
            face_vec = nose - head_dir
            # Default face vector is [0, 0, 1] (facing forward)
            bones['head'] = self._calculate_quaternion_from_vectors(np.array([0, 0, 1]), face_vec)

        except Exception as e:
            logger.error(f"Error mapping landmarks: {e}")
            
        return bones

    async def process_video(self, source_url: str):
        """Process video (YouTube URL or local path) and broadcast motion data."""
        self.is_running = True
        
        # If it's a youtube link, resolve to direct mp4 stream
        if "youtube.com" in source_url or "youtu.be" in source_url:
            logger.info(f"Extracting stream URL for {source_url}...")
            try:
                stream_url = self._get_youtube_stream_url(source_url)
            except Exception as e:
                logger.error(f"Failed to extract YouTube stream: {e}")
                self.is_running = False
                return
        else:
            stream_url = source_url

        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            logger.error(f"Could not open video stream: {stream_url}")
            self.is_running = False
            return
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps < 1:
            fps = 30.0
            
        frame_time = 1.0 / fps
        logger.info(f"Starting motion capture from stream at ~{fps} FPS.")

        while cap.isOpened() and self.is_running:
            loop_start = asyncio.get_event_loop().time()
            
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert BGR to RGB for MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            results = self.pose.process(image)
            
            if results.pose_landmarks:
                bones = self._landmarks_to_vrm(results.pose_landmarks)
                
                # We can also add some dummy blendshapes based on mouth openness
                # For a full DigiHuman implementation, we would use FaceMesh
                payload = {
                    "bones": bones,
                    "blendshapes": {
                        "A": 0.0 # Neutral mouth for now
                    }
                }
                
                await self.broadcast(payload)
                
            # Maintain framing speed
            elapsed = asyncio.get_event_loop().time() - loop_start
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            else:
                await asyncio.sleep(0.001)

        cap.release()
        self.is_running = False
        logger.info("Video processing finished.")

    def stop(self):
        self.is_running = False

# Standalone execution for testing
if __name__ == "__main__":
    service = VRMMotionService()
    asyncio.run(service.start_server())
