
import logging
from datetime import datetime


class TerminalFormatter(logging.Formatter):
    RESET = "\033[0m"
    MUTED = "\033[38;2;137;148;167m"
    BLUE = "\033[38;2;57;121;237m"
    WHITE = "\033[38;2;241;245;249m"
    YELLOW = "\033[38;2;255;196;87m"
    RED = "\033[38;2;255;119;119m"
    BOLD = "\033[1m"

    LEVELS = {
        logging.DEBUG: ("DEBUG", MUTED),
        logging.INFO: ("INFO", BLUE),
        logging.WARNING: ("WARNING", YELLOW),
        logging.ERROR: ("ERROR", RED),
        logging.CRITICAL: ("CRITICAL", f"{BOLD}{RED}"),
    }

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime(
            "%H:%M:%S"
        )
        level, color = self.LEVELS.get(
            record.levelno,
            (record.levelname, self.WHITE),
        )

        logger_name = record.name
        message = record.getMessage()

        timestamp = f"{self.MUTED}{timestamp}{self.RESET}"
        level = f"{color}{level:<10}{self.RESET}"
        logger_name = f"{self.WHITE}{logger_name.upper():<15}{self.RESET}"
        message = f"{self.WHITE}{message}{self.RESET}"

        output = f"{timestamp} │ {level} │ {logger_name} │ {message}"

        if record.exc_info:
            output += "\n" + self.formatException(record.exc_info)

        if record.stack_info:
            output += "\n" + self.formatStack(record.stack_info)

        return output


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(TerminalFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)
