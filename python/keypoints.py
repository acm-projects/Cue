import collections
import numpy as np
import torch

NUM_SAMPLES = 50   # replace with num_samples from your TGCN config.ini

# MediaPipe pose index for each of the 13 body joints, in the model's order.
# None = computed (neck = shoulder midpoint, mid-hip = hip midpoint)
BODY_MAP = [0, None, 12, 14, 16, 11, 13, 15, None, 5, 2, 8, 7]


def _pts(landmarks):
    if landmarks is None:
        return None
    return np.array([[l.x, l.y] for l in landmarks.landmark], dtype=np.float32)


def frame_to_keypoints(results):
    """MediaPipe Holistic results -> (55, 2) in the model's format, or None if no body."""
    pose = _pts(results.pose_landmarks)
    if pose is None:
        return None  # caller repeats the previous frame

    raw = np.zeros((55, 2), dtype=np.float32)  # undetected stays (0,0), which becomes -1 below
    neck = (pose[11] + pose[12]) / 2
    lm = results.pose_landmarks.landmark
    hips_ok = lm[23].visibility > 0.5 and lm[24].visibility > 0.5
    hip = (pose[23] + pose[24]) / 2

    for i, idx in enumerate(BODY_MAP):
        if idx is not None:
            raw[i] = pose[idx]
        elif i == 1:
            raw[i] = neck
        elif hips_ok:
            raw[i] = hip  # otherwise stays 0 (missing)

    lh = _pts(results.left_hand_landmarks)
    rh = _pts(results.right_hand_landmarks)
    if lh is not None:
        raw[13:34] = lh
    if rh is not None:
        raw[34:55] = rh

    return 2 * (raw - 0.5)  # same transform as sign_dataset.py


class PoseBuffer:
    def __init__(self):
        self.frames = collections.deque(maxlen=NUM_SAMPLES)

    def add(self, kp):
        if kp is None and self.frames:
            kp = self.frames[-1]  # repeat last frame, like the dataset code
        if kp is not None:
            self.frames.append(kp)

    def tensor(self):
        if len(self.frames) < NUM_SAMPLES:
            return None
        clip = np.stack(self.frames)                       # (T, 55, 2)
        x = clip.transpose(1, 0, 2).reshape(55, -1)        # (55, T*2), x and y interleaved per frame
        return torch.from_numpy(x).float().unsqueeze(0)    # (1, 55, T*2)