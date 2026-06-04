"""Scan video files and save map screenshots when the HLL map opens."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2

from .detector import HLLMapDetector, crop_map_region


@dataclass
class CaptureEvent:
    timestamp_sec: float
    frame_index: int
    output_path: Path
    good_matches: int


@dataclass
class ProcessingStats:
    frames_scanned: int
    map_open_frames: int
    captures: list[CaptureEvent]


class VideoMapProcessor:
    def __init__(
        self,
        detector: HLLMapDetector,
        output_dir: Path,
        *,
        speed_factor: int = 4,
        min_capture_interval_sec: float = 2.0,
        closed_frames_required: int = 3,
        map_crop: dict[str, float] | None = None,
        image_format: str = "png",
        video_stem: str = "video",
    ) -> None:
        self.detector = detector
        self.output_dir = output_dir
        self.speed_factor = max(1, speed_factor)
        self.min_capture_interval_sec = min_capture_interval_sec
        self.closed_frames_required = max(1, closed_frames_required)
        self.map_crop = map_crop or {
            "left": 0.22,
            "top": 0.07,
            "width": 0.56,
            "height": 0.86,
        }
        self.image_format = image_format.lower().lstrip(".")
        self.video_stem = video_stem

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process(self, video_path: Path) -> ProcessingStats:
        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
        frame_index = 0
        scanned = 0
        map_open_frames = 0
        captures: list[CaptureEvent] = []

        map_is_open = False
        closed_streak = self.closed_frames_required
        last_capture_timestamp = -999.0
        capture_counter = 0

        while True:
            ok, frame = capture.read()
            if not ok:
                break

            if frame_index % self.speed_factor != 0:
                frame_index += 1
                continue

            scanned += 1
            timestamp_sec = frame_index / fps
            result = self.detector.detect(frame)

            if result.map_open:
                map_open_frames += 1
                closed_streak = 0

                should_capture = (
                    not map_is_open
                    or timestamp_sec - last_capture_timestamp >= self.min_capture_interval_sec
                )
                if should_capture:
                    capture_counter += 1
                    map_image = crop_map_region(frame, self.map_crop)
                    filename = (
                        f"{self.video_stem}_map_{capture_counter:03d}_"
                        f"{self._format_timestamp(timestamp_sec)}.{self.image_format}"
                    )
                    output_path = self.output_dir / filename
                    cv2.imwrite(str(output_path), map_image)
                    captures.append(
                        CaptureEvent(
                            timestamp_sec=timestamp_sec,
                            frame_index=frame_index,
                            output_path=output_path,
                            good_matches=result.good_matches,
                        )
                    )
                    last_capture_timestamp = timestamp_sec

                map_is_open = True
            else:
                closed_streak += 1
                if closed_streak >= self.closed_frames_required:
                    map_is_open = False

            frame_index += 1

        capture.release()
        return ProcessingStats(
            frames_scanned=scanned,
            map_open_frames=map_open_frames,
            captures=captures,
        )

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        total = int(seconds)
        hours, remainder = divmod(total, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}h{minutes:02d}m{secs:02d}s"
        return f"{minutes:02d}m{secs:02d}s"
