"""Runtime log visibility controls shared by CLI commands."""

from loguru import logger

__all__ = ["_set_saba_logs"]


def _set_saba_logs(enabled: bool) -> None:
    if enabled:
        logger.enable("saba")
    else:
        logger.disable("saba")
