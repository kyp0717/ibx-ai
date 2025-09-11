#!/usr/bin/env python
"""
Demo script to showcase Trading Panel Feature 6 implementation
"""

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from src.ui.panels.action_panel import ActionPanel
import time

console = Console(width=100)
action_panel = ActionPanel()

# Demo scenarios
scenarios = [
    {
        "title": "Scenario 1: No position with Buy signal",
        "symbol": "AAPL",
        "price": 185.50,
        "position": {"quantity": 0},
        "indicators": {"ema9": 184.0, "vwap": 183.5, "macd": 1.2, "macd_signal": 0.8},
        "order": {"order_id": 101, "status": "Inactive", "filled_qty": 0, "total_qty": 0}
    },
    {
        "title": "Scenario 2: Partial position (50 shares)",
        "symbol": "TSLA",
        "price": 250.75,
        "position": {"quantity": 50, "avg_cost": 249.50},
        "indicators": {"ema9": 251.0, "vwap": 250.0, "macd": 0.5, "macd_signal": 0.6},
        "order": {"order_id": 102, "status": "PartiallyFilled", "filled_qty": 50, "total_qty": 100, "avg_price": 249.50}
    },
    {
        "title": "Scenario 3: Full position (100 shares)",
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
    
    panel = action_panel.render(
        prompt_text="",
        symbol=scenario["symbol"],
        price=scenario["price"],
        indicators=scenario["indicators"],
        position_data=scenario["position"],
        order_data=scenario["order"]
    )
    
    console.print(panel)
    console.print("\n[dim]Press Enter to continue to next scenario...[/dim]")
    input()

console.print("\n[bold green]✓ Demo completed![/bold green]")
console.print("\nFeature 6 Implementation Summary:")
console.print("• Dynamic panel title: '<Symbol> Trade'")
console.print("• Position-aware prompts (0, partial, full)")
console.print("• Signal display when no position")
console.print("• Status messages for opening/filled positions")
console.print("• Integrated position/order information")