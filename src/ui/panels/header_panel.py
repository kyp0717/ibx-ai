"""
Header panel with integrated status bar and nested message panel
"""

from datetime import datetime
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.columns import Columns
from typing import List, Dict, Any


class HeaderPanel:
    def __init__(self):
        self.title = "IBX Trading"
    
    def render(self, connected: bool = False, order_id: int = 0, port: int = 7497,
               messages: List[Dict[str, Any]] = None):
        """Render the header panel with status information and nested message panel"""
        
        # Left side: Status information
        status_table = Table(show_header=False, box=None, padding=0, expand=True)
        status_table.add_column(justify="center")
        
        # Line 1: Blank space
        status_table.add_row("")
        
        # Line 2: Application title
        title_text = Text("IBX Trading", style="bold cyan", justify="center")
        status_table.add_row(title_text)
        
        # Line 3: Connection status
        conn_text = Text()
        if connected:
            conn_text.append("● Active on port ", style="green")
            conn_text.append(str(port), style="bold green")
        else:
            conn_text.append("● Disconnected", style="red")
        status_table.add_row(Align.center(conn_text))
        
        # Line 4: Order ID | System time
        info_text = Text()
        info_text.append("Order ID: ", style="white")
        info_text.append(str(order_id), style="bold yellow")
        info_text.append(" | ", style="dim white")
        info_text.append(datetime.now().strftime("%H:%M:%S"), style="cyan")
        status_table.add_row(Align.center(info_text))
        
        # Right side: TWS Message panel (fixed at 60 columns, justified right)
        msg_table = Table(show_header=False, box=None, padding=0, width=58)
        msg_table.add_column("Time", style="cyan", width=8)
        msg_table.add_column("Message", style="white", width=50)
        
        if messages:
            # Display the latest 4 system messages (these are TWS messages)
            recent_messages = messages[-4:] if len(messages) > 4 else messages
            for msg in recent_messages:
                time_str = msg.get("time", "")
                message = msg.get("message", "")
                # Truncate message if too long
                if len(message) > 50:
                    message = message[:47] + "..."
                # Add time and message as separate columns
                msg_table.add_row(time_str, message)
        else:
            msg_table.add_row("No TWS messages")
        
        msg_panel = Panel(
            msg_table,
            title="TWS Messages",
            title_align="center",
            border_style="dim cyan",
            height=6,
            width=60
        )
        
        # Combine both sides
        header_content = Columns([
            status_table,
            Align.right(msg_panel)
        ], expand=True, equal=False)
        
        return Panel(
            header_content,
            style="bold white on blue",
            border_style="blue",
            height=7
        )