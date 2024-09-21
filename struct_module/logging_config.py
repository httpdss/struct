# FILE: struct_module/logging_config.py
import logging
import colorlog

def configure_logging(level=logging.INFO, log_file=None):
    """Configure logging with colorlog."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s][%(levelname)s][struct] >>> %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))

    logging.basicConfig(
        level=level,
        handlers=[handler],
    )

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s][%(levelname)s][struct] >>> %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logging.getLogger().addHandler(file_handler)
