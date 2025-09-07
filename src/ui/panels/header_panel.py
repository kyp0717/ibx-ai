"""
Header panel with integrated status bar
"""

from datetime import datetime
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table


class HeaderPanel:
    def __init__(self):
        self.title = "IBX AI Trading Terminal"
    
    def render(self, connected: bool = False, order_id: int = 0, port: int = 7500):
        """Render the header panel with status information"""
        
        header_table = Table(show_header=False, box=None, padding=0, expand=True)
        header_table.add_column(justify="center")
        
        title_text = Text(self.title, style="bold cyan", justify="center")
        header_table.add_row(title_text)
        
        status_parts = []
        
        if connected:
            status_parts.append(("● Active", "green"))
        else:
            status_parts.append(("● Disconnected", "red"))
        
        status_parts.append((f"Order ID: {order_id}", "white"))
        status_parts.append((datetime.now().strftime("Time: %H:%M:%S"), "white"))
        status_parts.append((f"Port: {port}", "white"))
        
        status_text = Text()
        for i, (text, color) in enumerate(status_parts):
            if i > 0:
                status_text.append(" | ", style="dim white")
            if i == 0:
                status_text.append("Connection: ", style="white")
                status_text.append(text, style=color)
            else:
                status_text.append(text, style=color)
        
        header_table.add_row(Align.center(status_text))
        
        return Panel(
            header_table,
            style="bold white on blue",
            border_style="blue"
        )