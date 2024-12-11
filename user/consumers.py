# consumers.py in your Django app
import cv2
import json
import time
import numpy as np
import mediapipe as mp
from channels.generic.websocket import AsyncWebsocketConsumer

class TrainingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.running = True

    async def disconnect(self, close_code):
        self.running = False

    async def receive(self, text_data):
        # Parse the incoming data (if any)
        data = json.loads(text_data)
        duration = 30  # Training duration in seconds

        # Initialize Mediapipe Pose and OpenCV
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()
        deviation_threshold = 0.05
        session_scores = []

        cap = cv2.VideoCapture(0)  # Open camera
        if not cap.isOpened():
            await self.send(json.dumps({"error": "Camera not accessible"}))
            return

        start_time = time.time()
        while self.running and (time.time() - start_time < duration):
            ret, frame = cap.read()
            if not ret:
                break

            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            # Process landmarks and give feedback
            if results.pose_landmarks:
                for lm in results.pose_landmarks.landmark:
                    deviation = np.random.rand()  # Replace with real deviation calculation
                    session_scores.append(deviation)
                    color = (0, 255, 0) if deviation < deviation_threshold else (0, 0, 255)
                    x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, color, -1)

            # Encode frame as JPEG and send to frontend
            _, buffer = cv2.imencode(".jpg", frame)
            await self.send(bytes_data=buffer.tobytes())

        cap.release()
        pose.close()

        # Calculate and send the final score
        final_score = 100 - (np.mean(session_scores) * 100)
        await self.send(json.dumps({"score": final_score}))
        self.running = False
  