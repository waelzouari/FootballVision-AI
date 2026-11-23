"""Video ingestion with explicit, source-relative timestamps.

OpenCV remains an optional runtime dependency so schema and unit tests can run
without downloading or installing video packages.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from contracts.schemas import FramePacket


class Capture(Protocol):
    """Subset of OpenCV's VideoCapture used by :class:`OpenCVVideoReader`."""

    def isOpened(self) -> bool: ...

    def get(self, property_id: int) -> float: ...

    def read(self) -> tuple[bool, Any]: ...

    def release(self) -> None: ...


@dataclass(frozen=True)
class VideoInfo:
    source_id: str
    width: int
    height: int
    fps: float
    frame_count: int | None


@dataclass(frozen=True)
class VideoFrame:
    """A decoded image paired with the contract-safe frame metadata."""

    packet: FramePacket
    image: Any


class OpenCVVideoReader:
    """Read an MP4 or camera source without putting image arrays in contracts."""

    def __init__(
        self,
        source: str | int | Path,
        *,
        capture_factory: Callable[[str | int], Capture] | None = None,
        source_id: str | None = None,
    ) -> None:
        self._source = str(source) if isinstance(source, Path) else source
        self._capture_factory = capture_factory
        self.source_id = source_id or str(source)

    def _open(self) -> tuple[Capture, tuple[int, int, int, int, int]]:
        if self._capture_factory is None:
            try:
                import cv2
            except ImportError as exc:  # pragma: no cover - environment dependent
                raise RuntimeError(
                    "OpenCV is required for video ingestion; install footballvision[video]."
                ) from exc
            factory: Callable[[str | int], Capture] = cv2.VideoCapture
            properties = (
                cv2.CAP_PROP_FRAME_WIDTH,
                cv2.CAP_PROP_FRAME_HEIGHT,
                cv2.CAP_PROP_FPS,
                cv2.CAP_PROP_FRAME_COUNT,
                cv2.CAP_PROP_POS_MSEC,
            )
        else:
            factory = self._capture_factory
            # OpenCV's public numeric IDs allow simple fake captures in tests.
            properties = (3, 4, 5, 7, 0)
        capture = factory(self._source)
        if not capture.isOpened():
            capture.release()
            raise ValueError(f"Cannot open video source: {self.source_id}")
        return capture, properties

    def info(self) -> VideoInfo:
        capture, (width_id, height_id, fps_id, count_id, _) = self._open()
        try:
            frame_count = int(capture.get(count_id))
            return VideoInfo(
                source_id=self.source_id,
                width=int(capture.get(width_id)),
                height=int(capture.get(height_id)),
                fps=float(capture.get(fps_id)),
                frame_count=frame_count if frame_count > 0 else None,
            )
        finally:
            capture.release()

    def frames(self) -> Iterator[VideoFrame]:
        capture, (_, _, fps_id, _, position_ms_id) = self._open()
        fps = float(capture.get(fps_id))
        if fps <= 0:
            capture.release()
            raise ValueError(f"Video source has invalid FPS: {self.source_id}")
        frame_index = 0
        try:
            while True:
                ok, image = capture.read()
                if not ok:
                    return
                height, width = image.shape[:2]
                timestamp_s = float(capture.get(position_ms_id)) / 1000.0
                if timestamp_s <= 0 and frame_index > 0:
                    timestamp_s = frame_index / fps
                yield VideoFrame(
                    packet=FramePacket(
                        frame_index=frame_index,
                        timestamp_s=timestamp_s,
                        width=int(width),
                        height=int(height),
                    ),
                    image=image,
                )
                frame_index += 1
        finally:
            capture.release()
