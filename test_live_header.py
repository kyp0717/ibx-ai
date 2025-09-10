#!/usr/bin/env python
"""
Test header panel with live TWS connection
"""

import sys
import time
sys.path.insert(0, 'src')

from order_placement import OrderClient
from ui.terminal_ui import TerminalUI
from rich.live import Live

def test_live_header(port=7497):
    print(f"Testing header with live TWS connection on port {port}")
    print("Make sure TWS is running and API connections are enabled")
    print("-" * 50)
    
    # Create real client
    client = OrderClient()
    
    # Try to connect
    print(f"Connecting to TWS on port {port}...")
    if not client.connect_to_tws(host="127.0.0.1", port=port, client_id=1):
        print("Failed to connect to TWS")
        print("Please ensure TWS is running and API connections are enabled")
        return False
    
    print("Connected successfully!")
    print(f"Connection status: {client.is_connected()}")
    print(f"Next order ID: {client.next_order_id}")
    
    # Create UI with real client
    ui = TerminalUI(client=client, port=port)
    
    print("\nDisplaying header for 5 seconds...")
    print("-" * 50)
    
    # Run UI for 5 seconds
    ui.is_running = True
    with Live(ui.render(), console=ui.console, refresh_per_second=2) as live:
        for i in range(5):
            live.update(ui.render())
            time.sleep(1)
    
    ui.is_running = False
    client.disconnect_from_tws()
    
    print("\nTest completed!")
    print("Header should have shown:")
    print(f"- Connection: ● Active on port {port}")
    print(f"- Order ID: {client.next_order_id}")
    print("- Current time updating every second")
    
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test header with live TWS connection")
    parser.add_argument("--port", type=int, default=7497, help="TWS API port")
    args = parser.parse_args()
    
    test_live_header(args.port)