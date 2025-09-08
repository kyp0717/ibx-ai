"""
Log panel for displaying logging messages
"""

from datetime import datetime
from typing import List, Dict, Any
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group


class LogPanel:
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
    
    def render(self, messages: List[Dict[str, Any]]) -> Panel:
        """Render the log panel with log messages"""
        
        if not messages:
            content = Align.center(
                Text("No log messages", style="dim italic"),
                vertical="middle"
            )
        else:
            text_lines = []
            for msg in messages[-self.max_messages:]:
                time_str = msg.get("time", "")
                level = msg.get("level", "INFO")
                message = msg.get("message", "")
                
                # Color based on log level
                if level == "ERROR":
                    style = "red"
                elif level == "WARNING":
                    style = "yellow"
                elif level == "DEBUG":
                    style = "dim white"
                else:
                    style = "white"
                
                line = Text()
                line.append(f"[{time_str}] ", style="dim cyan")
                line.append(f"{level:7} ", style=style)
                line.append(message[:50], style=style)  # Truncate long messages
                text_lines.append(line)
            
            content = Group(*text_lines) if text_lines else Text("No log messages", style="dim italic")
        
        return Panel(
            content,
            title="[bold cyan]LOG MESSAGES[/bold cyan]",
            border_style="cyan",
            padding=(0, 1)
        )