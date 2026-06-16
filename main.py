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

# ---------------------------------------------------------------------------
# Internal imports (populated after skeletons are implemented)
# ---------------------------------------------------------------------------
from utils.logger import get_logger
from utils.helpers import load_config
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
        self.source = source or config["video"]["source"]
        self.headless = headless

        # Pipeline modules – initialised in setup()
        self.detector: Optional[VehicleDetector] = None
        self.counter: Optional[VehicleCounter] = None
        self.analyzer: Optional[TrafficAnalyzer] = None
        self.controller: Optional[SignalController] = None
        self.predictor: Optional[CongestionPredictor] = None
        self.dashboard_data: Optional[DashboardData] = None

        logger.info("TrafficManagementApp initialised.")

    def setup(self) -> bool:
        """Initialise all pipeline modules and open the video source.

        Returns
        -------
        bool
            True if setup succeeded, False otherwise.
        """
        # TODO: Instantiate each module with the relevant config section.
        # TODO: Call detector.load_model() and detector.open_source(self.source).
        # TODO: Return False if any critical step fails.
        raise NotImplementedError("TODO: implement setup()")

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
        # TODO: Implement the main processing loop.
        # TODO: Log a summary at the end of the session.
        raise NotImplementedError("TODO: implement run()")

    def teardown(self) -> None:
        """Release resources (camera, DB connections, etc.).

        Called automatically at the end of run() or on KeyboardInterrupt.
        """
        # TODO: Call detector.release().
        # TODO: Close database connection in dashboard_data.
        # TODO: Log session end.
        raise NotImplementedError("TODO: implement teardown()")


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
