#!/usr/bin/env python
"""
Test log panel implementation
"""

import sys
import time
import logging
import threading
sys.path.insert(0, 'src')

from ui.terminal_ui import TerminalUI
from ui.ui_log_handler import UILogHandler
from rich.live import Live

# Mock client for testing
class MockClient:
    def __init__(self):
        self.next_order_id = 100
    def is_connected(self):
        return True

def simulate_logs(ui):
    """Simulate various log messages"""
    logger = logging.getLogger("test_logger")
    
    time.sleep(1)
    logger.info("Starting market data stream")
    
    time.sleep(1)
    logger.warning("Market data delayed by 15 minutes")
    
    time.sleep(1)
    logger.error("Failed to connect to backup server")
    
    time.sleep(1)
    logger.debug("Debug: Processing tick data")
    
    time.sleep(1)
    logger.info("Order placement module initialized")

def test_log_panel():
    print("Testing Log Panel Implementation")
    print("-" * 50)
    
    # Setup logging with UI handler
    ui_handler = UILogHandler()
    ui_handler.setFormatter(logging.Formatter("%(message)s"))
    
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[ui_handler]
    )
    
    # Create UI with mock client
    mock_client = MockClient()
    ui = TerminalUI(client=mock_client, port=7500)
    
    # Connect handler to UI
    ui_handler.set_ui(ui)
    
    # Add some system messages
    ui.add_system_message("System initialized", "success")
    ui.add_system_message("Waiting for market data", "info")
    
    # Start log simulation thread
    log_thread = threading.Thread(target=simulate_logs, args=(ui,))
    log_thread.daemon = True
    log_thread.start()
    
    print("Running UI for 7 seconds...")
    print("Watch for log messages appearing in the right panel")
    print("-" * 50)
    
    # Run UI
    ui.is_running = True
    with Live(ui.render(), console=ui.console, refresh_per_second=2) as live:
        for i in range(7):
            live.update(ui.render())
            time.sleep(1)
    
    ui.is_running = False
    
    print("\n✓ Test completed!")
    print("You should have seen:")
    print("- System messages on the left panel")
    print("- Log messages on the right panel")
    print("- Different colors for INFO (white), WARNING (yellow), ERROR (red)")

if __name__ == "__main__":
    test_log_panel()