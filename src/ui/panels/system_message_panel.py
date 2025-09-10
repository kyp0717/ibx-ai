"""
System message log panel for displaying trading events and notifications
"""

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from typing import List, Dict, Any


class SystemMessagePanel:
    def __init__(self, max_messages: int = 4):
        self.max_messages = max_messages
    
    def render(self, messages: List[Dict[str, Any]]) -> Panel:
        """Render the system message panel"""
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Time", style="dim cyan", width=10)
        table.add_column("Message", style="white")
        
        display_messages = messages[-self.max_messages:] if messages else []
        
        if not display_messages:
            table.add_row("", "Waiting for system messages...")
        else:
            for msg in display_messages:
                time_text = f"[{msg['time']}]"
                
                msg_style = "white"
                if msg['type'] == 'error':
                    msg_style = "red"
                elif msg['type'] == 'warning':
                    msg_style = "yellow"
                elif msg['type'] == 'success':
                    msg_style = "green"
                elif msg['type'] == 'info':
                    msg_style = "cyan"
                
                table.add_row(time_text, Text(msg['message'], style=msg_style))
        
        return Panel(
            table,
            title="SYSTEM MESSAGES",
            title_align="center",
            border_style="yellow",
            style="on black"
        )