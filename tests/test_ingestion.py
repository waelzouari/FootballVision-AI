from __future__ import annotations

from dataclasses import dataclass

import pytest

from ingestion.video import OpenCVVideoReader


@dataclass
class FakeImage:
    shape: tuple[int, int, int] = (720, 1280, 3)


class FakeCapture:
    def __init__(self, frames: list[FakeImage], *, fps: float = 25.0, opened: bool = True):
        self.frames = iter(frames)
        self.fps = fps
        self.opened = opened
        self.released = False
        self.read_count = 0

    def isOpened(self):
        return self.opened

    def get(self, property_id):
        return {3: 1280, 4: 720, 5: self.fps, 7: 2, 0: self.read_count * 40}.get(property_id, 0)

    def read(self):
        try:
            image = next(self.frames)
        except StopIteration:
            return False, None
        self.read_count += 1
        return True, image

    def release(self):
        self.released = True


def test_frames_expose_source_relative_metadata_and_release_capture():
    capture = FakeCapture([FakeImage(), FakeImage()])
    reader = OpenCVVideoReader("clip.mp4", capture_factory=lambda _: capture)

    frames = list(reader.frames())

    assert [(item.packet.frame_index, item.packet.timestamp_s) for item in frames] == [(0, 0.04), (1, 0.08)]
    assert frames[0].packet.width == 1280
    assert capture.released


def test_invalid_fps_is_rejected():
    capture = FakeCapture([], fps=0)
    reader = OpenCVVideoReader("clip.mp4", capture_factory=lambda _: capture)

    with pytest.raises(ValueError, match="invalid FPS"):
        list(reader.frames())
    assert capture.released
