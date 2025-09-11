#!/usr/bin/env python
"""
Demo script to showcase Trading Panel with side-by-side layout
"""

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
import sys
sys.path.append('/home/kelp/work/ibx-ai-paper')
from src.ui.panels.trading_panel import TradingPanel
import time

console = Console(width=100)
trading_panel = TradingPanel()

# Demo scenarios
scenarios = [
    {
        "title": "Scenario 1: No position - Buy Signal (Side-by-Side Layout)",
        "symbol": "AAPL",
        "price": 185.50,
        "position": {"quantity": 0},
        "indicators": {"ema9": 184.0, "vwap": 183.5, "macd": 1.2, "macd_signal": 0.8},
        "order": {"order_id": 101, "status": "Inactive", "filled_qty": 0, "total_qty": 0}
    },
    {
        "title": "Scenario 2: Partial position - 50 shares (Side-by-Side Layout)",
        "symbol": "TSLA",
        "price": 250.75,
        "position": {"quantity": 50, "avg_cost": 249.50},
        "indicators": {"ema9": 251.0, "vwap": 250.0, "macd": 0.5, "macd_signal": 0.6},
        "order": {"order_id": 102, "status": "PartiallyFilled", "filled_qty": 50, "total_qty": 100, "avg_price": 249.50}
    },
    {
        "title": "Scenario 3: Full position - 100 shares (Side-by-Side Layout)",
        "symbol": "NVDA",
        "price": 875.25,
        "position": {"quantity": 100, "avg_cost": 870.00},
        "indicators": {"ema9": 876.0, "vwap": 875.5, "macd": -0.3, "macd_signal": -0.2},
        "order": {"order_id": 103, "status": "Filled", "filled_qty": 100, "total_qty": 100, "avg_price": 870.00}
    }
]

# Display each scenario
for scenario in scenarios:
    console.clear()
    console.print(f"\n[bold cyan]{scenario['title']}[/bold cyan]\n")
    
    panel = trading_panel.render(
        prompt_text="",
        symbol=scenario["symbol"],
        price=scenario["price"],
        indicators=scenario["indicators"],
        position_data=scenario["position"],
        order_data=scenario["order"]
    )
    
    console.print(panel)
    console.print("\n[dim]Note: Left side shows prompts | Right side shows position/order status[/dim]")
    console.print("[dim]Press Enter to continue to next scenario...[/dim]")
    input()

console.print("\n[bold green]✓ Side-by-side layout demo completed![/bold green]")
console.print("\nFeature Updates:")
console.print("• Panel renamed from 'ACTION' to '<Symbol> Trade'")
console.print("• Left side: Time, signal/status, and action prompts")
console.print("• Right side: Position and order information")
console.print("• Content displayed side-by-side within the Trading Panel")