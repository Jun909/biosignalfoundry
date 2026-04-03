import logging
import sys

import structlog

_configured = False


def setup_logging(
    log_level: str = "INFO", render_json: bool = False
) -> structlog.stdlib.BoundLogger:
    """
    Configure structlog for the application and return a bound logger.

    Idempotent — safe to call from any module. Only the first call applies
    the configuration; subsequent calls skip setup and return a logger directly.

    Args:
        log_level: Minimum log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        render_json: If True, emit JSON lines (use in production/cloud).
                     If False, emit human-readable coloured output (use in dev).

    Returns:
        A structlog BoundLogger ready to use.

    Usage:
        logger = setup_logging(log_level="INFO", render_json=False)
        logger.info("app started", env="development")
    """
    global _configured

    if _configured:
        return structlog.get_logger()

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
        # ExceptionRenderer must come before JSONRenderer so that exc_info
        # is serialised into a structured dict rather than dropped.
        tail_processors: list[structlog.types.Processor] = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.ExceptionRenderer(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: coloured, aligned, human-readable output.
        # ConsoleRenderer handles exc_info natively.
        tail_processors = [
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

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
        processors=tail_processors,
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

    _configured = True
    return structlog.get_logger()
