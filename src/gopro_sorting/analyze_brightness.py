from __future__ import annotations

import cv2
import numpy as np


def estimate_luminance(frame_bgr: np.ndarray) -> float:
    """Compute mean luminance from Y channel in YCrCb."""
    ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)
    return float(ycrcb[:, :, 0].mean())


def classify_night(luminance: float, threshold: float) -> tuple[bool, float]:
    """Classify night by threshold and return confidence in [0, 1]."""
    is_night = luminance < threshold
    distance = abs(luminance - threshold)
    confidence = min(1.0, 0.5 + (distance / max(threshold, 1.0)) * 0.5)
    return is_night, confidence
