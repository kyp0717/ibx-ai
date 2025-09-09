"""
Final Phase 3 UI Verification Test
Comprehensive test to verify Phase 3 implementation meets specifications
"""

import unittest
from unittest.mock import Mock
import sys
import os
from io import StringIO

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.terminal_ui import TerminalUI
from ui.panels.header_panel import HeaderPanel
from ui.panels.market_status_panel import MarketStatusPanel
from ui.panels.action_panel import ActionPanel
from ui.panels.pnl_panel import PnLPanel
from rich.console import Console


class TestPhase3FinalVerification(unittest.TestCase):
    """Final comprehensive test for Phase 3 implementation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 1001
        
        # Initialize UI with port 7497 (Phase 3 requirement)
        self.ui = TerminalUI(client=self.mock_client, port=7497)
        
        # Test data matching Phase 3 requirements
        self.test_market_data = {
            "symbol": "AAPL",
            "last_price": 150.50,
            "bid_price": 150.45,
            "bid_size": 100,
            "ask_price": 150.55,
            "ask_size": 200,
            "volume": 1500000,
            "change": 0.75,
            "change_pct": 0.50
        }
        
        self.test_indicators = {
            "ema9": 149.80,
            "vwap": 150.10,
            "macd": 0.45,
            "macd_signal": 0.32,
            "current_price": 150.50
        }
        
        self.test_position = {
            "symbol": "AAPL",
            "position": 100,
            "avg_cost": 149.50,
            "market_value": 15050.00,
            "unrealized_pnl": 100.00,
            "realized_pnl": 50.00
        }

    def test_phase3_console_width_requirement(self):
        """TEST: Feature 10 - Verify console width is fixed to 130 columns"""
        self.assertEqual(self.ui.console.size.width, 130,
                        "Console width must be 130 columns per Phase 3 specification")

    def test_phase3_header_panel_structure(self):
        """TEST: Feature 2 - Verify header panel displays required information"""
        header_panel = HeaderPanel()
        
        # Test header with connection info
        test_messages = [
            {"time": "14:30:15", "message": "Connected to TWS", "type": "info"}
        ]
        
        result = header_panel.render(
            connected=True,
            order_id=1001,
            port=7497,
            messages=test_messages
        )
        
        # Render to string to check content
        console = Console(file=StringIO(), width=130)
        console.print(result)
        output = console.file.getvalue()
        
        # Check for required header elements
        self.assertIn("IBX Trading", output, "Header must display application title")
        self.assertIn("7497", output, "Header must display port number")
        self.assertIn("1001", output, "Header must display order ID counter")
        self.assertIn(":", output, "Header must display system time format")

    def test_phase3_market_status_panel_integration(self):
        """TEST: Feature 7 - Verify Market Status panel contains Quote and Indicator panels"""
        market_status_panel = MarketStatusPanel()
        
        result = market_status_panel.render(self.test_market_data, self.test_indicators)
        
        # Render to string to verify content
        console = Console(file=StringIO(), width=130)
        console.print(result)
        output = console.file.getvalue()
        
        # Verify panel title and border color
        self.assertEqual(result.title, "MARKET STATUS")
        self.assertEqual(result.border_style, "bright_yellow", "Market Status panel must have orange/yellow border")
        
        # Verify quote data is present
        self.assertIn("AAPL", output, "Market Status must display symbol")
        self.assertIn("150.50", output, "Market Status must display last price")
        self.assertIn("150.45", output, "Market Status must display bid price")
        self.assertIn("150.55", output, "Market Status must display ask price")
        
        # Verify indicators are present (3 column format without signal)
        self.assertIn("EMA(9)", output, "Market Status must display EMA indicator")
        self.assertIn("VWAP", output, "Market Status must display VWAP indicator")
        self.assertIn("MACD", output, "Market Status must display MACD indicator")
        
        # Verify vertical separator between panels
        self.assertIn("│", output, "Market Status must have vertical line separator")

    def test_phase3_action_panel_structure(self):
        """TEST: Feature 6 - Verify Action panel redesign and yellow border"""
        action_panel = ActionPanel()
        
        # Test with buy signal scenario
        test_prompt = "Buy AAPL at $150.50 (press enter) ?"
        
        result = action_panel.render(
            test_prompt,
            "AAPL",
            150.50,
            self.test_indicators,
            self.test_position,
            {"order_id": 1001, "status": "None", "filled_qty": 0, "total_qty": 0, "avg_price": 0}
        )
        
        # Verify yellow border
        self.assertEqual(result.border_style, "yellow", 
                        "Action panel must have yellow border per Phase 3")
        
        # Verify panel title
        self.assertEqual(result.title, "ACTION", "Action panel must be named ACTION")
        
        # Render to string to check content structure
        console = Console(file=StringIO(), width=130)
        console.print(result)
        output = console.file.getvalue()
        
        # Check for time format [ HH:MM:SS ]
        import re
        time_pattern = r'\[\s*\d{2}:\d{2}:\d{2}\s*\]'
        self.assertTrue(re.search(time_pattern, output), 
                       "Action panel must display time in [ HH:MM:SS ] format")
        
        # Check for symbol display
        self.assertIn("AAPL", output, "Action panel must display stock symbol")
        
        # Check for signal display (formatted as ** Signal: X **)
        signal_pattern = r'\*\*\s*Signal:\s*(Buy|Sell|Hold)\s*\*\*'
        self.assertTrue(re.search(signal_pattern, output), 
                       "Action panel must display signal in ** Signal: X ** format")

    def test_phase3_pnl_panel_structure(self):
        """TEST: Feature 8 - Verify PnL panel with yellow border"""
        pnl_panel = PnLPanel()
        
        result = pnl_panel.render(self.test_position, self.test_market_data)
        
        # Verify yellow border
        self.assertEqual(result.border_style, "yellow",
                        "PnL panel must have yellow border per Phase 3")
        
        # Render to string to check content
        console = Console(file=StringIO(), width=130)
        console.print(result)
        output = console.file.getvalue()
        
        # Verify PnL values are displayed even at $0
        self.assertIn("Unrealized", output, "PnL panel must show unrealized PnL")
        self.assertIn("Realized", output, "PnL panel must show realized PnL")

    def test_phase3_layout_structure_verification(self):
        """TEST: Comprehensive layout structure verification"""
        # Update UI with test data
        self.ui.update_market_data("AAPL", self.test_market_data)
        self.ui.update_indicators(self.test_indicators)
        self.ui.update_position_data(self.test_position)
        
        # Add test messages
        self.ui.add_system_message("Connected to TWS", "info")
        self.ui.add_log_message("Application started", "INFO")
        
        # Render complete layout
        layout = self.ui.render()
        
        # Verify all required sections exist and have correct sizes
        self.assertEqual(layout["header"].size, 7, "Header must be 7 lines")
        self.assertEqual(layout["market_status"].size, 15, "Market Status must be 15 lines")
        self.assertEqual(layout["bottom_panels"].size, 12, "Bottom panels must be 12 lines")
        
        # Verify bottom panels split correctly
        bottom_panels = layout["bottom_panels"]
        pnl_panel = bottom_panels["pnl"]
        action_panel = bottom_panels["action"]
        
        # Verify ratio: PnL (1) vs Action (3)
        self.assertEqual(pnl_panel.ratio, 1, "PnL panel ratio should be 1")
        self.assertEqual(action_panel.ratio, 3, "Action panel ratio should be 3")

    def test_phase3_message_handling_system(self):
        """TEST: Feature 3 - Verify message panel integration in header"""
        # Add various message types
        self.ui.add_system_message("TWS Connection established", "info")
        self.ui.add_system_message("Market data received", "success")
        self.ui.add_log_message("Application initialized", "INFO")
        self.ui.add_log_message("Processing market data", "DEBUG")
        
        # Render layout
        layout = self.ui.render()
        header_content = layout["header"]
        
        # Verify messages are integrated
        console = Console(file=StringIO(), width=130)
        console.print(header_content.renderable)
        output = console.file.getvalue()
        
        # Check for message integration (latest 5 messages only per spec)
        self.assertIn("TWS Connection", output, "System messages must be displayed")
        self.assertIn("Application initialized", output, "Log messages must be displayed")
        
        # Verify message count limit
        self.assertLessEqual(len(self.ui.messages), 50, "Message history must be limited")
        self.assertLessEqual(len(self.ui.log_messages), 50, "Log message history must be limited")

    def test_phase3_complete_rendering_without_errors(self):
        """TEST: Complete UI rendering verification without errors"""
        try:
            # Populate with full test data
            self.ui.update_market_data("AAPL", self.test_market_data)
            self.ui.update_indicators(self.test_indicators)
            self.ui.update_position_data(self.test_position)
            self.ui.update_order_status(1001, "Submitted", 0, 100, 0.0)
            self.ui.update_prompt("Buy AAPL at $150.50 (press enter) ?")
            
            # Add messages
            self.ui.add_system_message("All systems operational", "info")
            self.ui.add_log_message("Ready for trading", "INFO")
            
            # Full render test
            layout = self.ui.render()
            
            # Verify layout renders successfully
            console = Console(file=StringIO(), width=130)
            console.print(layout)
            output = console.file.getvalue()
            
            # Basic content verification
            self.assertGreater(len(output), 100, "UI must generate substantial output")
            
            # No error indicators in output
            self.assertNotIn("Error", output)
            self.assertNotIn("Exception", output)
            self.assertNotIn("Failed", output)
            
            # Success - all panels render without errors
            success_message = "✓ Phase 3 UI renders successfully"
            
        except Exception as e:
            self.fail(f"Phase 3 UI rendering failed: {e}")


if __name__ == '__main__':
    # Custom test runner to display results clearly
    unittest.main(verbosity=2)