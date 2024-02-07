
import logging
import sys
from colorama import init, Fore, Style
init()

# logging.basicConfig(format='[%(name)s:%(levelname)s] %(message)s', level=logging.DEBUG)

level = logging.INFO
for arg in sys.argv:
    if(arg == '-v'):
        level = logging.DEBUG

class CustomFormatter(logging.Formatter):

    format = "[%(name)s:%(levelname)s] %(message)s (%(filename)s:%(lineno)d)" if level == logging.DEBUG else \
        "[%(name)s:%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: Style.DIM + format + Style.RESET_ALL,
        logging.INFO: Fore.RESET + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + format + Style.RESET_ALL
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())

script_logger = logging.getLogger("shell-script")
script_logger.setLevel(level)
script_logger.addHandler(ch)

internal_logger = logging.getLogger("shell-init")
internal_logger.setLevel(level)
internal_logger.addHandler(ch)