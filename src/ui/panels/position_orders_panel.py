"""
Position and orders panel displaying current position, order status, and P&L
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from typing import Dict, Any, Optional


class PositionOrdersPanel:
    def __init__(self):
        pass
    
    def render(self, position_data: Dict[str, Any], order_data: Dict[str, Any]) -> Panel:
        """Render the position and orders panel"""
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Label", style="dim white", width=12)
        table.add_column("Value", style="white")
        
        position_qty = position_data.get("quantity", 0) if position_data else 0
        avg_cost = position_data.get("avg_cost", 0) if position_data else 0
        
        if position_qty > 0:
            table.add_row("Position:", Text(f"{position_qty} shares", style="bold cyan"))
            table.add_row("Avg Cost:", f"${avg_cost:.2f}")
        else:
            table.add_row("Position:", Text("No position", style="dim white"))
            table.add_row("Avg Cost:", "-")
        
        table.add_row("", "")
        
        if order_data:
            order_id = order_data.get("order_id", 0)
            status = order_data.get("status", "PENDING")
            filled_qty = order_data.get("filled_qty", 0)
            total_qty = order_data.get("total_qty", 0)
            avg_price = order_data.get("avg_price", 0)
            
            status_style = "yellow"
            if status == "FILLED":
                status_style = "green"
            elif status == "CANCELLED":
                status_style = "red"
            elif status == "PARTIAL":
                status_style = "yellow"
            
            table.add_row("Order Status:", Text(status, style=f"bold {status_style}"))
            table.add_row("Order ID:", f"#{order_id}")
            
            if filled_qty > 0:
                table.add_row("Filled:", f"{filled_qty}/{total_qty} @ ${avg_price:.2f}")
            else:
                table.add_row("Filled:", "0/0 @ $0.00")
        else:
            table.add_row("Order Status:", Text("No active order", style="dim white"))
            table.add_row("Order ID:", "-")
            table.add_row("Filled:", "-")
        
        table.add_row("", "")
        
        current_price = position_data.get("current_price", 0) if position_data else 0
        
        if position_qty > 0 and current_price > 0:
            current_value = position_qty * current_price
            total_cost = position_qty * avg_cost
            pnl = current_value - total_cost
            pnl_pct = (pnl / total_cost * 100) if total_cost > 0 else 0
            
            pnl_style = "green" if pnl >= 0 else "red"
            sign = "+" if pnl >= 0 else ""
            
            pnl_text = Text()
            pnl_text.append(f"${abs(pnl):.2f} ({sign}{pnl_pct:.2f}%)", style=pnl_style)
            table.add_row("P&L:", pnl_text)
            
            realized_pnl = position_data.get("realized_pnl", 0) if position_data else 0
            table.add_row("Realized:", f"${realized_pnl:.2f}")
            table.add_row("Unrealized:", Text(f"${pnl:.2f}", style=pnl_style))
            
            commission = position_data.get("commission", 0) if position_data else 0
            table.add_row("Commission:", f"${commission:.2f}")
        else:
            table.add_row("P&L:", "$0.00")
            table.add_row("Realized:", "$0.00")
            table.add_row("Unrealized:", "$0.00")
            table.add_row("Commission:", "$0.00")
        
        return Panel(
            table,
            title="POSITION & ORDERS",
            title_align="center",
            border_style="magenta",
            style="on black"
        )