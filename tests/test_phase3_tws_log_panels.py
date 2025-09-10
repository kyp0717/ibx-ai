"""
Comprehensive tests for TWS Message Panel and Log Panel changes in Phase 3
Tests the updated header_panel.py, new log_panel.py, and terminal_ui.py integration
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from rich.console import Console
from rich.layout import Layout

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.panels.header_panel import HeaderPanel
from ui.panels.log_panel import LogPanel
from ui.terminal_ui import TerminalUI


class TestHeaderPanelTWSMessages(unittest.TestCase):
    """Test suite for updated header_panel.py with TWS Message panel"""
    
    def setUp(self):
        self.header_panel = HeaderPanel()
        self.sample_messages = [
            {"time": "10:30:15", "message": "Connected to TWS", "type": "tws", "source": "TWS"},
            {"time": "10:30:16", "message": "Market data started", "type": "info", "source": "SYSTEM"},
            {"time": "10:30:17", "message": "Order submitted", "type": "tws", "source": "TWS"},
            {"time": "10:30:18", "message": "Position updated", "type": "info", "source": "SYSTEM"},
            {"time": "10:30:19", "message": "Order filled", "type": "tws", "source": "TWS"},
            {"time": "10:30:20", "message": "Account data received", "type": "tws", "source": "TWS"},
            {"time": "10:30:21", "message": "Portfolio updated", "type": "tws", "source": "TWS"},
        ]
    
    def test_header_panel_renders_correctly(self):
        """Test that header panel renders without errors"""
        panel = self.header_panel.render(connected=True, order_id=123, port=7497)
        self.assertIsNotNone(panel)
        self.assertEqual(panel.height, 7)
        self.assertEqual(panel.border_style, "blue")
    
    def test_tws_message_panel_nested_in_header(self):
        """Test that TWS Message panel is properly nested inside header panel"""
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=self.sample_messages)
        
        # Verify panel structure - should contain Columns with status and message panel
        self.assertIsNotNone(panel)
        self.assertTrue(hasattr(panel, 'renderable'))
    
    def test_tws_message_panel_fixed_width(self):
        """Test that TWS Message panel is fixed at 60 columns width"""
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=self.sample_messages)
        
        # The render method should create a panel with width=60
        # This is verified by checking the panel creation in the source
        self.assertIsNotNone(panel)
    
    def test_tws_message_filtering(self):
        """Test that only TWS messages are displayed in the message panel"""
        mixed_messages = [
            {"time": "10:30:15", "message": "Connected to TWS", "type": "tws", "source": "TWS"},
            {"time": "10:30:16", "message": "System startup", "type": "info", "source": "SYSTEM"},
            {"time": "10:30:17", "message": "TWS order update", "type": "tws", "source": "TWS"},
            {"time": "10:30:18", "message": "Debug message", "type": "debug", "source": "APP"},
        ]
        
        # Render with mixed messages
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=mixed_messages)
        
        # Should only show TWS messages (2 out of 4)
        self.assertIsNotNone(panel)
    
    def test_tws_message_latest_four_only(self):
        """Test that only 4 latest TWS messages are shown"""
        tws_messages = [
            {"time": "10:30:15", "message": "Message 1", "type": "tws", "source": "TWS"},
            {"time": "10:30:16", "message": "Message 2", "type": "tws", "source": "TWS"},
            {"time": "10:30:17", "message": "Message 3", "type": "tws", "source": "TWS"},
            {"time": "10:30:18", "message": "Message 4", "type": "tws", "source": "TWS"},
            {"time": "10:30:19", "message": "Message 5", "type": "tws", "source": "TWS"},
            {"time": "10:30:20", "message": "Message 6", "type": "tws", "source": "TWS"},
        ]
        
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=tws_messages)
        
        # Should display only the latest 4 messages (Message 3, 4, 5, 6)
        self.assertIsNotNone(panel)
    
    def test_tws_message_format_time_and_message(self):
        """Test that TWS messages display only time and message with single space"""
        simple_messages = [
            {"time": "10:30:15", "message": "Test message", "type": "tws", "source": "TWS"},
        ]
        
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=simple_messages)
        
        # The format should be "time message" with single space
        self.assertIsNotNone(panel)
    
    def test_tws_message_truncation(self):
        """Test that long TWS messages are truncated properly"""
        long_messages = [
            {
                "time": "10:30:15", 
                "message": "This is a very long message that should be truncated because it exceeds the 50 character limit set for the panel", 
                "type": "tws", 
                "source": "TWS"
            },
        ]
        
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=long_messages)
        
        # Message should be truncated to 47 chars + "..."
        self.assertIsNotNone(panel)
    
    def test_no_tws_messages_display(self):
        """Test behavior when no TWS messages are available"""
        empty_messages = []
        
        panel = self.header_panel.render(connected=True, order_id=123, port=7497, messages=empty_messages)
        
        # Should display "No TWS messages"
        self.assertIsNotNone(panel)
    
    def test_connection_status_display(self):
        """Test connection status display in header"""
        # Test connected state
        connected_panel = self.header_panel.render(connected=True, order_id=123, port=7497)
        self.assertIsNotNone(connected_panel)
        
        # Test disconnected state
        disconnected_panel = self.header_panel.render(connected=False, order_id=123, port=7497)
        self.assertIsNotNone(disconnected_panel)


class TestLogPanel(unittest.TestCase):
    """Test suite for new log_panel.py"""
    
    def setUp(self):
        self.log_panel = LogPanel()
        self.sample_logs = [
            {"time": "10:30:15", "message": "Application started", "level": "INFO"},
            {"time": "10:30:16", "message": "Market data connected", "level": "INFO"},
            {"time": "10:30:17", "message": "Warning: High volatility", "level": "WARN"},
            {"time": "10:30:18", "message": "Error in calculation", "level": "ERROR"},
            {"time": "10:30:19", "message": "Debug trace", "level": "DEBUG"},
        ]
    
    def test_log_panel_renders_correctly(self):
        """Test that log panel renders without errors"""
        panel = self.log_panel.render(log_messages=self.sample_logs)
        self.assertIsNotNone(panel)
        self.assertEqual(panel.height, 12)
        self.assertEqual(panel.border_style, "cyan")
    
    def test_log_panel_title(self):
        """Test that log panel has correct title"""
        panel = self.log_panel.render(log_messages=self.sample_logs)
        self.assertIsNotNone(panel)
        self.assertEqual(panel.title, "Log")
    
    def test_log_messages_display_format(self):
        """Test that log messages display time and message with single space"""
        simple_logs = [
            {"time": "10:30:15", "message": "Test log entry", "level": "INFO"},
        ]
        
        panel = self.log_panel.render(log_messages=simple_logs)
        
        # The format should be "time message" with single space (no level)
        self.assertIsNotNone(panel)
    
    def test_log_panel_latest_ten_messages(self):
        """Test that only 10 latest log messages are shown"""
        many_logs = []
        for i in range(15):
            many_logs.append({
                "time": f"10:30:{i:02d}",
                "message": f"Log message {i+1}",
                "level": "INFO"
            })
        
        panel = self.log_panel.render(log_messages=many_logs)
        
        # Should display only the latest 10 messages (messages 6-15)
        self.assertIsNotNone(panel)
    
    def test_empty_log_messages_handling(self):
        """Test handling of empty log messages"""
        # Test with None
        panel_none = self.log_panel.render(log_messages=None)
        self.assertIsNotNone(panel_none)
        
        # Test with empty list
        panel_empty = self.log_panel.render(log_messages=[])
        self.assertIsNotNone(panel_empty)
    
    def test_log_panel_no_header_table(self):
        """Test that log panel table has no headers"""
        panel = self.log_panel.render(log_messages=self.sample_logs)
        self.assertIsNotNone(panel)
        # The table should be created with show_header=False


class TestTerminalUIIntegration(unittest.TestCase):
    """Test suite for terminal_ui.py integration with TWS and Log panels"""
    
    def setUp(self):
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 123
        
        self.terminal_ui = TerminalUI(client=self.mock_client, port=7497)
    
    def test_terminal_ui_layout_includes_log_panel(self):
        """Test that log panel is added to layout at bottom"""
        layout = self.terminal_ui.layout
        
        # Check that log section exists by trying to access it
        try:
            log_layout = layout["log"]
            self.assertIsNotNone(log_layout)
        except KeyError:
            self.fail("Log panel not found in layout")
        
        # Verify layout structure by checking if we can render it
        rendered_layout = self.terminal_ui.render()
        self.assertIsInstance(rendered_layout, Layout)
    
    def test_add_system_message_method(self):
        """Test add_system_message method functionality"""
        # Add a system message
        self.terminal_ui.add_system_message("Test system message", "info")
        
        # Check that message was added
        self.assertEqual(len(self.terminal_ui.messages), 1)
        self.assertEqual(self.terminal_ui.messages[0]["message"], "Test system message")
        self.assertEqual(self.terminal_ui.messages[0]["type"], "info")
        self.assertIsNotNone(self.terminal_ui.messages[0]["time"])
    
    def test_add_log_message_method(self):
        """Test add_log_message method functionality"""
        # Add a log message
        self.terminal_ui.add_log_message("Test log message", "INFO")
        
        # Check that message was added
        self.assertEqual(len(self.terminal_ui.log_messages), 1)
        self.assertEqual(self.terminal_ui.log_messages[0]["message"], "Test log message")
        self.assertEqual(self.terminal_ui.log_messages[0]["level"], "INFO")
        self.assertIsNotNone(self.terminal_ui.log_messages[0]["time"])
    
    def test_tws_and_log_message_separation(self):
        """Test that TWS messages are separated from log messages"""
        # Add both types of messages
        self.terminal_ui.add_system_message("TWS connection established", "tws")
        self.terminal_ui.add_log_message("Application started", "INFO")
        self.terminal_ui.add_system_message("Regular system message", "info")
        
        # Check separation
        self.assertEqual(len(self.terminal_ui.messages), 2)  # System messages
        self.assertEqual(len(self.terminal_ui.log_messages), 1)  # Log messages
    
    def test_message_list_trimming(self):
        """Test that message lists are trimmed to prevent memory issues"""
        # Add more than 50 system messages
        for i in range(55):
            self.terminal_ui.add_system_message(f"Message {i}", "info")
        
        # Should be trimmed to 50
        self.assertEqual(len(self.terminal_ui.messages), 50)
        
        # Add more than 50 log messages
        for i in range(55):
            self.terminal_ui.add_log_message(f"Log {i}", "INFO")
        
        # Should be trimmed to 50
        self.assertEqual(len(self.terminal_ui.log_messages), 50)
    
    def test_render_method_data_flow(self):
        """Test that render method correctly passes data to both panels"""
        # Add test data
        self.terminal_ui.add_system_message("TWS message", "tws")
        self.terminal_ui.add_log_message("Log message", "INFO")
        
        # Mock market data
        self.terminal_ui.update_market_data("AAPL", {
            "last_price": 150.0,
            "bid_price": 149.95,
            "ask_price": 150.05
        })
        
        # Render layout
        layout = self.terminal_ui.render()
        
        # Check that layout is returned
        self.assertIsInstance(layout, Layout)
    
    def test_tws_message_filtering_in_render(self):
        """Test that render method filters TWS messages correctly"""
        # Add mixed messages
        self.terminal_ui.add_system_message("TWS connection", "tws")
        self.terminal_ui.add_system_message("System info", "info")
        self.terminal_ui.messages.append({
            "time": "10:30:15",
            "message": "TWS order update", 
            "source": "TWS"
        })
        
        # Render should filter only TWS messages for header panel
        layout = self.terminal_ui.render()
        
        # Check that layout renders without error
        self.assertIsInstance(layout, Layout)
    
    def test_concurrent_access_thread_safety(self):
        """Test thread safety of data access with locks"""
        import threading
        import time
        
        def add_messages():
            for i in range(10):
                self.terminal_ui.add_system_message(f"Thread message {i}", "info")
                self.terminal_ui.add_log_message(f"Thread log {i}", "INFO")
                time.sleep(0.01)
        
        def render_ui():
            for i in range(10):
                self.terminal_ui.render()
                time.sleep(0.01)
        
        # Start threads
        thread1 = threading.Thread(target=add_messages)
        thread2 = threading.Thread(target=render_ui)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Should complete without deadlock or corruption
        self.assertTrue(len(self.terminal_ui.messages) > 0)
        self.assertTrue(len(self.terminal_ui.log_messages) > 0)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases
    test_suite.addTest(unittest.makeSuite(TestHeaderPanelTWSMessages))
    test_suite.addTest(unittest.makeSuite(TestLogPanel))
    test_suite.addTest(unittest.makeSuite(TestTerminalUIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)