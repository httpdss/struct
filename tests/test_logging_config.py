import pytest
import logging
from struct_module.logging_config import configure_logging

def test_configure_logging_default_level():
    configure_logging()
    logger = logging.getLogger()
    assert logger.level == logging.INFO

def test_configure_logging_debug_level():
    configure_logging(level=logging.DEBUG)
    logger = logging.getLogger()
    assert logger.level == logging.DEBUG

def test_configure_logging_with_log_file(tmp_path):
    log_file = tmp_path / "test.log"
    configure_logging(log_file=str(log_file))
    logger = logging.getLogger()
    logger.info("Test log message")
    with open(log_file, 'r') as f:
        log_content = f.read()
    assert "Test log message" in log_content
