#!/usr/bin/env python
"""
Main entry point with new Rich-based terminal UI
"""

import sys
import argparse
import logging
import time
import select
import threading
from pathlib import Path
from datetime import datetime

from order_placement import OrderClient
from ui.terminal_ui import TerminalUI
from ui.ui_log_handler import UILogHandler

# Create UI log handler (will be attached to UI later)
ui_handler = UILogHandler()
ui_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

# Configure logging with both file and UI handlers
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"trading_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,  # Set to INFO to capture more messages
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        ui_handler  # This will redirect to UI panel
    ]
)

# Set specific loggers to appropriate levels
logging.getLogger("ibapi").setLevel(logging.WARNING)
logging.getLogger("ibapi.client").setLevel(logging.WARNING)
logging.getLogger("ibapi.wrapper").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class TradingApp:
    def __init__(self, port: int, symbol: str, position_size: int):
        self.port = port
        self.symbol = symbol
        self.position_size = position_size
        self.client = None
        self.ui = None
        self.running = False
        
        self.order_placed = False
        self.order_filled = False
        self.filled_order = None
        self.position_closed = False
        self.close_order = None
        self.audit_complete = False
    
    def connect(self) -> bool:
        """Connect to TWS"""
        self.client = OrderClient()
        
        if not self.client.connect_to_tws(host="127.0.0.1", port=self.port, client_id=1):
            return False
        
        return True
    
    def update_market_data_loop(self):
        """Background thread to update market data"""
        while self.running:
            try:
                quote = self.client.get_stock_quote(self.symbol, timeout=1)
                
                if quote and quote.is_valid():
                    market_data = {
                        "symbol": self.symbol,
                        "last_price": quote.last_price,
                        "bid_price": quote.bid_price,
                        "bid_size": quote.bid_size,
                        "ask_price": quote.ask_price,
                        "ask_size": quote.ask_size,
                        "volume": quote.volume,
                        "high": quote.high if hasattr(quote, 'high') else quote.last_price,
                        "low": quote.low if hasattr(quote, 'low') else quote.last_price,
                        "open": quote.open if hasattr(quote, 'open') else quote.close,
                        "close": quote.close,
                        "change": quote.last_price - quote.close if quote.close > 0 else 0,
                        "change_pct": ((quote.last_price - quote.close) / quote.close * 100) if quote.close > 0 else 0
                    }
                    
                    self.ui.update_market_data(self.symbol, market_data)
                    
                    # Update position data if we have a position
                    if self.symbol in self.client.positions:
                        position = self.client.positions[self.symbol]
                        position_data = {
                            "quantity": position["quantity"],
                            "avg_cost": position["avg_cost"],
                            "current_price": quote.last_price,
                            "realized_pnl": 0,
                            "commission": self.client.commissions.get(self.symbol, {}).get("total", 0)
                        }
                        self.ui.update_position_data(position_data)
                    
                    # Simulate indicators (would be calculated from real data)
                    indicators = {
                        "current_price": quote.last_price,
                        "ema9": quote.last_price - 0.15,  # Placeholder
                        "vwap": quote.last_price - 0.40,  # Placeholder
                        "macd": 0.45,  # Placeholder
                        "macd_signal": 0.32,  # Placeholder
                        "volume_trend": "increasing" if quote.volume > 40000000 else "stable",
                        "rsi": 65.4  # Placeholder
                    }
                    self.ui.update_indicators(indicators)
                    
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error updating market data: {e}")
                time.sleep(2)
    
    def handle_trading_flow(self):
        """Handle the trading flow with user interaction"""
        time.sleep(2)  # Wait for UI to initialize
        
        self.ui.add_system_message(f"Connected to TWS on port {self.port}", "success")
        self.ui.add_system_message(f"Market data subscription active for {self.symbol}", "info")
        
        while self.running:
            try:
                quote = self.client.get_stock_quote(self.symbol, timeout=1)
                
                if not quote or not quote.is_valid():
                    time.sleep(1)
                    continue
                
                if not self.order_placed:
                    # Open position prompt
                    self.ui.update_prompt(f"Open Trade at ${quote.ask_price:.2f} (press enter)?")
                    
                    # Wait for Enter key
                    ready = select.select([sys.stdin], [], [], 1.0)[0]
                    
                    if ready:
                        sys.stdin.readline()
                        
                        self.ui.add_system_message(
                            f"Placing BUY order for {self.position_size} shares at ${quote.ask_price:.2f}",
                            "info"
                        )
                        
                        result = self.client.place_limit_order(
                            self.symbol, "BUY", self.position_size, quote.ask_price
                        )
                        
                        if result:
                            self.order_placed = True
                            self.ui.add_system_message(
                                f"Order #{result.order_id} placed successfully",
                                "success"
                            )
                            
                            # Monitor order
                            result = self.monitor_order(result, "Open")
                            
                            if result.is_filled():
                                self.order_filled = True
                                self.filled_order = result
                                self.ui.add_system_message(
                                    f"Order filled: {result.quantity} shares @ ${result.avg_fill_price:.2f}",
                                    "success"
                                )
                            elif result.status == "CANCELLED":
                                # Reset flags to allow retry
                                self.order_placed = False
                                self.ui.add_system_message(
                                    "Order was cancelled. You can try placing a new order.",
                                    "warning"
                                )
                
                elif self.order_filled and not self.position_closed:
                    # Close position prompt
                    self.ui.update_prompt(f"Close position at ${quote.bid_price:.2f} (press enter)?")
                    
                    ready = select.select([sys.stdin], [], [], 1.0)[0]
                    
                    if ready:
                        sys.stdin.readline()
                        
                        if self.symbol in self.client.positions:
                            position = self.client.positions[self.symbol]
                            
                            self.ui.add_system_message(
                                f"Placing SELL order for {position['quantity']} shares at ${quote.bid_price:.2f}",
                                "info"
                            )
                            
                            result = self.client.place_limit_order(
                                self.symbol, "SELL", position["quantity"], quote.bid_price
                            )
                            
                            if result:
                                self.ui.add_system_message(
                                    f"Sell order #{result.order_id} placed successfully",
                                    "success"
                                )
                                
                                result = self.monitor_order(result, "Close")
                                
                                if result.is_filled():
                                    self.position_closed = True
                                    self.close_order = result
                                    
                                    # Calculate final P&L
                                    pnl = (result.avg_fill_price - position["avg_cost"]) * position["quantity"]
                                    self.client.pnl[self.symbol] = pnl
                                    
                                    self.ui.add_system_message(
                                        f"Position closed - Realized P&L: ${pnl:.2f}",
                                        "success" if pnl >= 0 else "warning"
                                    )
                                    
                                    # Perform audit
                                    self.perform_audit()
                                    self.audit_complete = True
                                elif result.status == "CANCELLED":
                                    # Allow retry for sell order
                                    self.ui.add_system_message(
                                        "Sell order was cancelled. You can try closing the position again.",
                                        "warning"
                                    )
                
                elif self.position_closed and self.audit_complete:
                    # Exit prompt
                    self.ui.update_prompt("Exit the trade (press enter)?")
                    
                    ready = select.select([sys.stdin], [], [], 1.0)[0]
                    
                    if ready:
                        sys.stdin.readline()
                        self.ui.add_system_message("Exiting trade...", "info")
                        time.sleep(2)
                        self.running = False
                        break
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                self.ui.add_system_message("Trading interrupted by user", "warning")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in trading flow: {e}")
                self.ui.add_system_message(f"Error: {str(e)}", "error")
                time.sleep(2)
    
    def monitor_order(self, order_result, order_type: str):
        """Monitor order status"""
        while not order_result.is_filled() and self.running:
            if order_result.order_id in self.client.orders:
                order_result = self.client.orders[order_result.order_id]
            
            order_data = {
                "order_id": order_result.order_id,
                "status": order_result.status,
                "filled_qty": order_result.filled_qty,
                "total_qty": order_result.quantity,
                "avg_price": order_result.avg_fill_price
            }
            
            self.ui.update_order_status(**order_data)
            
            if order_result.status == "CANCELLED":
                self.ui.add_system_message(f"{order_type} order cancelled", "error")
                # Update the order_result status before breaking
                order_result.status = "CANCELLED"
                break
            elif order_result.is_filled():
                break
            
            time.sleep(0.5)
        
        # Return the updated order result
        return order_result
    
    def perform_audit(self):
        """Perform position audit"""
        actual_positions = self.client.request_positions()
        
        position_qty = 0
        if self.symbol in actual_positions:
            position_qty = actual_positions[self.symbol]["position"]
        
        final_pnl = self.client.pnl.get(self.symbol, 0.0)
        total_commission = self.client.commissions.get(self.symbol, {}).get("total", 0.0)
        pnl_after_commission = final_pnl - total_commission
        
        self.ui.add_system_message(f"Audit: Final Position {position_qty}", "info")
        self.ui.add_system_message(f"Audit: Commission Cost ${total_commission:.2f}", "info")
        self.ui.add_system_message(
            f"Audit: Final P&L after commission ${pnl_after_commission:.2f}",
            "success" if pnl_after_commission >= 0 else "warning"
        )
        
        if position_qty == 0:
            self.ui.add_system_message("Position successfully closed", "success")
        else:
            self.ui.add_system_message(f"Warning: Position still open with {position_qty} shares", "error")
    
    def run(self):
        """Run the trading application"""
        print(f"\nStarting IBX Trading Terminal for {self.symbol}")
        print(f"Position size: {self.position_size} shares")
        print(f"TWS Port: {self.port}")
        print("Connecting to TWS...")
        
        if not self.connect():
            print("Failed to connect to TWS")
            print("Please ensure TWS is running and API connections are enabled")
            return False
        
        print("Connected successfully!")
        print("Starting terminal UI...")
        time.sleep(1)
        
        # Initialize UI
        self.ui = TerminalUI(self.client, port=self.port)
        self.running = True
        
        # Connect UI to log handler
        ui_handler.set_ui(self.ui)
        
        # Start background threads
        market_thread = threading.Thread(target=self.update_market_data_loop)
        market_thread.daemon = True
        market_thread.start()
        
        trading_thread = threading.Thread(target=self.handle_trading_flow)
        trading_thread.daemon = True
        trading_thread.start()
        
        try:
            # Run the UI (blocking)
            self.ui.run()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.running = False
            self.ui.stop()
            
            if self.client and self.client.is_connected():
                self.client.disconnect_from_tws()
                print("Disconnected from TWS")
            
            print("Goodbye!")
        
        return True


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="IBX Trading Terminal with Rich UI - Trade stocks via Interactive Brokers TWS"
    )
    parser.add_argument("--port", type=int, required=True, help="TWS API port number (must be first argument)")
    parser.add_argument("symbol", type=str, help="Stock symbol to trade (e.g., AAPL)")
    parser.add_argument("position_size", type=int, help="Number of shares to trade")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode without TWS connection")
    return parser.parse_args()


def main():
    """Main entry point"""
    try:
        args = parse_arguments()
    except SystemExit:
        print("\nError: Port, symbol and position size are required")
        print("Usage: python main_ui.py --port <port> <symbol> <position_size>")
        print("Example: python main_ui.py --port 7497 AAPL 100")
        print("Demo mode: python main_ui.py --port 7497 AAPL 100 --demo")
        sys.exit(1)
    
    port = args.port
    symbol = args.symbol.upper()
    position_size = args.position_size
    
    if position_size <= 0:
        print("\nError: Position size must be greater than 0")
        sys.exit(1)
    
    if args.demo:
        print("\nRunning in DEMO mode - no real trading")
        import ui_demo
        ui_demo.main(port=port)
    else:
        app = TradingApp(port, symbol, position_size)
        success = app.run()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()