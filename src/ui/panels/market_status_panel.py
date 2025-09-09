"""
Market Status panel containing Quote and Indicator panels side by side
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Dict, Any
from .quote_panel import QuotePanel
from .indicators_panel import IndicatorsPanel


class MarketStatusPanel:
    def __init__(self):
        self.quote_panel = QuotePanel()
        self.indicators_panel = IndicatorsPanel()
        
    def render(self, market_data: Dict[str, Any], indicators: Dict[str, Any]) -> Panel:
        """Render the Market Status panel with Quote and Indicator tables separated by vertical line"""
        
        # Get the two tables (no borders)
        quote_table = self.quote_panel.render(market_data)
        indicators_table = self.indicators_panel.render(indicators)
        
        # Create main table to hold both side by side without separator
        main_table = Table(show_header=False, box=None, padding=0, expand=True)
        main_table.add_column(width=30)  # Quote panel
        main_table.add_column(width=45)  # Indicators panel
        
        # Add a single row with both panels
        main_table.add_row(
            quote_table,
            indicators_table
        )
        
        return Panel(
            main_table,
            title="MARKET STATUS",
            title_align="center",
            border_style="bright_yellow",  # Orange border (bright_yellow in Rich)
            style="on black",
            padding=(0, 1)
        )