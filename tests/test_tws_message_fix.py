#!/usr/bin/env python
"""
Test suite to verify TWS message panel functionality
Tests system message display, formatting, and latest 4 message limit
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from rich.console import Console

from src.ui.terminal_ui import TerminalUI
from src.ui.panels.header_panel import HeaderPanel


class TestTWSMessagePanel:
    """Test TWS message panel displays system messages correctly"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 12345
        self.terminal_ui = TerminalUI(client=self.mock_client, port=7497)
        self.header_panel = HeaderPanel()
    
    def test_add_system_message_stores_correctly(self):
        """Test that add_system_message stores messages with correct format"""
        # Add a system message
        test_message = "Connection established to TWS"
        self.terminal_ui.add_system_message(test_message, "info")
        
        # Verify message was stored
        assert len(self.terminal_ui.messages) == 1
        message = self.terminal_ui.messages[0]
        
        # Check message structure
        assert "time" in message
        assert "message" in message
        assert "type" in message
        assert message["message"] == test_message
        assert message["type"] == "info"
        
        # Check time format (HH:MM:SS)
        time_parts = message["time"].split(":")
        assert len(time_parts) == 3
        assert all(len(part) == 2 and part.isdigit() for part in time_parts)
    
    def test_multiple_system_messages(self):
        """Test adding multiple system messages"""
        messages = [
            "TWS connection established",
            "Market data subscription active", 
            "Order management ready",
            "Risk controls initialized",
            "Paper trading mode active"
        ]
        
        for msg in messages:
            self.terminal_ui.add_system_message(msg)
        
        # Verify all messages stored
        assert len(self.terminal_ui.messages) == 5
        
        # Verify messages stored in order
        for i, expected_msg in enumerate(messages):
            assert self.terminal_ui.messages[i]["message"] == expected_msg
    
    def test_message_limit_fifty(self):
        """Test that messages are limited to 50 entries"""
        # Add 55 messages to test limit
        for i in range(55):
            self.terminal_ui.add_system_message(f"Test message {i:02d}")
        
        # Should only keep the latest 50
        assert len(self.terminal_ui.messages) == 50
        
        # Should have messages 5-54 (the latest 50)
        assert self.terminal_ui.messages[0]["message"] == "Test message 05"
        assert self.terminal_ui.messages[-1]["message"] == "Test message 54"
    
    def test_header_panel_displays_latest_four(self):
        """Test that header panel displays only the latest 4 messages"""
        # Add 6 messages
        messages = [
            "Message 1",
            "Message 2", 
            "Message 3",
            "Message 4",
            "Message 5",
            "Message 6"
        ]
        
        for msg in messages:
            self.terminal_ui.add_system_message(msg)
        
        # Render header panel with messages
        rendered_panel = self.header_panel.render(
            connected=True,
            order_id=12345,
            port=7497,
            messages=self.terminal_ui.messages
        )
        
        # Convert to string to check content
        console = Console(width=100, file=None)
        with console.capture() as capture:
            console.print(rendered_panel)
        output = capture.get()
        
        # Should contain latest 4 messages (3, 4, 5, 6)
        assert "Message 3" in output
        assert "Message 4" in output
        assert "Message 5" in output
        assert "Message 6" in output
        
        # Should NOT contain first 2 messages
        assert "Message 1" not in output
        assert "Message 2" not in output
    
    def test_header_panel_message_format(self):
        """Test that messages display with correct time and message in table format"""
        # Add a test message with known timestamp
        with patch('src.ui.terminal_ui.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "14:30:25"
            mock_datetime.now.return_value = mock_now
            
            self.terminal_ui.add_system_message("Test formatting message")
        
        # Render header panel
        rendered_panel = self.header_panel.render(
            connected=True,
            order_id=12345,
            port=7497,
            messages=self.terminal_ui.messages
        )
        
        # Convert to string to check format
        console = Console(width=100, file=None)
        with console.capture() as capture:
            console.print(rendered_panel)
        output = capture.get()
        
        # Should contain time and message in table format (may be on different lines)
        assert "14:30:25" in output
        assert "Test formatting message" in output
    
    def test_header_panel_with_no_messages(self):
        """Test header panel displays correctly with no messages"""
        rendered_panel = self.header_panel.render(
            connected=True,
            order_id=12345,
            port=7497,
            messages=[]
        )
        
        console = Console(width=100, file=None)
        with console.capture() as capture:
            console.print(rendered_panel)
        output = capture.get()
        
        # Should show "No TWS messages" when no messages (may be split across lines)
        assert "No TWS" in output or "No TWS messages" in output
        assert "TWS Messages" in output  # Panel title should still be there
    
    def test_header_panel_message_truncation(self):
        """Test that long messages are truncated correctly"""
        long_message = "This is a very long message that should be truncated because it exceeds the fifty character limit for display"
        
        self.terminal_ui.add_system_message(long_message)
        
        rendered_panel = self.header_panel.render(
            connected=True,
            order_id=12345,
            port=7497,
            messages=self.terminal_ui.messages
        )
        
        console = Console(width=100, file=None)
        with console.capture() as capture:
            console.print(rendered_panel)
        output = capture.get()
        
        # Should contain truncated message with "..." (at least first part)
        assert "This is a very long message" in output
        assert ("..." in output or "trun." in output)  # Should have truncation indicator (may be abbreviated)
        assert long_message not in output  # Full message should not appear
    
    def test_terminal_ui_passes_messages_to_header(self):
        """Test that terminal_ui.render() passes messages correctly to header panel"""
        # Add test messages
        test_messages = [
            "Connection established",
            "Market data active",
            "Ready for trading"
        ]
        
        for msg in test_messages:
            self.terminal_ui.add_system_message(msg)
        
        # Mock the header panel render method to capture arguments
        with patch.object(self.terminal_ui.header_panel, 'render') as mock_render:
            mock_render.return_value = Mock()
            
            # Render the terminal UI
            self.terminal_ui.render()
            
            # Verify header panel was called with messages
            mock_render.assert_called_once()
            call_kwargs = mock_render.call_args[1]
            
            assert 'messages' in call_kwargs
            passed_messages = call_kwargs['messages']
            assert len(passed_messages) == 3
            assert passed_messages[0]['message'] == "Connection established"
            assert passed_messages[1]['message'] == "Market data active" 
            assert passed_messages[2]['message'] == "Ready for trading"
    
    def test_message_types_preserved(self):
        """Test that different message types are stored correctly"""
        test_cases = [
            ("Info message", "info"),
            ("Warning message", "warning"),
            ("Error message", "error"),
            ("Success message", "success")
        ]
        
        for message, msg_type in test_cases:
            self.terminal_ui.add_system_message(message, msg_type)
        
        # Verify all types preserved
        assert len(self.terminal_ui.messages) == 4
        for i, (expected_msg, expected_type) in enumerate(test_cases):
            assert self.terminal_ui.messages[i]["message"] == expected_msg
            assert self.terminal_ui.messages[i]["type"] == expected_type
    
    def test_concurrent_message_access(self):
        """Test that message access is thread-safe with data lock"""
        import threading
        import time
        
        def add_messages():
            for i in range(10):
                self.terminal_ui.add_system_message(f"Thread message {i}")
                time.sleep(0.01)
        
        # Start multiple threads adding messages
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=add_messages)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have 30 messages total
        assert len(self.terminal_ui.messages) == 30
        
        # All messages should have proper structure
        for msg in self.terminal_ui.messages:
            assert "time" in msg
            assert "message" in msg
            assert "type" in msg


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])