from __future__ import annotations

from collections import deque

import cv2
import numpy as np


class MotionEstimator:
    """Estimate large-scale motion while smoothing out minor frame jitter."""

    def __init__(self, motion_threshold: float, window_size: int = 5) -> None:
        self.motion_threshold = motion_threshold
        self._window = deque(maxlen=window_size)

    def estimate(self, prev_gray: np.ndarray, curr_gray: np.ndarray) -> tuple[bool, float, float]:
        """Return (is_moving, confidence, smoothed_magnitude)."""
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray,
            curr_gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=21,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )
        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

        # Use a high quantile to focus on large coherent motion, not tiny waves.
        raw_mag = float(np.percentile(mag, 75))
        self._window.append(raw_mag)
        smoothed = float(np.mean(self._window))
        is_moving = smoothed >= self.motion_threshold

        distance = abs(smoothed - self.motion_threshold)
        confidence = min(1.0, 0.5 + distance / max(self.motion_threshold, 1e-6) * 0.5)
        return is_moving, confidence, smoothed
