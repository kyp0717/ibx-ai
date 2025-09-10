"""
PnL panel for displaying profit and loss information
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Dict, Any


class PnLPanel:
    def __init__(self):
        pass
    
    def render(self, position_data: Dict[str, Any] = None, 
               market_data: Dict[str, Any] = None) -> Panel:
        """Render the PnL panel with live updated values"""
        
        table = Table(show_header=False, box=None, padding=(0, 1), width=46)
        table.add_column("Label", style="cyan", width=20)
        table.add_column("Value", style="white", width=24)
        
        # Extract position data - show values even when zero
        quantity = position_data.get("quantity", 0) if position_data else 0
        avg_cost = position_data.get("avg_cost", 0) if position_data else 0
        
        # Get current price from market data
        current_price = market_data.get("last_price", 0) if market_data else 0
        
        # Always show P&L values, even when zero
        # No blank line at top per updated requirements
        
        # Position Size (quantity of stock, not price) - no 'shares' word
        if quantity != 0:
            table.add_row("Size:", f"{quantity}")
        else:
            table.add_row("Size:", "0")
        
        # Cost Basis (amount it cost to enter position)
        cost_basis = quantity * avg_cost
        table.add_row("Cost Basis:", f"${cost_basis:,.2f}")
        
        # Current Value
        current_value = quantity * current_price
        table.add_row("Current Value:", f"${current_value:,.2f}")
        
        # Unrealized P&L in dollars (updates as stock price changes)
        unrealized_pnl = current_value - cost_basis
        pnl_text = Text()
        if unrealized_pnl > 0:
            pnl_text.append(f"${unrealized_pnl:+,.2f}", style="green")
        elif unrealized_pnl < 0:
            pnl_text.append(f"${unrealized_pnl:+,.2f}", style="red")
        else:
            pnl_text.append(f"${unrealized_pnl:+,.2f}", style="yellow")
        table.add_row("Unrealized:", pnl_text)
        
        # Removed 'Unreal Gain' metric per updated requirements (was duplicate of Unrealized)
        
        # Commission (derived from TWS, not calculated manually)
        commission = position_data.get("commission", 0) if position_data else 0
        comm_text = Text(f"${commission:.2f}", style="red" if commission > 0 else "white")
        table.add_row("Commission:", comm_text)
        
        return Panel(
            table,
            title="P&L",
            title_align="center",
            border_style="yellow",  # Yellow border
            style="on black",
            width=50  # Fixed width at 50 columns
        )