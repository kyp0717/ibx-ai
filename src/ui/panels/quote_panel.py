"""
Quote panel for displaying market quotes (bid/ask/last)
"""

from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from typing import Dict, Any, Union


class QuotePanel:
    def __init__(self):
        pass
    
    def render(self, market_data: Dict[str, Any], with_panel: bool = True) -> Union[Table, Panel]:
        """Render the quote panel with bid/ask/last prices (quotes only, no OHLC)"""
        
        table = Table(show_header=False, box=None, padding=(0, 1), width=46)
        table.add_column("Label", style="cyan", width=15)
        table.add_column("Value", style="white", width=29)
        
        if not market_data:
            table.add_row("", "No data")
            if with_panel:
                return Panel(
                    table,
                    title="Quote",
                    title_align="center",
                    border_style="yellow",  # Yellow border
                    width=50  # Fixed width at 50 columns
                )
            return table
        
        # Symbol with price change
        symbol = market_data.get("symbol", "-")
        last_price = market_data.get("last_price", 0)
        change = market_data.get("change", 0)
        change_pct = market_data.get("change_percent", 0)
        
        symbol_text = Text(f"{symbol}", style="bold white")
        table.add_row("Symbol:", symbol_text)
        
        # Last price with change indicator
        last_text = Text()
        last_text.append(f"${last_price:.2f}", style="white")
        table.add_row("Last:", last_text)
        
        # Change
        change_text = Text()
        if change > 0:
            change_text.append(f"▲ ${abs(change):.2f}", style="green")
        elif change < 0:
            change_text.append(f"▼ ${abs(change):.2f}", style="red")
        else:
            change_text.append(f"─ ${abs(change):.2f}", style="yellow")
        
        if change_pct != 0:
            change_text.append(f" ({change_pct:+.2f}%)", style="dim white")
        
        table.add_row("Change:", change_text)
        
        # Bid
        bid_price = market_data.get("bid_price", 0)
        bid_size = market_data.get("bid_size", 0)
        if bid_price > 0:
            bid_text = f"${bid_price:.2f}"
            if bid_size > 0:
                bid_text += f" x{bid_size}"
        else:
            bid_text = "-"
        table.add_row("Bid:", bid_text)
        
        # Ask
        ask_price = market_data.get("ask_price", 0)
        ask_size = market_data.get("ask_size", 0)
        if ask_price > 0:
            ask_text = f"${ask_price:.2f}"
            if ask_size > 0:
                ask_text += f" x{ask_size}"
        else:
            ask_text = "-"
        table.add_row("Ask:", ask_text)
        
        # Volume
        volume = market_data.get("volume", 0)
        if volume > 0:
            volume_text = f"{volume:,}"
        else:
            volume_text = "-"
        table.add_row("Volume:", volume_text)
        
        if with_panel:
            return Panel(
                table,
                title="Quote",
                title_align="center",
                border_style="yellow",  # Yellow border
                width=50  # Fixed width at 50 columns
            )
        return table  # Return table without Panel wrapper