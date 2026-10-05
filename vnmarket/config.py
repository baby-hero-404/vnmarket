"""Configuration settings for vnmarket library."""

import logging


class Config:
    # -------------------------------------------------------------------------
    # HTTP request settings
    # -------------------------------------------------------------------------
    # Default timeout (in seconds) for any network request
    REQUEST_TIMEOUT: int = 30

    # Number of retry attempts on transient failures
    RETRIES: int = 3

    # Tenacity backoff strategy parameters
    BACKOFF_MULTIPLIER: float = 1.0
    BACKOFF_MIN: float = 2  # minimum wait between retries (seconds)
    BACKOFF_MAX: float = 10  # maximum wait between retries (seconds)

    # -------------------------------------------------------------------------
    # Block detection (CDN / WAF)
    # -------------------------------------------------------------------------
    BLOCK_DETECTION_ENABLED: bool = True
    BODY_SNIFF_LIMIT: int = 8192
    RETRY_AFTER_MAX_WAIT: float = 30.0

    # -------------------------------------------------------------------------
    # Per-host circuit breaker
    # -------------------------------------------------------------------------
    CIRCUIT_BREAKER_ENABLED: bool = True
    BLOCK_COOLDOWN_RATE_LIMIT: float = 60.0
    BLOCK_COOLDOWN_CHALLENGE: float = 300.0
    BLOCK_COOLDOWN_DENIED: float = 300.0
    BLOCK_COOLDOWN_MIN: float = 5.0
    BLOCK_COOLDOWN_MAX: float = 900.0
    CIRCUIT_MAX_ENTRIES: int = 256

    # -------------------------------------------------------------------------
    # Caching
    # -------------------------------------------------------------------------
    CACHE_SIZE: int = 128

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    LOG_LEVEL: int = logging.INFO

    @classmethod
    def apply_logging_config(cls):
        """Configure vnmarket logging."""
        logging.getLogger("vnmarket").setLevel(cls.LOG_LEVEL)
