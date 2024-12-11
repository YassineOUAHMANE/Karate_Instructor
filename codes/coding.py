import cv2
import numpy as np
from scipy.spatial.distance import euclidean
import mediapipe as mp
import time
import json
import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime
from feedback.models import ProgressHistory
import os
import win32gui
import win32con
import win32api


# Save session data
def save_session_data(movement, score):
    ProgressHistory.objects.create(movement=movement, score=score)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
# Mapping of keypoints to body parts for feedback
body_parts = {
    11: "left shoulder", 12: "right shoulder",
    13: "left elbow", 14: "right elbow",
    15: "left wrist", 16: "right wrist",
    23: "left hip", 24: "right hip",
    25: "left knee", 26: "right knee",
    27: "left ankle", 28: "right ankle"
}

# Function to load the reference sequence for a movement
def load_reference_sequence(movement, reference_sequences_file=r"C:\Users\pc gamer\OneDrive\Desktop\ver1\Karate_Instructor\codes\reference_sequences.json"):
    with open(reference_sequences_file, "r") as f:
        reference_sequences = json.load(f)
    return np.array(reference_sequences.get(movement, []))

# Moving average function to smooth deviations
def smooth_deviation(deviations, window_size=5):
    smoothed = []
    for i in range(len(deviations)):
        window = deviations[max(0, i - window_size + 1):i + 1]
        smoothed.append(np.mean(window))
    return smoothed

# Function to save session data
def save_session_datajson(movement, score, progress_history_file=r"C:\Users\pc gamer\OneDrive\Desktop\ver1\Karate_Instructor\codes\progress_history.json"):
    try:
        with open(progress_history_file, "r") as f:
            progress_history = json.load(f)
    except FileNotFoundError:
        progress_history = {}
    
    session_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if movement not in progress_history:
        progress_history[movement] = []
    progress_history[movement].append({"session_id": session_id, "score": score})

    with open(progress_history_file, "w") as f:
        json.dump(progress_history, f)

# Function to plot progress over sessions
def setup_window(window_name, width, height, x, y):
    # Create a named window
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Resize and move the window
    cv2.resizeWindow(window_name, width, height)
    cv2.moveWindow(window_name, x, y)

    # Get the HWND for the OpenCV window
    hwnd = win32gui.FindWindow(None, window_name)

    # Remove the title bar and borders
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    # Set the window on top of all others
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW
    )

# Real-time feedback function with video or live camera support
def warp_keypoints(keypoints, transformation_matrix):
    keypoints_homogeneous = np.hstack((np.array(keypoints, dtype=np.float32), np.ones((len(keypoints), 1))))
    warped_keypoints = np.dot(keypoints_homogeneous, transformation_matrix.T)
    return warped_keypoints[:, :2]

def provide_real_time_feedback(movement, 
                                video_path=None,
                                reference_sequences_file=r"C:\Users\pc gamer\OneDrive\Desktop\ver1\Karate_Instructor\codes\reference_sequences.json", 
                                progress_history_file=r"C:\Users\pc gamer\OneDrive\Desktop\ver1\Karate_Instructor\codes\progress_history.json", 
                                deviation_threshold=0.06, 
                                moving_average_window=5, 
                                window_width=976, window_height=550, window_x=265, window_y=190):
    print(movement)
    if movement:
        movement='CHOKU-ZUKI'

    reference_sequence = load_reference_sequence(movement, reference_sequences_file)
    if len(reference_sequence) == 0:
        print(f"No reference sequence found for movement '{movement}'.")
        return

    cap = cv2.VideoCapture(0 if video_path is None else video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video source: {'camera' if video_path is None else video_path}")
        return

    window_name = "Real-Time Feedback"
    setup_window(window_name, window_width, window_height, window_x, window_y)

    stability_start_time = None
    frame_idx = 0
    deviation_history = {i: deque(maxlen=moving_average_window) for i in body_parts.keys()}
    session_deviation_scores = []
    stability_threshold = 0.01
    stability_duration = 5  # seconds
    is_scoring = False
    elapsed_time=0
    prev_keypoints=None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)
        feedback_messages = []

        if result.pose_landmarks:
            user_keypoints = [(lm.x, lm.y) for lm in result.pose_landmarks.landmark]

            if not is_scoring:
                ref_keypoints = reference_sequence[0]
                if prev_keypoints==None:
                    deviation=0.4
                else:
                    deviation = np.mean([euclidean(u, p) for u, p in zip(user_keypoints, prev_keypoints)])
                prev_keypoints = user_keypoints
                if deviation!=0 and deviation < stability_threshold:
                    transformation_matrix = cv2.estimateAffinePartial2D(np.array(user_keypoints, dtype=np.float32), 
                                                             np.array(ref_keypoints, dtype=np.float32))[0]
                    if stability_start_time is None:
                        stability_start_time = cv2.getTickCount()
                    elapsed_time = (cv2.getTickCount() - stability_start_time) / cv2.getTickFrequency()
                    if elapsed_time >= stability_duration:
                        print("Stability achieved. Starting scoring.")
                        is_scoring = True
                        stability_start_time = None
                else:
                    stability_start_time = None

                cv2.putText(frame, "Hold steady to start scoring...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            else:
                if stability_start_time is None:
                    stability_start_time = cv2.getTickCount()
                if frame_idx < len(reference_sequence):
                    warped_user_keypoints = warp_keypoints(user_keypoints, transformation_matrix)
                    ref_keypoints = reference_sequence[frame_idx]
                    deviations = []

                    for idx, (user_kp, warped_kp, ref_kp) in enumerate(zip(user_keypoints, warped_user_keypoints, ref_keypoints)):
                        deviation = euclidean(warped_kp, ref_kp)
                        if idx in body_parts:
                            deviation_history[idx].append(deviation)
                            smoothed_deviation = np.mean(deviation_history[idx])
                            deviations.append(smoothed_deviation)

                            if smoothed_deviation > deviation_threshold:
                                feedback_messages.append(f"Adjust {body_parts[idx]}")
                                cv2.circle(frame, (int(user_kp[0] * frame.shape[1]), int(user_kp[1] * frame.shape[0])), 5, (0, 0, 255), -1)
                            else:
                                cv2.circle(frame, (int(user_kp[0] * frame.shape[1]), int(user_kp[1] * frame.shape[0])), 5, (0, 255, 0), -1)

                    frame_deviation = np.mean(deviations)
                    normalized_deviation = min(frame_deviation / deviation_threshold, 1.0)
                    score = (1 - normalized_deviation) * 170
                    session_deviation_scores.append(score)
                    elapsed_time = (cv2.getTickCount() - stability_start_time) / cv2.getTickFrequency()
                frame_idx += 1
                if frame_idx >= len(reference_sequence):
                    frame_idx = 0

        y_offset = 60
        for message in feedback_messages:
            cv2.putText(frame, message, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            y_offset += 20

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q') or elapsed_time >= 20:
            break

    session_score = np.mean(session_deviation_scores) if session_deviation_scores else None
    print(f"Session score for '{movement}': {session_score}")

    cap.release()
    cv2.destroyAllWindows()
    return session_score