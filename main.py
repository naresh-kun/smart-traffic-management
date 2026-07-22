"""
Smart Traffic Management System
================================
Entry point for the application.

Orchestrates the full processing pipeline:
  VideoSource → VehicleDetector → VehicleCounter → TrafficAnalyzer
              → CongestionPredictor → SignalController → DashboardData

Usage
-----
  python main.py                              # webcam (default)
  python main.py --source data/videos/x.mp4  # video file
  python main.py --headless                   # no OpenCV window
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import cv2

# ---------------------------------------------------------------------------
# Internal imports (populated after skeletons are implemented)
# ---------------------------------------------------------------------------
from utils.logger import get_logger, setup_logging
from utils.helpers import load_config, ensure_dir, get_config_value
from modules.vehicle_detector import VehicleDetector
from modules.vehicle_counter import VehicleCounter
from modules.traffic_analyzer import TrafficAnalyzer
from modules.signal_controller import SignalController
from modules.congestion_predictor import CongestionPredictor
from modules.dashboard_data import DashboardData

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser with all supported flags.
    """
    parser = argparse.ArgumentParser(
        description="Smart Traffic Management System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Video source: integer for webcam index or path to a video file.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Disable the OpenCV display window.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to the YAML configuration file.",
    )
    return parser


# ---------------------------------------------------------------------------
# Application class
# ---------------------------------------------------------------------------

class TrafficManagementApp:
    """Top-level orchestrator for the Smart Traffic Management System.

    Wires together all pipeline modules and runs the main processing loop.
    Designed to be replaceable with an async/multi-intersection variant
    in future iterations.

    Parameters
    ----------
    config : dict
        Loaded configuration dictionary from config.yaml.
    source : Optional[str]
        Override video source (webcam index or file path). When None the
        value from config is used.
    headless : bool
        When True, no OpenCV window is displayed.
    """

    def __init__(
        self,
        config: dict,
        source: Optional[str] = None,
        headless: bool = False,
    ) -> None:
        self.config = config
        self.source = source if source is not None else config["video"]["source"]
        self.headless = headless

        # Pipeline modules – initialised in setup()
        self.detector: Optional[VehicleDetector] = None
        self.counter: Optional[VehicleCounter] = None
        self.analyzer: Optional[TrafficAnalyzer] = None
        self.controller: Optional[SignalController] = None
        self.predictor: Optional[CongestionPredictor] = None
        self.dashboard_data: Optional[DashboardData] = None
        self._teardown_done: bool = False

        logger.info("TrafficManagementApp initialised.")

    def setup(self) -> bool:
        """Initialise all pipeline modules and open the video source.

        Returns
        -------
        bool
            True if setup succeeded, False otherwise.
        """
        log_dir = get_config_value(self.config, "logging", "log_dir", default="data/logs")
        ensure_dir(log_dir)
        ensure_dir("data/videos")
        ensure_dir("data/results")

        self.detector = VehicleDetector(self.config)

        if not self.detector.load_model():
            logger.error("Failed to load YOLO model.")
            return False

        if not self.detector.open_source(self.source):
            logger.error(f"Failed to open video source: {self.source}")
            return False

        width, height = self.detector.get_frame_dimensions()
        logger.info(
            f"Setup complete. Source={self.source!r}, "
            f"resolution={width}x{height}."
        )
        return True

    def run(self) -> None:
        """Run the main frame-processing loop until the source is exhausted
        or the user presses 'q'.

        Pipeline per frame
        ------------------
        1. detector.read_frame()
        2. detector.detect_frame()
        3. counter.update()
        4. analyzer.generate_metrics()
        5. predictor.predict() (if ready)
        6. controller.calculate_timings()
        7. dashboard_data.update()
        8. Optional: display annotated frame
        """
        if self.detector is None:
            logger.error("Cannot run: detector not initialised. Call setup() first.")
            return

        logger.info("Starting processing loop. Press 'q' to exit.")
        frames_processed = 0
        window_name = "Smart Traffic Management"

        if not self.headless:
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while self.detector.is_open:
            ret, frame = self.detector.read_frame()
            if not ret or frame is None:
                logger.info("End of video stream or error reading frame.")
                break

            detections = self.detector.detect_frame(frame)

            if detections:
                logger.debug(
                    f"Frame {self.detector.frame_id}: "
                    f"{len(detections)} vehicle(s) detected."
                )

            if not self.headless:
                annotated = self.detector.annotate_frame(frame, detections)
                cv2.imshow(window_name, annotated)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Exit requested by user.")
                    break

            frames_processed += 1

        logger.info(f"Session ended. Processed {frames_processed} frames.")

    def teardown(self) -> None:
        """Release resources (camera, DB connections, etc.).

        Called automatically at the end of run() or on KeyboardInterrupt.
        Safe to call multiple times.
        """
        if self._teardown_done:
            return

        if self.detector is not None:
            self.detector.release()
            self.detector = None

        if not self.headless:
            cv2.destroyAllWindows()

        self._teardown_done = True
        logger.info("Application teardown complete.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments, load config, and start the application."""
    parser = build_arg_parser()
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    config = load_config(str(config_path))

    setup_logging(
        level=get_config_value(config, "logging", "level", default="INFO"),
        log_dir=get_config_value(config, "logging", "log_dir", default="data/logs"),
        log_file=get_config_value(config, "logging", "log_file", default="traffic_system.log"),
        rotation=get_config_value(config, "logging", "rotation", default="10 MB"),
        retention=get_config_value(config, "logging", "retention", default="7 days"),
    )

    app = TrafficManagementApp(
        config=config,
        source=args.source,
        headless=args.headless,
    )

    try:
        if not app.setup():
            logger.error("Setup failed. Exiting.")
            sys.exit(1)
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        app.teardown()


if __name__ == "__main__":
    main()
