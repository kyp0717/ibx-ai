#!/usr/bin/env python
"""
Demo script to test the new terminal UI with simulated data
"""

import time
import random
import threading
from datetime import datetime
from ui.terminal_ui import TerminalUI


def simulate_market_data(ui: TerminalUI):
    """Simulate market data updates"""
    base_price = 150.0
    
    while ui.is_running:
        price_change = random.uniform(-2, 2)
        new_price = base_price + price_change
        
        market_data = {
            "symbol": "AAPL",
            "last_price": new_price,
            "bid_price": new_price - 0.01,
            "bid_size": random.randint(100, 1000),
            "ask_price": new_price + 0.01,
            "ask_size": random.randint(100, 1000),
            "volume": random.randint(40000000, 50000000),
            "high": base_price + 2.5,
            "low": base_price - 2.5,
            "open": base_price - 1.0,
            "close": base_price - 1.0,
            "change": price_change,
            "change_pct": (price_change / base_price) * 100
        }
        
        ui.update_market_data("AAPL", market_data)
        
        # Simulate indicators
        indicators = {
            "current_price": new_price,
            "ema9": base_price + random.uniform(-1, 1),
            "vwap": base_price + random.uniform(-0.5, 0.5),
            "macd": random.uniform(-0.5, 0.5),
            "macd_signal": random.uniform(-0.3, 0.3),
            "volume_trend": random.choice(["increasing", "decreasing", "stable"]),
            "rsi": random.uniform(30, 70)
        }
        
        ui.update_indicators(indicators)
        
        time.sleep(2)


def simulate_trading_flow(ui: TerminalUI):
    """Simulate a trading flow"""
    time.sleep(3)
    
    # Add system messages
    ui.add_system_message("Connected to TWS successfully", "success")
    time.sleep(1)
    ui.add_system_message("Market data subscription active for AAPL", "info")
    time.sleep(2)
    
    # Simulate open trade prompt
    ui.update_prompt("Open Trade at $150.26 (press enter)?")
    time.sleep(5)
    
    # Simulate order placement
    ui.add_system_message("Order #123 placed - BUY 100 AAPL @ $150.25", "info")
    
    order_data = {
        "order_id": 123,
        "status": "PENDING",
        "filled_qty": 0,
        "total_qty": 100,
        "avg_price": 0
    }
    ui.update_order_status(**order_data)
    
    time.sleep(2)
    
    # Simulate partial fill
    order_data["status"] = "PARTIAL"
    order_data["filled_qty"] = 50
    order_data["avg_price"] = 150.25
    ui.update_order_status(**order_data)
    ui.add_system_message("Order #123 partially filled - 50/100 @ $150.25", "warning")
    
    time.sleep(2)
    
    # Simulate complete fill
    order_data["status"] = "FILLED"
    order_data["filled_qty"] = 100
    ui.update_order_status(**order_data)
    ui.add_system_message("Order #123 completely filled - 100 @ $150.25", "success")
    
    # Update position
    position_data = {
        "quantity": 100,
        "avg_cost": 150.25,
        "current_price": 150.50,
        "realized_pnl": 0,
        "commission": 1.00
    }
    ui.update_position_data(position_data)
    
    time.sleep(3)
    
    # Simulate close position prompt
    ui.update_prompt("Close position at $150.50 (press enter)?")
    time.sleep(5)
    
    # Simulate closing position
    ui.add_system_message("Sell order #124 placed - SELL 100 AAPL @ $150.50", "info")
    
    sell_order = {
        "order_id": 124,
        "status": "FILLED",
        "filled_qty": 100,
        "total_qty": 100,
        "avg_price": 150.50
    }
    ui.update_order_status(**sell_order)
    ui.add_system_message("Position closed - Realized P&L: $25.00", "success")
    
    # Clear position
    position_data["quantity"] = 0
    position_data["realized_pnl"] = 25.00
    ui.update_position_data(position_data)
    
    time.sleep(3)
    
    # Exit prompt
    ui.update_prompt("Exit the trade (press enter)?")


def main():
    print("Starting Terminal UI Demo...")
    print("Press Ctrl+C to exit")
    time.sleep(2)
    
    # Create UI instance
    ui = TerminalUI()
    
    # Start data simulation threads
    market_thread = threading.Thread(target=simulate_market_data, args=(ui,))
    market_thread.daemon = True
    market_thread.start()
    
    trading_thread = threading.Thread(target=simulate_trading_flow, args=(ui,))
    trading_thread.daemon = True
    trading_thread.start()
    
    try:
        # Run the UI (blocking)
        ui.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        ui.stop()


if __name__ == "__main__":
    main()