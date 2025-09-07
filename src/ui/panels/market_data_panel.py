"""
Market data panel displaying symbol, price, and volume information
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Dict, Any


class MarketDataPanel:
    def __init__(self):
        pass
    
    def render(self, data: Dict[str, Any]) -> Panel:
        """Render the market data panel"""
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Label", style="dim white", width=12)
        table.add_column("Value", style="white")
        
        if not data or not data.get("symbol"):
            table.add_row("", "No market data available")
            return Panel(
                table,
                title="MARKET DATA",
                title_align="center",
                border_style="cyan",
                style="on black"
            )
        
        symbol = data.get("symbol", "N/A")
        last_price = data.get("last_price", 0)
        change = data.get("change", 0)
        change_pct = data.get("change_pct", 0)
        
        table.add_row("Symbol:", Text(symbol, style="bold cyan"))
        
        price_style = "green" if change >= 0 else "red"
        arrow = "▲" if change >= 0 else "▼"
        sign = "+" if change >= 0 else ""
        
        price_text = Text()
        price_text.append(f"${last_price:.2f} ", style="bold white")
        price_text.append(f"{arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)", style=price_style)
        table.add_row("Last:", price_text)
        
        bid_price = data.get("bid_price", 0)
        bid_size = data.get("bid_size", 0)
        table.add_row("Bid:", f"${bid_price:.2f} x {bid_size}")
        
        ask_price = data.get("ask_price", 0)
        ask_size = data.get("ask_size", 0)
        table.add_row("Ask:", f"${ask_price:.2f} x {ask_size}")
        
        volume = data.get("volume", 0)
        table.add_row("Volume:", f"{volume:,}")
        
        high = data.get("high", 0)
        low = data.get("low", 0)
        table.add_row("Day Range:", f"{low:.2f} - {high:.2f}")
        
        table.add_row("", "")
        
        table.add_row("High:", f"${high:.2f}")
        table.add_row("Low:", f"${low:.2f}")
        table.add_row("Open:", f"${data.get('open', 0):.2f}")
        table.add_row("Close:", f"${data.get('close', 0):.2f}")
        
        return Panel(
            table,
            title="MARKET DATA",
            title_align="center",
            border_style="cyan",
            style="on black"
        )