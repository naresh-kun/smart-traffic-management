"""
tests/test_main.py
------------------
Unit tests for the top-level ``TrafficManagementApp`` in ``main.py``.
"""

from unittest.mock import MagicMock, patch

import pytest
import numpy as np

from main import TrafficManagementApp


@pytest.fixture
def minimal_config() -> dict:
    return {
        "video": {"source": "test.mp4"},
        "logging": {"log_dir": "data/logs_test"}
    }


class TestTrafficManagementApp:
    def test_init_sets_attributes(self, minimal_config):
        """Test the app initializes correctly with config and arguments."""
        app = TrafficManagementApp(minimal_config, source=0, headless=True)
        assert app.config == minimal_config
        assert app.source == 0
        assert app.headless is True
        assert app.detector is None

    @patch("main.ensure_dir")
    @patch("main.VehicleDetector")
    def test_setup_success(self, mock_detector_cls, mock_ensure_dir, minimal_config):
        """Test setup() succeeds when dependencies load correctly."""
        mock_detector = MagicMock()
        mock_detector.load_model.return_value = True
        mock_detector.open_source.return_value = True
        mock_detector.get_frame_dimensions.return_value = (1280, 720)
        mock_detector_cls.return_value = mock_detector

        app = TrafficManagementApp(minimal_config, headless=True)
        result = app.setup()

        assert result is True
        assert app.detector == mock_detector
        assert mock_ensure_dir.call_count == 3
        mock_ensure_dir.assert_any_call("data/logs_test")
        mock_ensure_dir.assert_any_call("data/videos")
        mock_ensure_dir.assert_any_call("data/results")
        mock_detector.load_model.assert_called_once()
        mock_detector.open_source.assert_called_once_with("test.mp4")

    @patch("main.ensure_dir")
    @patch("main.VehicleDetector")
    def test_setup_failure_model(self, mock_detector_cls, mock_ensure_dir, minimal_config):
        """Test setup() fails if model loading fails."""
        mock_detector = MagicMock()
        mock_detector.load_model.return_value = False
        mock_detector_cls.return_value = mock_detector

        app = TrafficManagementApp(minimal_config, headless=True)
        result = app.setup()

        assert result is False
        mock_detector.open_source.assert_not_called()

    @patch("main.ensure_dir")
    @patch("main.VehicleDetector")
    def test_setup_failure_source(self, mock_detector_cls, mock_ensure_dir, minimal_config):
        """Test setup() fails if the video source cannot be opened."""
        mock_detector = MagicMock()
        mock_detector.load_model.return_value = True
        mock_detector.open_source.return_value = False
        mock_detector_cls.return_value = mock_detector

        app = TrafficManagementApp(minimal_config, headless=True)
        result = app.setup()

        assert result is False
        mock_detector.load_model.assert_called_once()
        mock_detector.open_source.assert_called_once_with("test.mp4")

    @patch("main.cv2")
    def test_run_headless(self, mock_cv2, minimal_config):
        """Test run() processes frames and exits without cv2 window functions if headless."""
        app = TrafficManagementApp(minimal_config, headless=True)
        app.detector = MagicMock()

        blank_frame = np.zeros((10, 10, 3), dtype=np.uint8)
        app.detector.read_frame.side_effect = [(True, blank_frame), (True, blank_frame), (False, None)]
        app.detector.detect_frame.return_value = []
        app.detector.is_open = True

        app.run()

        assert app.detector.read_frame.call_count == 3
        assert app.detector.detect_frame.call_count == 2
        mock_cv2.namedWindow.assert_not_called()
        mock_cv2.imshow.assert_not_called()

    @patch("main.cv2")
    def test_run_without_detector(self, mock_cv2, minimal_config):
        """Test run() exits early when setup was not completed."""
        app = TrafficManagementApp(minimal_config, headless=False)

        app.run()

        mock_cv2.namedWindow.assert_not_called()
        mock_cv2.imshow.assert_not_called()

    @patch("main.cv2")
    def test_run_with_display_quit(self, mock_cv2, minimal_config):
        """Test run() processes frames with display and exits on 'q'."""
        app = TrafficManagementApp(minimal_config, headless=False)
        app.detector = MagicMock()

        blank_frame = np.zeros((10, 10, 3), dtype=np.uint8)
        app.detector.read_frame.return_value = (True, blank_frame)
        app.detector.detect_frame.return_value = []
        app.detector.annotate_frame.return_value = blank_frame
        app.detector.is_open = True

        mock_cv2.waitKey.side_effect = [-1, -1, ord("q")]

        app.run()

        mock_cv2.namedWindow.assert_called_once()
        assert app.detector.read_frame.call_count == 3
        assert app.detector.annotate_frame.call_count == 3
        assert mock_cv2.imshow.call_count == 3

    @patch("main.cv2")
    def test_teardown(self, mock_cv2, minimal_config):
        """Test teardown releases resources."""
        app = TrafficManagementApp(minimal_config, headless=False)
        mock_detector = MagicMock()
        app.detector = mock_detector

        app.teardown()

        mock_detector.release.assert_called_once()
        mock_cv2.destroyAllWindows.assert_called_once()
        assert app.detector is None

    @patch("main.cv2")
    def test_teardown_idempotent(self, mock_cv2, minimal_config):
        """Test repeated teardown calls do not raise or double-release."""
        app = TrafficManagementApp(minimal_config, headless=False)
        mock_detector = MagicMock()
        app.detector = mock_detector

        app.teardown()
        app.teardown()

        mock_detector.release.assert_called_once()
        mock_cv2.destroyAllWindows.assert_called_once()
        assert app.detector is None
        assert app._teardown_done is True
