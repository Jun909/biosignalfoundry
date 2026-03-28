import logging
import sys

import structlog


def setup_logging(log_level: str = "INFO", render_json: bool = False) -> None:
    """
    Configure structlog for the application.

    Args:
        log_level: Minimum log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        render_json: If True, emit JSON lines (use in production/cloud).
                     If False, emit human-readable coloured output (use in dev).
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if render_json:
        # Production: machine-parseable JSON, one line per event.
        # Compatible with CloudWatch, GCP Logging, Datadog, etc.
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        # Development: coloured, aligned, human-readable output.
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors
        + [
            # Prepare the event dict for the stdlib formatter so that
            # stdlib loggers (e.g. uvicorn, httpx) are merged into the
            # same pipeline.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # These processors run only on stdlib log records that were NOT
        # already processed by structlog (e.g. uvicorn's own log lines).
        foreign_pre_chain=shared_processors,
        processor=renderer,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    # Silence noisy third-party loggers.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
