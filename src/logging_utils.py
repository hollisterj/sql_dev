import logging
import sys
from pathlib import Path
from datetime import datetime
import re

def sanitize_label(label: str, replacement: str = "_") -> str:
    """
    Sanitizes a string to be safely used as a filename across Windows, macOS, and Linux.
    Additionally, replace '.' with the specified replacement character.
    """
    if not label:
        return "unnamed_file"

    # 1. Strip out illegal characters and control characters
    # Windows forbids: < > : " / \ | ? *
    # Unix forbids: / and null bytes (\x00)
    # \x00-\x1F handles invisible control characters (like tabs or newlines)
    illegal_chars_pattern = r'[.<>:"/\\|?*\x00-\x1F]'
    sanitized = re.sub(illegal_chars_pattern, replacement, str(label))

    # 2. Windows does not allow filenames to end with a space or a period.
    sanitized = sanitized.strip(". ")

    # Fallback if the label was entirely illegal characters and got stripped away
    return sanitized if sanitized else "unnamed_file"

class Logger:
    """
    A logging utility with both console and file stream handlers.
    Automatically creates an output folder for log files.
    """

    def __init__(self,
                 log_dir: str = './logs',
                 name: str = __name__,
                 label: str = None
            ):
        """
        Initialize the logger with console and file handlers.
        
        Args:
            name: Logger name (typically __name__)
            label: Optional label for the logger.
        """
        # Create output directory if it doesn't exist
        Path(log_dir).mkdir(exist_ok=True)
        
        # Set up logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '[%(asctime)s][%(name)s][%(funcName)s][%(levelname)s][%(message)s]',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler (INFO level and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (DEBUG level and above)
        log_file = f"{sanitize_label(label)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        log_path = Path(log_dir) / log_file
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self.logger.addHandler(file_handler)
        
        self.log_path = log_path
    
    def debug(self, msg: str):
        self.logger.debug(msg, stacklevel=2)
    
    def info(self, msg: str):
        self.logger.info(msg, stacklevel=2)
    
    def warning(self, msg: str):
        self.logger.warning(msg, stacklevel=2)
    
    def error(self, msg: str):
        self.logger.error(msg, stacklevel=2)
    
    def critical(self, msg: str):
        self.logger.critical(msg, stacklevel=2)