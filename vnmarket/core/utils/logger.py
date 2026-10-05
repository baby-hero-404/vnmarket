import logging
import os
from logging.handlers import RotatingFileHandler


def advanced_logger(
    name,
    level="DEBUG",
    handler_type="stream",
    filename=None,
    log_format=None,
    date_format=None,
    max_bytes=10485760,
    backup_count=5,
):
    """
    Configure and return a customizable logger with various options.

    Parameters:
    - name: str - the logger's name. Example: 'api_logger'.
    - level: str - logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Example: 'INFO'.
    - handler_type: str - type of handler ('stream', 'file', 'rotating').
      'stream' will print to console, 'file' will write to a file, 'rotating' will write to a file with a max size and backup files. Example: 'rotating'.
    - filename: str - path to log file. Defaults to current directory if None provided. Example: '/var/logs/api.log'.
    - log_format: str - format of the log messages. Example: '%(asctime)s - %(levelname)s - %(message)s'.
    - date_format: str - format of the timestamp in log messages. Example: '%Y-%m-%d %H:%M:%S'.
    - max_bytes: int - maximum log file size in bytes (for 'rotating' handler). Example: 10485760 (10MB).
    - backup_count: int - number of backup files to keep (for 'rotating' handler). Example: 5.

    Returns:
    - logger: logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():  # Prevent adding multiple handlers if already configured
        logger.handlers.clear()

    # Set default file name if none provided
    if filename is None:
        filename = os.path.join(os.getcwd(), f"{name}.log")

    # Set default log format if not provided
    log_format = log_format or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = date_format or "%Y-%m-%d %H:%M:%S"

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Determine the handler type
    if handler_type == "file":
        handler = logging.FileHandler(filename)
    elif handler_type == "rotating":
        handler = RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count
        )
    else:  # Default to stream handler
        handler = logging.StreamHandler()

    # Set formatter and add handler to logger
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the logging level
    logger.setLevel(getattr(logging, level.upper()))

    return logger


_DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _ensure_package_logger() -> None:
    """Give the "vnmarket" logger a single console handler, once.

    Module loggers carry no handler of their own: they inherit this one and the
    level in ``Config.LOG_LEVEL``. ``propagate`` is off, so an application that
    configures the root logger does not see every record twice.
    """
    from vnmarket.config import Config

    pkg = logging.getLogger("vnmarket")
    if pkg.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT, _DEFAULT_DATE_FORMAT))
    pkg.addHandler(handler)
    pkg.propagate = False
    if pkg.level == logging.NOTSET:
        pkg.setLevel(Config.LOG_LEVEL)


def get_logger(
    name,
    level=None,
    handler_type="stream",
    filename=None,
    log_format=None,
    date_format=None,
    max_bytes=10485760,
    backup_count=5,
):
    """
    Return the logger for a module: ``get_logger(__name__)``.

    Called with just a name, the logger shares the package handler and follows
    ``Config.LOG_LEVEL``. Passing any other argument builds a dedicated logger
    with its own handler through ``advanced_logger`` (file, rotating, custom
    format or fixed level, which then defaults to DEBUG).

    Returns:
    - logger: logging.Logger instance.
    """
    customised = (
        level is not None
        or handler_type != "stream"
        or filename is not None
        or log_format is not None
        or date_format is not None
    )
    if not customised:
        _ensure_package_logger()
        return logging.getLogger(name)
    return advanced_logger(
        name=name,
        level=level or "DEBUG",
        handler_type=handler_type,
        filename=filename,
        log_format=log_format,
        date_format=date_format,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
