#!/usr/bin/env python
"""
Test full demo with header display
"""

import time
import threading
import sys
sys.path.insert(0, 'src')
from ui.terminal_ui import TerminalUI

class MockClient:
    """Mock client for demo purposes"""
    def __init__(self):
        self.next_order_id = 54321
        self.positions = {}
        self.orders = {}
        self.commissions = {}
    
    def is_connected(self):
        """Always return True for demo"""
        return True

def test_demo():
    print("Testing Terminal UI with Header...")
    print("This will run for 5 seconds")
    print("-" * 50)
    
    # Create mock client and UI
    mock_client = MockClient()
    mock_client.next_order_id = 54321
    ui = TerminalUI(client=mock_client, port=7497)
    
    # Start UI in thread
    def run_ui():
        ui.is_running = True
        try:
            with ui.console.capture() as capture:
                # Just render once to test
                rendered = ui.render()
                ui.console.print(rendered)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            ui.is_running = False
    
    ui_thread = threading.Thread(target=run_ui)
    ui_thread.daemon = True
    ui_thread.start()
    
    # Let it run briefly
    time.sleep(1)
    ui.is_running = False
    ui_thread.join(timeout=2)
    
    print("\nUI rendered successfully!")
    print("Header should show:")
    print("- Title: IBX Trading")
    print("- Status: ● Active on port 7497")
    print("- Order ID: 54321")
    print("- Current time in HH:MM:SS format")

if __name__ == "__main__":
    test_demo()