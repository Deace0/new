import os
import logging


def create_log_directory(log_dir):
    """
    Creates the log directory if it does not exist.

    Args:
       log_dir (str): The directory where logs should be saved.
    """
    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Created logs directory at {log_dir}")
        else:
            print(f"Log directory already exists at {log_dir}")
    except OSError as e:
        print(f"Error creating log directory: {e}")
        raise


def configure_logging(log_dir, log_file="log.log"):
    """
    Configures and returns a logger.

    Args:
       log_dir (str): The directory where logs should be saved.
       log_file (str): The log file name. Defaults to 'log.log'.
    """
    log_path = os.path.join(log_dir, log_file)
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log_warning(message):
    """
    Logs a warning message.

    Args:
       message (str): The message to log as a warning.
    """
    logger = logging.getLogger(__name__)
    logger.warning(message)
