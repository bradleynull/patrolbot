"""camera_unit_tests.py
Tests to confirm the camera sensor is working."""

import unittest
from patrolbot.sensors.camera.camera import VideoCamera


class TestCamera(unittest.TestCase):
    """Tests for the camera sensor."""

    def test_constructor(self):
        """Test that the camera can be successfully constructed."""
        cam = VideoCamera()
        self.assertNotEqual(cam, None)
        cam.release()

    def test_get_current_frame(self):
        """Test that a frame can be received from the camera."""
        cam = VideoCamera()
        frame = cam.get_current_frame()
        self.assertGreater(frame.shape[0], 0)
        self.assertGreater(frame.shape[1], 0)
        cam.release()

    def test_multithreaded(self):
        """Test that a frame is received when runnning in the multithreaded
        mode."""
        cam = VideoCamera(multithread=True)
        frame = cam.get_current_frame()
        self.assertGreater(frame.shape[0], 0)
        self.assertGreater(frame.shape[1], 0)
        cam.release()
