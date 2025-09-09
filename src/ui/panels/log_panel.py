"""
Log panel to display log messages at the bottom of the terminal
"""

from rich.panel import Panel
from rich.table import Table
from typing import List, Dict, Any


class LogPanel:
    def __init__(self):
        self.title = "Log"
    
    def render(self, log_messages: List[Dict[str, Any]] = None):
        """Render the log panel with the latest 10 messages"""
        
        # Create table for log messages
        log_table = Table(show_header=False, box=None, padding=0, expand=True)
        log_table.add_column("Log", style="white")
        
        if log_messages:
            # Display only the latest 10 messages
            recent_logs = log_messages[-10:] if len(log_messages) > 10 else log_messages
            for log in recent_logs:
                time_str = log.get("time", "")
                message = log.get("message", "")
                # Format with single space between time and message (no log type)
                log_entry = f"{time_str} {message}"
                log_table.add_row(log_entry)
        else:
            log_table.add_row("No log messages")
        
        return Panel(
            log_table,
            title="Log",
            title_align="left",
            border_style="cyan",
            height=12
        )