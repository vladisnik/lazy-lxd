import sys
import logging
from colorama import Fore


def init(debug_level: bool = False) -> None:
    """
    Initialize logging for messaging.

    Args:
        debug_level (bool): Flag about verbose output.
                            Use DEBUG level as default if setted.
    """

    class MsgFormatter(logging.Formatter):
        """
        Coloring message according to level.
        """

        COLOR_AND_FORMAT = {
            logging.DEBUG: f"{Fore.LIGHTYELLOW_EX}VERBOSE ",
            logging.INFO: Fore.RESET,
            logging.WARNING: Fore.LIGHTMAGENTA_EX,
            logging.ERROR: Fore.RED
        }

        def format(self, record):
            msg = super(MsgFormatter, self).format(record)
            return f"{MsgFormatter.COLOR_AND_FORMAT[record.levelno]}{msg}"

    class MsgFilter(logging.Filter):
        """
        Filtering message above than ERROR level.
        """
        def filter(self, record):
            if record.levelno < logging.ERROR:
                return True

    log_level = logging.DEBUG if debug_level else logging.INFO
    logger = logging.getLogger('lazy_lxd')
    logger.setLevel(log_level)

    out_lh = logging.StreamHandler(sys.stdout)
    out_lh.setLevel(log_level)
    out_lh.addFilter(MsgFilter())
    out_lh.setFormatter(MsgFormatter("%(msg)s"))

    err_lh = logging.StreamHandler(sys.stderr)
    err_lh.setLevel(logging.ERROR)
    err_lh.setFormatter(MsgFormatter("%(levelname)s %(msg)s"))

    logger.addHandler(err_lh)
    logger.addHandler(out_lh)
