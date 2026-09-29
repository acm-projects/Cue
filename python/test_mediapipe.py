import cv2
import mediapipe as mp

from keypoints import frame_to_keypoints, PoseBuffer, NUM_SAMPLES

mp_holistic = mp.solutions.holistic
mp_draw = mp.solutions.drawing_utils

buffer = PoseBuffer()
cap = cv2.VideoCapture(1)  # 0 = default camera; try 1 if you get a black screen

with mp_holistic.Holistic(min_detection_confidence=0.5,
                          min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            print("Could not read from camera")
            break

        # MediaPipe wants RGB, OpenCV gives BGR. Use the un-mirrored frame here.
        results = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        kp = frame_to_keypoints(results)
        buffer.add(kp)

        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        mp_draw.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_draw.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        status = (f"pose: {results.pose_landmarks is not None}   "
                  f"left: {results.left_hand_landmarks is not None}   "
                  f"right: {results.right_hand_landmarks is not None}   "
                  f"buffer: {len(buffer.frames)}/{NUM_SAMPLES}")

        display = cv2.flip(frame, 1)  # mirror only for display
        cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 0), 2)
        cv2.imshow("MediaPipe test", display)

        t = buffer.tensor()
        if t is not None and cv2.waitKey(1) & 0xFF == ord("p"):   # press p to print
            print("tensor shape:", tuple(t.shape))                # expect (1, 55, 100)
            print("neck, latest frame:", kp[1] if kp is not None else None)
            print("left hand joint 13:", kp[13] if kp is not None else None)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()