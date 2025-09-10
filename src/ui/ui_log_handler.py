"""
Custom logging handler to redirect log messages to the UI
"""

import logging
from typing import Optional


class UILogHandler(logging.Handler):
    """Custom log handler that sends messages to the UI panel"""
    
    def __init__(self, ui=None):
        super().__init__()
        self.ui = ui
    
    def set_ui(self, ui):
        """Set the UI instance after creation"""
        self.ui = ui
    
    def emit(self, record):
        """Emit a log record to the UI"""
        if self.ui and hasattr(self.ui, 'add_log_message'):
            try:
                msg = self.format(record)
                # Remove timestamp from message since UI adds its own
                if ' - ' in msg:
                    parts = msg.split(' - ', 2)
                    if len(parts) >= 3:
                        msg = parts[2]  # Get message part after timestamp and logger name
                
                self.ui.add_log_message(msg, record.levelname)
            except Exception:
                # Silently ignore any errors to prevent logging loops
                pass