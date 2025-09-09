"""
Phase 3 Terminal UI Integration Test
Tests the main panel integration and layout functionality
"""

import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.terminal_ui import TerminalUI
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console


class TestPhase3UIIntegration(unittest.TestCase):
    """Test Phase 3 terminal UI integration and panel rendering"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 1001
        self.port = 7497
        
        # Initialize terminal UI
        self.ui = TerminalUI(client=self.mock_client, port=self.port)
        
        # Sample test data
        self.sample_market_data = {
            "symbol": "AAPL",
            "last_price": 150.25,
            "bid_price": 150.20,
            "bid_size": 100,
            "ask_price": 150.30,
            "ask_size": 200,
            "volume": 1000000,
            "high": 152.00,
            "low": 149.00,
            "open": 150.00,
            "close": 149.50,
            "change": 0.75,
            "change_pct": 0.50
        }
        
        self.sample_indicators = {
            "SMA": {"value": 148.50, "signal": "BUY"},
            "RSI": {"value": 65.0, "signal": "HOLD"},
            "MACD": {"value": 1.25, "signal": "BUY"}
        }
        
        self.sample_position = {
            "symbol": "AAPL",
            "position": 100,
            "avg_cost": 149.00,
            "market_value": 15025.00,
            "unrealized_pnl": 125.00,
            "realized_pnl": 0.00
        }
        
        self.sample_order = {
            "order_id": 1001,
            "status": "Submitted",
            "filled_qty": 0,
            "total_qty": 100,
            "avg_price": 0.0
        }

    def test_ui_initialization(self):
        """Test that TerminalUI initializes correctly with proper dimensions"""
        # Verify console width is set to 130 as per Phase 3 requirements
        self.assertEqual(self.ui.console.size.width, 130)
        
        # Verify client and port are set
        self.assertEqual(self.ui.client, self.mock_client)
        self.assertEqual(self.ui.port, self.port)
        
        # Verify initial state
        self.assertFalse(self.ui.is_running)
        self.assertEqual(len(self.ui.messages), 0)
        self.assertEqual(len(self.ui.log_messages), 0)

    def test_layout_structure(self):
        """Test that the layout has the correct structure and panel sizes"""
        layout = self.ui.render()
        
        # Verify main layout structure exists
        self.assertIsInstance(layout, Layout)
        
        # Check that all required panels are accessible
        try:
            header_panel = layout["header"]
            market_status_panel = layout["market_status"]
            bottom_panels = layout["bottom_panels"]
            
            # Verify these are Layout objects
            self.assertIsInstance(header_panel, Layout)
            self.assertIsInstance(market_status_panel, Layout)
            self.assertIsInstance(bottom_panels, Layout)
            
        except KeyError as e:
            self.fail(f"Required panel not found in layout: {e}")
        
        # Check bottom panels split
        try:
            pnl_panel = bottom_panels["pnl"]
            action_panel = bottom_panels["action"]
            
            self.assertIsInstance(pnl_panel, Layout)
            self.assertIsInstance(action_panel, Layout)
            
        except KeyError as e:
            self.fail(f"Required bottom panel not found: {e}")
        
        # Verify panel sizes match Phase 3 specifications
        self.assertEqual(layout["header"].size, 7)
        self.assertEqual(layout["market_status"].size, 15)
        self.assertEqual(layout["bottom_panels"].size, 12)

    def test_panel_rendering_without_data(self):
        """Test that all panels render without errors when no data is available"""
        try:
            layout = self.ui.render()
            
            # Verify layout renders successfully
            self.assertIsInstance(layout, Layout)
            
            # Each panel should render without throwing exceptions
            header_content = layout["header"].renderable
            market_status_content = layout["market_status"].renderable
            pnl_content = layout["bottom_panels"]["pnl"].renderable
            action_content = layout["bottom_panels"]["action"].renderable
            
            # All should be Panel instances (Rich components)
            self.assertIsInstance(header_content, Panel)
            self.assertIsInstance(market_status_content, Panel)
            self.assertIsInstance(pnl_content, Panel)
            self.assertIsInstance(action_content, Panel)
            
        except Exception as e:
            self.fail(f"Panel rendering failed without data: {e}")

    def test_panel_rendering_with_data(self):
        """Test that all panels render correctly with sample data"""
        # Update UI with sample data
        self.ui.update_market_data("AAPL", self.sample_market_data)
        self.ui.update_indicators(self.sample_indicators)
        self.ui.update_position_data(self.sample_position)
        self.ui.update_order_status(
            self.sample_order["order_id"],
            self.sample_order["status"],
            self.sample_order["filled_qty"],
            self.sample_order["total_qty"],
            self.sample_order["avg_price"]
        )
        
        try:
            layout = self.ui.render()
            
            # Verify layout renders successfully with data
            self.assertIsInstance(layout, Layout)
            
            # Check that data is properly stored
            self.assertEqual(self.ui.market_data["symbol"], "AAPL")
            self.assertEqual(self.ui.market_data["last_price"], 150.25)
            self.assertEqual(self.ui.indicators_data["SMA"]["value"], 148.50)
            self.assertEqual(self.ui.position_data["position"], 100)
            self.assertEqual(self.ui.order_data["order_id"], 1001)
            
        except Exception as e:
            self.fail(f"Panel rendering failed with data: {e}")

    def test_message_handling(self):
        """Test system and log message handling"""
        # Add system messages
        self.ui.add_system_message("Connection established", "info")
        self.ui.add_system_message("Market data received", "success")
        
        # Add log messages
        self.ui.add_log_message("Starting application", "INFO")
        self.ui.add_log_message("Processing order", "DEBUG")
        
        # Verify messages are stored
        self.assertEqual(len(self.ui.messages), 2)
        self.assertEqual(len(self.ui.log_messages), 2)
        
        # Verify message structure
        self.assertIn("time", self.ui.messages[0])
        self.assertIn("message", self.ui.messages[0])
        self.assertIn("type", self.ui.messages[0])
        
        self.assertEqual(self.ui.messages[0]["message"], "Connection established")
        self.assertEqual(self.ui.log_messages[0]["message"], "Starting application")

    def test_prompt_update(self):
        """Test trading prompt update functionality"""
        test_prompt = "Buy AAPL at 150.25 (press enter)?"
        self.ui.update_prompt(test_prompt)
        
        self.assertEqual(self.ui.prompt_text, test_prompt)

    def test_data_thread_safety(self):
        """Test that data updates are thread-safe"""
        # This test verifies that the data_lock is properly used
        import threading
        import time
        
        def update_data():
            for i in range(10):
                self.ui.update_market_data("TEST", {"last_price": i})
                time.sleep(0.001)
        
        # Start multiple threads updating data
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=update_data)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify final state is consistent
        self.assertIsInstance(self.ui.market_data.get("last_price"), (int, float))

    def test_panel_components_exist(self):
        """Test that all required panel components are initialized"""
        # Verify all panel instances exist
        self.assertIsNotNone(self.ui.header_panel)
        self.assertIsNotNone(self.ui.market_status_panel)
        self.assertIsNotNone(self.ui.action_panel)
        self.assertIsNotNone(self.ui.pnl_panel)
        
        # Verify panels have render methods
        self.assertTrue(hasattr(self.ui.header_panel, 'render'))
        self.assertTrue(hasattr(self.ui.market_status_panel, 'render'))
        self.assertTrue(hasattr(self.ui.action_panel, 'render'))
        self.assertTrue(hasattr(self.ui.pnl_panel, 'render'))


if __name__ == '__main__':
    unittest.main()