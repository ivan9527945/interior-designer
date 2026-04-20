import logging
import os

import structlog


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer() if os.isatty(1) else structlog.processors.JSONRenderer(),
        ]
    )
