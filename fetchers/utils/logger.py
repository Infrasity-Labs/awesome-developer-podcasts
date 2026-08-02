import logging
from typing import Union


logger = logging.getLogger("Awesome-developer-podcast")

_LOG_FORMAT = '%(asctime)s - %(levelname)s [%(name)s] %(message)s'
_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def configure_logger(level: Union[int, str] = logging.INFO):
    logging.basicConfig(
        level=level,
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
        force=True,
    )


def set_logging_level(logging_lvl: int) -> bool:
    """ Sets the logger level.

    Returns False if the level is invalid, falls back to INFO.
    Returns True on success.
    """
    available_lvls = (
        logging.DEBUG,
        logging.CRITICAL,
        logging.ERROR,
        logging.INFO,
        logging.WARNING,
    )

    if logging_lvl not in available_lvls:
        logger.warning(f"Invalid logging level {logging_lvl!r}. Falling back to INFO.")
        logger.setLevel(logging.INFO)
        return False

    logger.setLevel(logging_lvl)
    logger.debug(f"Logging level set to {logging.getLevelName(logging_lvl)}")
    return True
