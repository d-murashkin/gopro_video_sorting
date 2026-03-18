from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import cv2
import numpy as np

from .analyze_brightness import classify_night, estimate_luminance
from .analyze_motion import MotionEstimator
from .config import AnalyzerConfig
from .discovery import build_video_records, with_media_props
from .models import Segment, VideoFile


class GoProClassifier:
    """Classify folder videos into movement/stationary/night timeline segments."""

    def __init__(self, config: AnalyzerConfig) -> None:
        self.config = config
        self._analysis_width = 360

    def classify_folder(self) -> tuple[list[VideoFile], list[Segment]]:
        videos = build_video_records(self.config.input_dir)
        segments: list[Segment] = []
        enriched: list[VideoFile] = []
        for video in videos:
            info, video_segments = self.classify_video(video)
            enriched.append(info)
            segments.extend(video_segments)
        return enriched, segments

    def classify_video(self, video: VideoFile) -> tuple[VideoFile, list[Segment]]:
        cap = cv2.VideoCapture(str(video.path))
        if not cap.isOpened():
            return video, []

        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        if fps <= 0:
            fps = 30.0

        frame_count = float(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0)
        duration_seconds = frame_count / fps if frame_count > 0 else 0.0

        info = with_media_props(video, duration_seconds=duration_seconds, fps=fps)
        step = max(1, self.config.sample_every_n_frames)
        motion_estimator = MotionEstimator(self.config.motion_threshold)
        max_frame_idx = None
        if self.config.max_analysis_seconds is not None:
            max_frame_idx = int(self.config.max_analysis_seconds * fps)

        sampled_labels: list[tuple[float, str, float]] = []
        prev_gray = None
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if max_frame_idx is not None and frame_idx > max_frame_idx:
                break

            if frame_idx % step != 0:
                frame_idx += 1
                continue

            timestamp = frame_idx / fps
            analysis_frame = self._resize_for_analysis(frame)
            gray = cv2.cvtColor(analysis_frame, cv2.COLOR_BGR2GRAY)
            luminance = estimate_luminance(frame)
            is_night, night_conf = classify_night(luminance, self.config.brightness_night_threshold)

            if is_night:
                label = "night"
                confidence = night_conf
            elif prev_gray is None:
                label = "stationary"
                confidence = 0.55
            else:
                is_moving, motion_conf, _ = motion_estimator.estimate(prev_gray, gray)
                label = "movement" if is_moving else "stationary"
                confidence = motion_conf

            sampled_labels.append((timestamp, label, confidence))
            prev_gray = gray
            frame_idx += 1

        cap.release()
        effective_duration = duration_seconds
        if max_frame_idx is not None:
            effective_duration = min(duration_seconds, max_frame_idx / fps)

        return info, self._segmentize(video, sampled_labels, effective_duration, step / fps)

    def _resize_for_analysis(self, frame: np.ndarray) -> np.ndarray:
        height, width = frame.shape[:2]
        if width <= self._analysis_width:
            return frame
        scale = self._analysis_width / float(width)
        new_h = max(1, int(height * scale))
        return cv2.resize(frame, (self._analysis_width, new_h), interpolation=cv2.INTER_AREA)

    def _segmentize(
        self,
        video: VideoFile,
        sampled_labels: list[tuple[float, str, float]],
        duration_seconds: float,
        sample_seconds: float,
    ) -> list[Segment]:
        if not sampled_labels:
            return []

        output: list[Segment] = []
        start_t, current_label, conf_sum = sampled_labels[0]
        conf_count = 1

        for idx in range(1, len(sampled_labels)):
            t, label, conf = sampled_labels[idx]
            if label == current_label:
                conf_sum += conf
                conf_count += 1
                continue

            end_t = max(start_t + sample_seconds, sampled_labels[idx - 1][0] + sample_seconds)
            output.append(
                Segment(
                    video_path=str(video.path),
                    global_start_epoch=video.start_epoch + start_t,
                    global_end_epoch=video.start_epoch + end_t,
                    local_start_seconds=start_t,
                    local_end_seconds=end_t,
                    label=current_label,
                    confidence=max(self.config.confidence_floor, conf_sum / conf_count),
                )
            )
            start_t = t
            current_label = label
            conf_sum = conf
            conf_count = 1

        output.append(
            Segment(
                video_path=str(video.path),
                global_start_epoch=video.start_epoch + start_t,
                global_end_epoch=video.start_epoch + duration_seconds,
                local_start_seconds=start_t,
                local_end_seconds=duration_seconds,
                label=current_label,
                confidence=max(self.config.confidence_floor, conf_sum / conf_count),
            )
        )

        return self._merge_short_segments(output)

    def _merge_short_segments(self, segments: list[Segment]) -> list[Segment]:
        if not segments:
            return []

        min_len = self.config.min_segment_seconds
        merged: list[Segment] = [segments[0]]

        for seg in segments[1:]:
            prev = merged[-1]
            prev_len = prev.local_end_seconds - prev.local_start_seconds
            if seg.label == prev.label or prev_len < min_len:
                merged[-1] = Segment(
                    video_path=prev.video_path,
                    global_start_epoch=prev.global_start_epoch,
                    global_end_epoch=seg.global_end_epoch,
                    local_start_seconds=prev.local_start_seconds,
                    local_end_seconds=seg.local_end_seconds,
                    label=seg.label if prev_len < min_len else prev.label,
                    confidence=max(prev.confidence, seg.confidence),
                )
            else:
                merged.append(seg)

        return merged


def segment_as_dict(segment: Segment) -> dict[str, str | float]:
    return asdict(segment)
