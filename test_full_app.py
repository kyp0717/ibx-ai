#!/usr/bin/env python
"""
Test full app with header verification
"""

import sys
import time
import threading
sys.path.insert(0, 'src')

from order_placement import OrderClient
from ui.terminal_ui import TerminalUI

def test_full_app(port=7500):
    print(f"Testing full app with port {port}")
    print("-" * 50)
    
    # Create and connect client
    client = OrderClient()
    if not client.connect_to_tws(host="127.0.0.1", port=port, client_id=1):
        print("Failed to connect to TWS")
        return False
    
    print(f"Connected! Order ID: {client.next_order_id}")
    
    # Create UI
    ui = TerminalUI(client=client, port=port)
    ui.is_running = True
    
    # Add some test messages
    ui.add_system_message(f"Connected to TWS on port {port}", "success")
    ui.add_system_message("Test mode - Header verification", "info")
    
    # Run for a few seconds
    print("\nRunning UI for 3 seconds...")
    from rich.live import Live
    with Live(ui.render(), console=ui.console, refresh_per_second=2) as live:
        for i in range(3):
            live.update(ui.render())
            time.sleep(1)
    
    ui.is_running = False
    client.disconnect_from_tws()
    
    print("\n✓ Header should show:")
    print(f"  - Title: IBX Trading")
    print(f"  - Status: ● Active on port {port}")
    print(f"  - Order ID: {client.next_order_id}")
    print(f"  - Time: HH:MM:SS (updating)")
    
    return True

if __name__ == "__main__":
    test_full_app(7500)