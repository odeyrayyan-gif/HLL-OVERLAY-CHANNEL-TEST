"""Hell Let Loose map detection from YouTube / local video frames."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VALID_TEMPLATE_HEIGHTS = {1080, 1200, 1440}


@dataclass
class DetectionResult:
    map_open: bool
    good_matches: int


class HLLMapDetector:
    """Detect when the HLL tactical map is open using ORB feature matching."""

    def __init__(
        self,
        templates_dir: Path,
        template_height: int = 1080,
        num_features: int = 500,
        min_good_matches: int = 12,
    ) -> None:
        if template_height not in VALID_TEMPLATE_HEIGHTS:
            raise ValueError(
                f"template_height must be one of {sorted(VALID_TEMPLATE_HEIGHTS)}"
            )

        self.template_height = template_height
        self.min_good_matches = min_good_matches
        self.templates_dir = templates_dir

        resolution_dir = templates_dir / f"{template_height}p"
        mask_path = templates_dir / f"mask-{template_height}p.png"
        if not resolution_dir.is_dir() or not mask_path.is_file():
            raise FileNotFoundError(
                f"Missing templates for {template_height}p in {templates_dir}"
            )

        self._mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if self._mask is None:
            raise RuntimeError(f"Could not read mask: {mask_path}")

        self._detector = cv2.ORB_create(
            nfeatures=num_features,
            scoreType=cv2.ORB_FAST_SCORE,
            nlevels=1,
            fastThreshold=10,
        )
        self._matcher = cv2.BFMatcher(cv2.NORM_HAMMING)

        self._template_descriptors: list[np.ndarray] = []
        for image_path in sorted(resolution_dir.iterdir()):
            if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
                continue
            gray = cv2.cvtColor(cv2.imread(str(image_path)), cv2.COLOR_BGR2GRAY)
            _, descriptors = self._detector.detectAndCompute(gray, None)
            if descriptors is not None:
                self._template_descriptors.append(descriptors)

        if not self._template_descriptors:
            raise RuntimeError(f"No template images found in {resolution_dir}")

    def _scale_frame_to_template_height(self, frame: np.ndarray) -> tuple[np.ndarray, float]:
        height, width = frame.shape[:2]
        if height == self.template_height:
            return frame, 1.0

        scale = self.template_height / height
        new_width = int(round(width * scale))
        resized = cv2.resize(frame, (new_width, self.template_height), interpolation=cv2.INTER_AREA)
        return resized, scale

    @staticmethod
    def _count_good_matches(matches: list[list[cv2.DMatch]], min_required: int) -> int:
        good: list[cv2.DMatch] = []
        for pair in matches:
            if len(pair) < 2:
                continue
            best, second = pair
            if best.distance < 0.75 * second.distance:
                good.append(best)
                if len(good) >= min_required:
                    break
        return len(good)

    def detect(self, frame: np.ndarray) -> DetectionResult:
        scaled_frame, _ = self._scale_frame_to_template_height(frame)
        masked = cv2.bitwise_and(scaled_frame, scaled_frame, mask=self._mask)
        gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
        _, frame_descriptors = self._detector.detectAndCompute(gray, self._mask)

        if frame_descriptors is None:
            return DetectionResult(map_open=False, good_matches=0)

        best_matches = 0
        map_open = False
        for template_descriptors in self._template_descriptors:
            matches = self._matcher.knnMatch(frame_descriptors, template_descriptors, k=2)
            good_count = self._count_good_matches(matches, self.min_good_matches)
            best_matches = max(best_matches, good_count)
            if good_count >= self.min_good_matches:
                map_open = True
                break

        return DetectionResult(map_open=map_open, good_matches=best_matches)


def crop_map_region(frame: np.ndarray, crop: dict[str, float]) -> np.ndarray:
    height, width = frame.shape[:2]
    x = int(width * crop["left"])
    y = int(height * crop["top"])
    w = int(width * crop["width"])
    h = int(height * crop["height"])
    x = max(0, min(x, width - 1))
    y = max(0, min(y, height - 1))
    w = max(1, min(w, width - x))
    h = max(1, min(h, height - y))
    return frame[y : y + h, x : x + w]
