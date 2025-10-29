# utils/logger.py
import os
import errno
import logging
import sys
from Controle.config import LOGGER_LEVEL as level

FIFO_PATH = "/tmp/game_logs"

def criar_fifo():
    try:
        os.mkfifo(FIFO_PATH)
        print(f"FIFO criado em: {FIFO_PATH}")
    except OSError as oe:
        if oe.errno != errno.EEXIST:
            raise
        print(f"FIFO já existe em: {FIFO_PATH}")

class FifoHandler(logging.Handler):
    def __init__(self, filename):
        try:
            self.fifo_file = open(filename, 'w')
        except FileNotFoundError:
             print(f"ERRO: FIFO não encontrado em {filename}. Ele precisa ser criado primeiro.", file=sys.stderr)
             self.fifo_file = None
        
        super().__init__()

    def emit(self, record):
        if self.fifo_file:
            log_entry = self.format(record)
            
            try:
                self.fifo_file.write(log_entry + '\n')
                self.fifo_file.flush()
            except Exception as e:
                print(f"ERRO ao escrever no FIFO: {e}", file=sys.stderr)
                self.fifo_file = None
            

def setup_logger(name: str) -> logging.Logger:
    """Function to set up a logger with the specified name and log file."""
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    
    # Create a logger
    logger = logging.getLogger(name)

    logger.setLevel(level)

    # Create file handler which logs even debug messages
    fh = logging.FileHandler(FIFO_PATH)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    
    # Create console handler with a higher log level
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.ERROR)
    # ch.setFormatter(formatter)

    # Add the handlers to the logger
    if not logger.hasHandlers():
        logger.addHandler(fh)
        # logger.addHandler(ch)

    return logger

if __name__ == "__main__":
    # Example usage
    #criar_fifo()
    logger = setup_logger('example_logger')
    logger.info("This is an info message.")
    logger.error("This is an error message.")
    logger.warning("This is a warning message.")
    logger.debug("This is a debug message.")
    logger.critical("This is a critical message.")

    vision = setup_logger('vision_logger')
    vision.info("This is an info message from vision logger.")
    vision.error("This is an error message from vision logger.")
    vision.warning("This is a warning message from vision logger.")
    vision.debug("This is a debug message from vision logger.")
    vision.critical("This is a critical message from vision logger.")

    control = setup_logger('control_logger')
    control.info("This is an info message from control logger.")
    control.error("This is an error message from control logger.")
    control.warning("This is a warning message from control logger.")
    control.debug("This is a debug message from control logger.")
    control.critical("This is a critical message from control logger.")