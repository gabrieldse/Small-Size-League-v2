# utils/logger.py
import logging
import os


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """Function to set up a logger with the specified name and log file."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    fh.setFormatter(formatter)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    if not logger.hasHandlers():
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


if __name__ == "__main__":
    # Example usage
    logger = setup_logger("example_logger", "logs/example.log")
    logger.info("This is an info message.")
    logger.error("This is an error message.")
