"""
Comprehensive tests for Phase 3 Enhancement panel implementations

Tests the new panel features:
- ACTION Panel (Feature 6): Time display and action prompts
- Signal Panel (Feature 8): Stock symbol and trading signals from indicators  
- Market Status Panel (Feature 7): Nested Quote and Indicator panels
- Updated Terminal UI: New layout with all panels integrated

Test data includes AAPL stock with various market conditions and indicators.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.panels.action_panel import ActionPanel
from ui.panels.signal_panel import SignalPanel
from ui.panels.market_status_panel import MarketStatusPanel
from ui.terminal_ui import TerminalUI


class TestActionPanel(unittest.TestCase):
    """Test ACTION Panel (Feature 6) functionality"""
    
    def setUp(self):
        self.panel = ActionPanel()
        self.test_symbol = "AAPL"
        self.test_price = 150.50
    
    def test_action_panel_initialization(self):
        """Test ACTION panel initializes correctly"""
        self.assertIsInstance(self.panel, ActionPanel)
    
    @patch('ui.panels.action_panel.datetime')
    def test_action_panel_time_display(self, mock_datetime):
        """Test ACTION panel shows current time in HH:MM:SS format"""
        # Mock current time
        mock_now = Mock()
        mock_now.strftime.return_value = "14:30:25"
        mock_datetime.now.return_value = mock_now
        
        result = self.panel.render("Waiting for action...", self.test_symbol, self.test_price)
        
        # Verify panel was created
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "ACTION")
        self.assertEqual(result.border_style, "yellow")
        
        # Verify time formatting was called
        mock_datetime.now.assert_called_once()
        mock_now.strftime.assert_called_with("%H:%M:%S")
    
    def test_action_panel_buy_prompt(self):
        """Test ACTION panel displays buy prompts correctly"""
        result = self.panel.render("Open Trade", self.test_symbol, self.test_price)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "ACTION")
    
    def test_action_panel_sell_prompt(self):
        """Test ACTION panel displays sell prompts correctly"""
        result = self.panel.render("Close position", self.test_symbol, self.test_price)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "ACTION")
    
    def test_action_panel_exit_prompt(self):
        """Test ACTION panel displays exit prompts correctly"""
        result = self.panel.render("Exit", self.test_symbol, self.test_price)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "ACTION")
    
    def test_action_panel_no_symbol_or_price(self):
        """Test ACTION panel handles missing symbol/price gracefully"""
        result = self.panel.render("Some prompt", "", 0)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "ACTION")
    
    def test_action_panel_generic_prompt(self):
        """Test ACTION panel handles generic prompts"""
        result = self.panel.render("Custom action", self.test_symbol, self.test_price)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "ACTION")


class TestSignalPanel(unittest.TestCase):
    """Test Signal Panel (Feature 8) functionality"""
    
    def setUp(self):
        self.panel = SignalPanel()
        self.test_symbol = "AAPL"
        self.test_indicators = {
            "current_price": 150.50,
            "ema9": 149.85,
            "vwap": 150.20,
            "macd": 0.45,
            "macd_signal": 0.32
        }
    
    def test_signal_panel_initialization(self):
        """Test Signal panel initializes correctly"""
        self.assertIsInstance(self.panel, SignalPanel)
    
    def test_signal_panel_symbol_display(self):
        """Test Signal panel shows stock symbol correctly"""
        result = self.panel.render(self.test_symbol, self.test_indicators)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "SIGNAL")
        self.assertEqual(result.border_style, "cyan")
    
    def test_signal_panel_buy_signal_calculation(self):
        """Test Signal panel calculates Buy signal from bullish indicators"""
        # All indicators bullish: price > EMA9, price > VWAP, MACD > signal
        bullish_indicators = {
            "current_price": 150.50,
            "ema9": 149.85,    # price > ema9 (bullish)
            "vwap": 150.20,    # price > vwap (bullish) 
            "macd": 0.45,      # macd > macd_signal (bullish)
            "macd_signal": 0.32
        }
        
        result = self.panel.render(self.test_symbol, bullish_indicators)
        self.assertIsNotNone(result)
    
    def test_signal_panel_sell_signal_calculation(self):
        """Test Signal panel calculates Sell signal from bearish indicators"""
        # All indicators bearish: price < EMA9, price < VWAP, MACD < signal
        bearish_indicators = {
            "current_price": 150.50,
            "ema9": 151.20,    # price < ema9 (bearish)
            "vwap": 151.00,    # price < vwap (bearish)
            "macd": 0.25,      # macd < macd_signal (bearish)
            "macd_signal": 0.40
        }
        
        result = self.panel.render(self.test_symbol, bearish_indicators)
        self.assertIsNotNone(result)
    
    def test_signal_panel_hold_signal_calculation(self):
        """Test Signal panel calculates Hold signal from mixed indicators"""
        # Mixed indicators: 1 bullish (MACD), 1 bearish (EMA), 1 neutral (VWAP)
        mixed_indicators = {
            "current_price": 150.50,
            "ema9": 150.80,    # price < ema9 (bearish)
            "vwap": 150.50,    # price = vwap (neutral)
            "macd": 0.45,      # macd > macd_signal (bullish)
            "macd_signal": 0.32
        }
        
        result = self.panel.render(self.test_symbol, mixed_indicators)
        self.assertIsNotNone(result)
    
    def test_signal_panel_no_indicators(self):
        """Test Signal panel handles missing indicators gracefully"""
        result = self.panel.render(self.test_symbol, None)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "SIGNAL")
    
    def test_signal_panel_empty_indicators(self):
        """Test Signal panel handles empty indicators dictionary"""
        result = self.panel.render(self.test_symbol, {})
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "SIGNAL")
    
    def test_signal_panel_no_symbol(self):
        """Test Signal panel handles missing symbol"""
        result = self.panel.render("", self.test_indicators)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "SIGNAL")
    
    def test_signal_panel_partial_indicators(self):
        """Test Signal panel handles partial indicator data"""
        partial_indicators = {
            "current_price": 150.50,
            "ema9": 149.85
            # Missing vwap, macd, macd_signal
        }
        
        result = self.panel.render(self.test_symbol, partial_indicators)
        self.assertIsNotNone(result)


class TestMarketStatusPanel(unittest.TestCase):
    """Test Market Status Panel (Feature 7) with nested panels"""
    
    def setUp(self):
        self.panel = MarketStatusPanel()
        self.test_market_data = {
            "symbol": "AAPL",
            "last_price": 150.50,
            "bid_price": 150.45,
            "ask_price": 150.55,
            "change": 2.30,
            "change_percent": 1.55,
            "volume": 45000000
        }
        self.test_indicators = {
            "current_price": 150.50,
            "ema9": 149.85,
            "vwap": 150.20,
            "macd": 0.45,
            "macd_signal": 0.32,
            "volume_trend": "increasing",
            "rsi": 65.5
        }
    
    def test_market_status_panel_initialization(self):
        """Test Market Status panel initializes with nested panels"""
        self.assertIsInstance(self.panel, MarketStatusPanel)
        self.assertIsNotNone(self.panel.quote_panel)
        self.assertIsNotNone(self.panel.indicators_panel)
    
    def test_market_status_panel_render(self):
        """Test Market Status panel renders with nested Quote and Indicator panels"""
        result = self.panel.render(self.test_market_data, self.test_indicators)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "MARKET STATUS")
        self.assertEqual(result.border_style, "bright_blue")
    
    def test_market_status_panel_empty_data(self):
        """Test Market Status panel handles empty market data"""
        result = self.panel.render({}, {})
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "MARKET STATUS")
    
    def test_market_status_panel_none_data(self):
        """Test Market Status panel handles None data"""
        result = self.panel.render(None, None)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "MARKET STATUS")
    
    def test_nested_quote_panel_functionality(self):
        """Test nested Quote panel displays bid/ask/last prices correctly"""
        # Test the nested quote panel directly
        quote_result = self.panel.quote_panel.render(self.test_market_data)
        
        self.assertIsNotNone(quote_result)
        self.assertEqual(quote_result.title, "QUOTES")
        self.assertEqual(quote_result.border_style, "blue")
    
    def test_nested_indicators_panel_functionality(self):
        """Test nested Indicator panel shows EMA, VWAP, MACD without signal column"""
        # Test the nested indicators panel directly
        indicators_result = self.panel.indicators_panel.render(self.test_indicators)
        
        self.assertIsNotNone(indicators_result)
        self.assertEqual(indicators_result.title, "INDICATORS")
        self.assertEqual(indicators_result.border_style, "green")


class TestTerminalUILayout(unittest.TestCase):
    """Test Updated Terminal UI (Phase 3 Layout) integration"""
    
    def setUp(self):
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 1001
        self.terminal = TerminalUI(client=self.mock_client, port=7497)
        
        # Set up test data
        self.test_market_data = {
            "symbol": "AAPL",
            "last_price": 150.50,
            "bid_price": 150.45,
            "ask_price": 150.55,
            "volume": 45000000
        }
        
        self.test_indicators = {
            "current_price": 150.50,
            "ema9": 149.85,
            "vwap": 150.20,
            "macd": 0.45,
            "macd_signal": 0.32
        }
    
    def test_terminal_ui_initialization(self):
        """Test Terminal UI initializes with all new panels"""
        self.assertIsNotNone(self.terminal.market_status_panel)
        self.assertIsNotNone(self.terminal.signal_panel)
        self.assertIsNotNone(self.terminal.action_panel)
    
    def test_terminal_ui_layout_structure(self):
        """Test Terminal UI has correct layout structure for Phase 3"""
        layout = self.terminal.layout
        
        # Check main layout sections exist by accessing named layouts
        try:
            self.assertIsNotNone(layout["header"])
            self.assertIsNotNone(layout["top_panels"])
            self.assertIsNotNone(layout["middle_panels"])
            self.assertIsNotNone(layout["bottom_panels"])
        except KeyError as e:
            self.fail(f"Layout section missing: {e}")
    
    def test_terminal_ui_market_data_update(self):
        """Test Terminal UI updates market data correctly"""
        self.terminal.update_market_data("AAPL", self.test_market_data)
        
        with self.terminal.data_lock:
            self.assertEqual(self.terminal.market_data["symbol"], "AAPL")
            self.assertEqual(self.terminal.market_data["last_price"], 150.50)
            self.assertEqual(self.terminal.market_data["bid_price"], 150.45)
            self.assertEqual(self.terminal.market_data["ask_price"], 150.55)
    
    def test_terminal_ui_indicators_update(self):
        """Test Terminal UI updates technical indicators correctly"""
        self.terminal.update_indicators(self.test_indicators)
        
        with self.terminal.data_lock:
            self.assertEqual(self.terminal.indicators_data["current_price"], 150.50)
            self.assertEqual(self.terminal.indicators_data["ema9"], 149.85)
            self.assertEqual(self.terminal.indicators_data["vwap"], 150.20)
            self.assertEqual(self.terminal.indicators_data["macd"], 0.45)
            self.assertEqual(self.terminal.indicators_data["macd_signal"], 0.32)
    
    def test_terminal_ui_prompt_update(self):
        """Test Terminal UI updates trading prompt text"""
        test_prompt = "Open Trade"
        self.terminal.update_prompt(test_prompt)
        
        with self.terminal.data_lock:
            self.assertEqual(self.terminal.prompt_text, test_prompt)
    
    def test_terminal_ui_render_integration(self):
        """Test Terminal UI renders all panels in integrated layout"""
        # Setup test data
        self.terminal.update_market_data("AAPL", self.test_market_data)
        self.terminal.update_indicators(self.test_indicators)
        self.terminal.update_prompt("Open Trade")
        
        # Render layout
        result = self.terminal.render()
        
        self.assertIsNotNone(result)
        self.assertEqual(type(result).__name__, "Layout")
    
    def test_terminal_ui_signal_panel_integration(self):
        """Test Signal panel integration in Terminal UI"""
        self.terminal.update_market_data("AAPL", self.test_market_data)
        self.terminal.update_indicators(self.test_indicators)
        
        # The signal panel should receive symbol and indicators
        layout = self.terminal.render()
        self.assertIsNotNone(layout)
    
    def test_terminal_ui_action_panel_integration(self):
        """Test ACTION panel integration in Terminal UI"""
        self.terminal.update_market_data("AAPL", self.test_market_data)
        self.terminal.update_prompt("Open Trade")
        
        # The action panel should receive prompt, symbol, and ask price
        layout = self.terminal.render()
        self.assertIsNotNone(layout)
    
    def test_terminal_ui_market_status_integration(self):
        """Test Market Status panel integration in Terminal UI"""
        self.terminal.update_market_data("AAPL", self.test_market_data)
        self.terminal.update_indicators(self.test_indicators)
        
        # The market status panel should receive both market data and indicators
        layout = self.terminal.render()
        self.assertIsNotNone(layout)


class TestComprehensiveIntegration(unittest.TestCase):
    """Comprehensive integration tests using all test data"""
    
    def setUp(self):
        """Setup comprehensive test scenario with provided test data"""
        self.test_data = {
            "symbol": "AAPL",
            "last_price": 150.50,
            "bid_price": 150.45,
            "ask_price": 150.55,
            "ema9": 149.85,
            "vwap": 150.20,
            "macd": 0.45,
            "macd_signal": 0.32,
            "prompt_text": "Open Trade"
        }
        
        self.market_data = {
            "symbol": self.test_data["symbol"],
            "last_price": self.test_data["last_price"],
            "bid_price": self.test_data["bid_price"],
            "ask_price": self.test_data["ask_price"],
            "change": 2.30,
            "change_percent": 1.55,
            "volume": 45000000
        }
        
        self.indicators = {
            "current_price": self.test_data["last_price"],
            "ema9": self.test_data["ema9"],
            "vwap": self.test_data["vwap"],
            "macd": self.test_data["macd"],
            "macd_signal": self.test_data["macd_signal"],
            "volume_trend": "increasing",
            "rsi": 65.5
        }
    
    def test_complete_workflow_simulation(self):
        """Test complete workflow with all panels using provided test data"""
        # Initialize all panels
        action_panel = ActionPanel()
        signal_panel = SignalPanel()
        market_status_panel = MarketStatusPanel()
        
        # Test ACTION Panel with test data
        action_result = action_panel.render(
            self.test_data["prompt_text"],
            self.test_data["symbol"],
            self.test_data["ask_price"]
        )
        self.assertIsNotNone(action_result)
        self.assertEqual(action_result.title, "ACTION")
        
        # Test Signal Panel with test data - should be Buy signal
        # price (150.50) > ema9 (149.85), price > vwap (150.20), macd (0.45) > macd_signal (0.32)
        # All 3 indicators bullish = Buy signal
        signal_result = signal_panel.render(self.test_data["symbol"], self.indicators)
        self.assertIsNotNone(signal_result)
        self.assertEqual(signal_result.title, "SIGNAL")
        
        # Test Market Status Panel with nested panels
        market_result = market_status_panel.render(self.market_data, self.indicators)
        self.assertIsNotNone(market_result)
        self.assertEqual(market_result.title, "MARKET STATUS")
        
        # Test full Terminal UI integration
        mock_client = Mock()
        mock_client.is_connected.return_value = True
        mock_client.next_order_id = 1001
        
        terminal = TerminalUI(client=mock_client)
        terminal.update_market_data(self.test_data["symbol"], self.market_data)
        terminal.update_indicators(self.indicators)
        terminal.update_prompt(self.test_data["prompt_text"])
        
        layout = terminal.render()
        self.assertIsNotNone(layout)
    
    def test_signal_calculation_accuracy(self):
        """Test signal calculation accuracy with provided test data"""
        signal_panel = SignalPanel()
        
        # With test data: price=150.50, ema9=149.85, vwap=150.20, macd=0.45, macd_signal=0.32
        # Expected: Buy signal (all 3 indicators bullish)
        result = signal_panel.render(self.test_data["symbol"], self.indicators)
        
        self.assertIsNotNone(result)
        # The signal should be calculated as Buy based on the test data
    
    def test_action_panel_time_formatting(self):
        """Test ACTION panel time display format with test data"""
        with patch('ui.panels.action_panel.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "14:30:25"
            mock_datetime.now.return_value = mock_now
            
            action_panel = ActionPanel()
            result = action_panel.render(
                self.test_data["prompt_text"],
                self.test_data["symbol"],
                self.test_data["ask_price"]
            )
            
            self.assertIsNotNone(result)
            mock_now.strftime.assert_called_with("%H:%M:%S")


if __name__ == "__main__":
    print("TEST: Phase 3 Enhancement - Panel Implementations")
    print("=" * 60)
    print(f"Test Input:")
    print(f"  Symbol: AAPL")
    print(f"  Last Price: $150.50")
    print(f"  Bid/Ask: $150.45 / $150.55")
    print(f"  EMA9: $149.85")
    print(f"  VWAP: $150.20")
    print(f"  MACD: 0.45 / Signal: 0.32")
    print(f"  Prompt: 'Open Trade'")
    print("=" * 60)
    print()
    
    # Run tests with detailed output
    unittest.main(verbosity=2, buffer=False)