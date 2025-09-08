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
        self.title = "IBX Trading"
    
    def render(self, connected: bool = False, order_id: int = 0, port: int = 7497):
        """Render the header panel with status information"""
        
        header_table = Table(show_header=False, box=None, padding=0, expand=True)
        header_table.add_column(justify="center")
        
        title_text = Text("IBX Trading", style="bold cyan", justify="center")
        header_table.add_row(title_text)
        
        status_text = Text()
        
        # Connection status with port
        if connected:
            status_text.append("● Active on port ", style="green")
            status_text.append(str(port), style="bold green")
        else:
            status_text.append("● Disconnected", style="red")
        
        # Separator
        status_text.append(" | ", style="dim white")
        
        # Order ID
        status_text.append("Order ID: ", style="white")
        status_text.append(str(order_id), style="bold white")
        
        # Separator
        status_text.append(" | ", style="dim white")
        
        # System time
        status_text.append(datetime.now().strftime("%H:%M:%S"), style="white")
        
        header_table.add_row(Align.center(status_text))
        
        return Panel(
            header_table,
            style="bold white on blue",
            border_style="blue"
        )