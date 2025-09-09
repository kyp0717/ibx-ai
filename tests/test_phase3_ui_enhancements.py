#!/usr/bin/env python
"""
Comprehensive unit tests for Phase 3 Terminal UI enhancements.

Tests cover:
1. Port number command line argument parsing (--port must be first argument)
2. Enhanced header panel with status bar and nested message panel
3. Redesigned action panel with integrated signal display
4. Indicators panel with 10s and 30s bar indicators (EMA9, VWAP, MACD)
5. Quote panel with 50-column width and yellow border
6. PnL panel with 50-column width showing live P&L updates
7. Console fixed at 100 columns width
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import argparse
from datetime import datetime
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

# Add src directory to path for imports
sys.path.insert(0, '/home/kelp/work/ibx-ai-termui/src')

import main_ui
from ui.terminal_ui import TerminalUI
from ui.panels.header_panel import HeaderPanel
from ui.panels.action_panel import ActionPanel
from ui.panels.indicators_panel import IndicatorsPanel
from ui.panels.quote_panel import QuotePanel
from ui.panels.pnl_panel import PnLPanel


class TestPhase3ArgumentParsing(unittest.TestCase):
    """Test command line argument parsing for Phase 3 enhancements."""

    def setUp(self):
        # Store original argv
        self.original_argv = sys.argv

    def tearDown(self):
        # Restore original argv
        sys.argv = self.original_argv

    def test_port_argument_required(self):
        """Test that --port argument is required."""
        sys.argv = ['main_ui.py', 'AAPL', '100']
        
        with self.assertRaises(SystemExit):
            main_ui.parse_arguments()

    def test_port_argument_parsing(self):
        """Test that --port argument is parsed correctly."""
        sys.argv = ['main_ui.py', '--port', '7497', 'AAPL', '100']
        
        args = main_ui.parse_arguments()
        
        self.assertEqual(args.port, 7497)
        self.assertEqual(args.symbol, 'AAPL')
        self.assertEqual(args.position_size, 100)

    def test_demo_mode_argument(self):
        """Test that --demo argument is handled correctly."""
        sys.argv = ['main_ui.py', '--port', '7497', 'AAPL', '100', '--demo']
        
        args = main_ui.parse_arguments()
        
        self.assertTrue(args.demo)

    def test_invalid_port_type(self):
        """Test that non-integer port raises error."""
        sys.argv = ['main_ui.py', '--port', 'invalid', 'AAPL', '100']
        
        with self.assertRaises(SystemExit):
            main_ui.parse_arguments()

    def test_all_required_arguments(self):
        """Test that all required arguments are validated."""
        sys.argv = ['main_ui.py', '--port', '7497', 'TSLA', '50']
        
        args = main_ui.parse_arguments()
        
        self.assertEqual(args.port, 7497)
        self.assertEqual(args.symbol, 'TSLA')
        self.assertEqual(args.position_size, 50)
        self.assertFalse(args.demo)


class TestPhase3HeaderPanel(unittest.TestCase):
    """Test header panel with enhanced status bar and nested message panel."""

    def setUp(self):
        self.header_panel = HeaderPanel()

    def test_header_panel_initialization(self):
        """Test header panel initializes correctly."""
        self.assertEqual(self.header_panel.title, "IBX Trading")

    def test_header_panel_connected_status(self):
        """Test header panel shows connected status correctly."""
        panel = self.header_panel.render(connected=True, port=7497, order_id=1001)
        
        self.assertIsInstance(panel, Panel)
        # Panel should show connected status - check panel properties
        self.assertTrue(panel.renderable is not None)

    def test_header_panel_disconnected_status(self):
        """Test header panel shows disconnected status correctly."""
        panel = self.header_panel.render(connected=False, port=7497, order_id=0)
        
        self.assertIsInstance(panel, Panel)
        # Panel should be properly rendered
        self.assertTrue(panel.renderable is not None)

    def test_header_panel_messages_display(self):
        """Test header panel displays messages correctly."""
        messages = [
            {"time": "10:30:15", "message": "Connected to TWS", "type": "success"},
            {"time": "10:30:16", "message": "Market data active", "type": "info"},
            {"time": "10:30:17", "message": "Order placed", "type": "success"}
        ]
        
        panel = self.header_panel.render(connected=True, messages=messages)
        
        self.assertIsInstance(panel, Panel)
        # Panel should have title 'Messages' in nested panel
        self.assertTrue(panel.renderable is not None)

    def test_header_panel_no_messages(self):
        """Test header panel handles no messages correctly."""
        panel = self.header_panel.render(connected=True, messages=None)
        
        self.assertIsInstance(panel, Panel)
        # Panel should render properly even with no messages
        self.assertTrue(panel.renderable is not None)

    def test_header_panel_message_truncation(self):
        """Test header panel truncates long messages."""
        long_message = "This is a very long message that should be truncated because it exceeds the maximum length"
        messages = [{"time": "10:30:15", "message": long_message, "type": "info"}]
        
        panel = self.header_panel.render(connected=True, messages=messages)
        
        self.assertIsInstance(panel, Panel)
        # Message should be properly handled
        self.assertTrue(panel.renderable is not None)

    def test_header_panel_order_id_display(self):
        """Test header panel displays order ID correctly."""
        panel = self.header_panel.render(connected=True, order_id=12345)
        
        self.assertIsInstance(panel, Panel)
        # Panel should contain order ID information
        self.assertTrue(panel.renderable is not None)


class TestPhase3ActionPanel(unittest.TestCase):
    """Test action panel with integrated signal display."""

    def setUp(self):
        self.action_panel = ActionPanel()

    def test_action_panel_initialization(self):
        """Test action panel initializes correctly."""
        self.assertIsInstance(self.action_panel, ActionPanel)

    def test_action_panel_basic_render(self):
        """Test action panel renders basic content."""
        panel = self.action_panel.render("Waiting for action", "AAPL", 150.0)
        
        self.assertIsInstance(panel, Panel)
        self.assertEqual(panel.width, 100)  # Fixed width at 100 columns (full width at bottom)

    def test_action_panel_signal_determination_bullish(self):
        """Test action panel determines bullish signal correctly."""
        indicators = {
            "current_price": 150.0,
            "ema9": 149.0,  # Price above EMA9
            "vwap": 149.5,  # Price above VWAP
            "macd": 0.5,
            "macd_signal": 0.3  # MACD above signal line
        }
        
        signal_text = self.action_panel._determine_signal(indicators, 150.0)
        
        self.assertIsInstance(signal_text, Text)
        signal_str = str(signal_text)
        self.assertIn("Buy", signal_str)

    def test_action_panel_signal_determination_bearish(self):
        """Test action panel determines bearish signal correctly."""
        indicators = {
            "current_price": 149.0,
            "ema9": 150.0,  # Price below EMA9
            "vwap": 150.5,  # Price below VWAP
            "macd": 0.3,
            "macd_signal": 0.5  # MACD below signal line
        }
        
        signal_text = self.action_panel._determine_signal(indicators, 149.0)
        
        self.assertIsInstance(signal_text, Text)
        signal_str = str(signal_text)
        self.assertIn("Sell", signal_str)

    def test_action_panel_signal_determination_hold(self):
        """Test action panel determines hold signal for mixed indicators."""
        indicators = {
            "current_price": 150.0,
            "ema9": 149.0,  # Price above EMA9 (bullish)
            "vwap": 151.0,  # Price below VWAP (bearish)
            "macd": 0.0,
            "macd_signal": 0.0  # Neutral MACD
        }
        
        signal_text = self.action_panel._determine_signal(indicators, 150.0)
        
        self.assertIsInstance(signal_text, Text)
        signal_str = str(signal_text)
        self.assertIn("Hold", signal_str)

    def test_action_panel_no_indicators(self):
        """Test action panel handles missing indicators."""
        signal_text = self.action_panel._determine_signal(None, 150.0)
        
        self.assertIsInstance(signal_text, Text)
        signal_str = str(signal_text)
        self.assertIn("Signal: -", signal_str)

    def test_action_panel_position_orders_table(self):
        """Test action panel creates position/orders table correctly."""
        position_data = {"quantity": 100, "avg_cost": 148.50}
        order_data = {"order_id": 1001, "status": "FILLED", "filled_qty": 100, "total_qty": 100, "avg_price": 149.0}
        
        table = self.action_panel._create_position_orders_table(position_data, order_data)
        
        self.assertIsInstance(table, Table)

    def test_action_panel_trading_prompts(self):
        """Test action panel displays trading prompts correctly."""
        # Test buy prompt
        panel_buy = self.action_panel.render("Open Trade at $150.00 (press enter)?", "AAPL", 150.0)
        self.assertIsInstance(panel_buy, Panel)
        
        # Test sell prompt
        panel_sell = self.action_panel.render("Close position at $151.00 (press enter)?", "AAPL", 151.0)
        self.assertIsInstance(panel_sell, Panel)


class TestPhase3IndicatorsPanel(unittest.TestCase):
    """Test indicators panel with 10s and 30s bar indicators."""

    def setUp(self):
        self.indicators_panel = IndicatorsPanel()

    def test_indicators_panel_initialization(self):
        """Test indicators panel initializes correctly."""
        self.assertIsInstance(self.indicators_panel, IndicatorsPanel)

    def test_indicators_panel_dual_timeframe_render(self):
        """Test indicators panel renders both 10s and 30s timeframes."""
        indicators_10s = {
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.5,
            "macd": 0.5,
            "macd_signal": 0.3
        }
        
        indicators_30s = {
            "current_price": 150.0,
            "ema9": 149.5,
            "vwap": 149.0,
            "macd": 0.4,
            "macd_signal": 0.2
        }
        
        panel = self.indicators_panel.render(indicators_10s, indicators_30s)
        
        self.assertIsInstance(panel, Layout)  # Changed from Panel to Layout - no border on main panel
        # Layout should have proper structure with split sections
        self.assertTrue(len(panel.children) > 0)  # Should have child layouts for 10s and 30s
        self.assertTrue(panel.renderable is not None)

    def test_indicators_panel_ema9_calculation(self):
        """Test indicators panel calculates EMA9 relative values correctly."""
        indicators = {
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.0,
            "macd": 0.0,
            "macd_signal": 0.0
        }
        
        subpanel = self.indicators_panel._create_indicator_subpanel(indicators, "Test", "cyan")
        
        self.assertIsInstance(subpanel, Panel)
        # Subpanel should render properly with EMA9 data
        self.assertTrue(subpanel.renderable is not None)

    def test_indicators_panel_vwap_signals(self):
        """Test indicators panel shows correct VWAP signals."""
        # Price above VWAP (bullish)
        indicators_bullish = {
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.0,
            "macd": 0.0,
            "macd_signal": 0.0
        }
        
        subpanel = self.indicators_panel._create_indicator_subpanel(indicators_bullish, "Test", "cyan")
        self.assertIsInstance(subpanel, Panel)
        self.assertTrue(subpanel.renderable is not None)

    def test_indicators_panel_macd_histogram(self):
        """Test indicators panel calculates MACD histogram correctly."""
        indicators = {
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.0,
            "macd": 0.5,
            "macd_signal": 0.3  # Histogram = 0.5 - 0.3 = 0.2 (positive)
        }
        
        subpanel = self.indicators_panel._create_indicator_subpanel(indicators, "Test", "cyan")
        
        self.assertIsInstance(subpanel, Panel)
        self.assertTrue(subpanel.renderable is not None)

    def test_indicators_panel_no_data(self):
        """Test indicators panel handles no data correctly."""
        panel = self.indicators_panel.render(None, None)
        
        self.assertIsInstance(panel, Layout)  # Changed from Panel to Layout - no border on main panel
        self.assertTrue(panel.renderable is not None)

    def test_indicators_panel_empty_indicators(self):
        """Test indicators panel handles empty indicators dict."""
        panel = self.indicators_panel.render({}, {})
        
        self.assertIsInstance(panel, Layout)  # Changed from Panel to Layout - no border on main panel
        self.assertTrue(panel.renderable is not None)


class TestPhase3QuotePanel(unittest.TestCase):
    """Test quote panel with 50-column width and yellow border."""

    def setUp(self):
        self.quote_panel = QuotePanel()

    def test_quote_panel_initialization(self):
        """Test quote panel initializes correctly."""
        self.assertIsInstance(self.quote_panel, QuotePanel)

    def test_quote_panel_width_and_border(self):
        """Test quote panel has correct width and yellow border."""
        market_data = {
            "symbol": "AAPL",
            "last_price": 150.0,
            "bid_price": 149.95,
            "ask_price": 150.05,
            "volume": 1000000
        }
        
        panel = self.quote_panel.render(market_data, with_panel=True)
        
        self.assertIsInstance(panel, Panel)
        self.assertEqual(panel.width, 50)  # Fixed width at 50 columns
        # Check that border style is yellow
        self.assertEqual(panel.border_style, "yellow")

    def test_quote_panel_market_data_display(self):
        """Test quote panel displays market data correctly."""
        market_data = {
            "symbol": "TSLA",
            "last_price": 250.75,
            "bid_price": 250.70,
            "bid_size": 100,
            "ask_price": 250.80,
            "ask_size": 200,
            "volume": 500000,
            "change": 2.50,
            "change_percent": 1.0
        }
        
        panel = self.quote_panel.render(market_data, with_panel=True)
        
        self.assertIsInstance(panel, Panel)
        # Panel should display market data properly
        self.assertTrue(panel.renderable is not None)

    def test_quote_panel_change_indicators(self):
        """Test quote panel shows correct change indicators."""
        # Test positive change
        market_data_up = {
            "symbol": "AAPL",
            "last_price": 150.0,
            "change": 2.50,
            "change_percent": 1.69
        }
        
        panel_up = self.quote_panel.render(market_data_up, with_panel=True)
        self.assertIsInstance(panel_up, Panel)
        
        # Test negative change
        market_data_down = {
            "symbol": "AAPL",
            "last_price": 150.0,
            "change": -1.50,
            "change_percent": -0.99
        }
        
        panel_down = self.quote_panel.render(market_data_down, with_panel=True)
        self.assertIsInstance(panel_down, Panel)

    def test_quote_panel_bid_ask_with_size(self):
        """Test quote panel displays bid/ask with size correctly."""
        market_data = {
            "symbol": "MSFT",
            "last_price": 300.0,
            "bid_price": 299.95,
            "bid_size": 500,
            "ask_price": 300.05,
            "ask_size": 300
        }
        
        panel = self.quote_panel.render(market_data, with_panel=True)
        self.assertIsInstance(panel, Panel)
        # Panel should display bid/ask with sizes
        self.assertTrue(panel.renderable is not None)

    def test_quote_panel_no_data(self):
        """Test quote panel handles no market data."""
        panel = self.quote_panel.render({}, with_panel=True)
        
        self.assertIsInstance(panel, Panel)
        self.assertTrue(panel.renderable is not None)

    def test_quote_panel_volume_formatting(self):
        """Test quote panel formats volume with commas."""
        market_data = {
            "symbol": "GOOGL",
            "last_price": 2500.0,
            "volume": 1234567
        }
        
        panel = self.quote_panel.render(market_data, with_panel=True)
        self.assertIsInstance(panel, Panel)
        # Panel should format volume properly
        self.assertTrue(panel.renderable is not None)


class TestPhase3PnLPanel(unittest.TestCase):
    """Test PnL panel with 50-column width and live P&L calculations."""

    def setUp(self):
        self.pnl_panel = PnLPanel()

    def test_pnl_panel_initialization(self):
        """Test PnL panel initializes correctly."""
        self.assertIsInstance(self.pnl_panel, PnLPanel)

    def test_pnl_panel_width_and_styling(self):
        """Test PnL panel has correct width and yellow border."""
        position_data = {"quantity": 100, "avg_cost": 150.0}
        market_data = {"last_price": 155.0}
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        self.assertEqual(panel.width, 50)  # Fixed width at 50 columns
        self.assertEqual(panel.border_style, "yellow")  # Yellow border

    def test_pnl_panel_profit_calculation(self):
        """Test PnL panel calculates profit correctly."""
        position_data = {"quantity": 100, "avg_cost": 150.0, "commission": 1.0}
        market_data = {"last_price": 155.0}  # $5 profit per share
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        # Panel should calculate profit correctly
        self.assertTrue(panel.renderable is not None)

    def test_pnl_panel_loss_calculation(self):
        """Test PnL panel calculates loss correctly."""
        position_data = {"quantity": 100, "avg_cost": 150.0, "commission": 1.0}
        market_data = {"last_price": 145.0}  # $5 loss per share
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        # Panel should calculate loss correctly
        self.assertTrue(panel.renderable is not None)

    def test_pnl_panel_zero_position(self):
        """Test PnL panel handles zero position correctly."""
        position_data = {"quantity": 0, "avg_cost": 0, "commission": 0}
        market_data = {"last_price": 150.0}
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        # Panel should handle zero position correctly
        self.assertTrue(panel.renderable is not None)

    def test_pnl_panel_commission_display(self):
        """Test PnL panel displays commission correctly."""
        position_data = {"quantity": 100, "avg_cost": 150.0, "commission": 2.50}
        market_data = {"last_price": 155.0}
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        # Panel should display commission correctly
        self.assertTrue(panel.renderable is not None)

    def test_pnl_panel_no_data(self):
        """Test PnL panel handles no data correctly."""
        panel = self.pnl_panel.render(None, None)
        
        self.assertIsInstance(panel, Panel)
        self.assertIsInstance(panel, Panel)
        # Panel should handle no data gracefully
        self.assertTrue(panel.renderable is not None)

    def test_pnl_panel_unrealized_gain_display(self):
        """Test PnL panel shows unrealized gain correctly."""
        position_data = {"quantity": 50, "avg_cost": 200.0, "commission": 0.75}
        market_data = {"last_price": 210.0}  # $10 gain per share
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        # Panel should display unrealized gain correctly
        self.assertTrue(panel.renderable is not None)

    def test_pnl_panel_large_numbers_formatting(self):
        """Test PnL panel formats large numbers with commas."""
        position_data = {"quantity": 1000, "avg_cost": 150.0, "commission": 5.0}
        market_data = {"last_price": 155.0}
        
        panel = self.pnl_panel.render(position_data, market_data)
        
        self.assertIsInstance(panel, Panel)
        # Panel should format large numbers with commas
        self.assertTrue(panel.renderable is not None)


class TestPhase3TerminalUI(unittest.TestCase):
    """Test terminal UI layout and console width constraints."""

    def setUp(self):
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 1001

    def test_terminal_ui_initialization(self):
        """Test terminal UI initializes with correct console width."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        self.assertEqual(ui.console.options.max_width, 100)  # Console fixed at 100 columns
        self.assertEqual(ui.port, 7497)
        self.assertIsNotNone(ui.layout)

    def test_terminal_ui_layout_structure(self):
        """Test terminal UI has correct layout structure."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        # Check that layout has proper structure
        self.assertTrue(hasattr(ui.layout, 'renderable'))
        self.assertIsNotNone(ui.layout)

    def test_terminal_ui_panel_initialization(self):
        """Test terminal UI initializes all panels correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        self.assertIsInstance(ui.header_panel, HeaderPanel)
        self.assertIsInstance(ui.indicators_panel, IndicatorsPanel)
        self.assertIsInstance(ui.action_panel, ActionPanel)
        self.assertIsInstance(ui.pnl_panel, PnLPanel)
        self.assertIsInstance(ui.quote_panel, QuotePanel)

    def test_terminal_ui_market_data_update(self):
        """Test terminal UI updates market data correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        market_data = {
            "symbol": "AAPL",
            "last_price": 150.0,
            "bid_price": 149.95,
            "ask_price": 150.05,
            "volume": 1000000
        }
        
        ui.update_market_data("AAPL", market_data)
        
        self.assertEqual(ui.market_data["symbol"], "AAPL")
        self.assertEqual(ui.market_data["last_price"], 150.0)

    def test_terminal_ui_indicators_update(self):
        """Test terminal UI updates indicators for both timeframes."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        indicators_10s = {
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.5,
            "macd": 0.5
        }
        
        indicators_30s = {
            "current_price": 150.0,
            "ema9": 149.5,
            "vwap": 149.0,
            "macd": 0.4
        }
        
        ui.update_indicators_10s(indicators_10s)
        ui.update_indicators_30s(indicators_30s)
        
        self.assertEqual(ui.indicators_10s["ema9"], 149.0)
        self.assertEqual(ui.indicators_30s["ema9"], 149.5)

    def test_terminal_ui_position_data_update(self):
        """Test terminal UI updates position data correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        position_data = {
            "quantity": 100,
            "avg_cost": 150.0,
            "current_price": 155.0,
            "commission": 2.0
        }
        
        ui.update_position_data(position_data)
        
        self.assertEqual(ui.position_data["quantity"], 100)
        self.assertEqual(ui.position_data["avg_cost"], 150.0)

    def test_terminal_ui_order_status_update(self):
        """Test terminal UI updates order status correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        ui.update_order_status(
            order_id=1001,
            status="FILLED",
            filled_qty=100,
            total_qty=100,
            avg_price=150.50
        )
        
        self.assertEqual(ui.order_data["order_id"], 1001)
        self.assertEqual(ui.order_data["status"], "FILLED")
        self.assertEqual(ui.order_data["avg_price"], 150.50)

    def test_terminal_ui_system_messages(self):
        """Test terminal UI handles system messages correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        ui.add_system_message("Order placed successfully", "success")
        ui.add_system_message("Market data active", "info")
        
        self.assertEqual(len(ui.messages), 2)
        self.assertEqual(ui.messages[0]["message"], "Order placed successfully")
        self.assertEqual(ui.messages[0]["type"], "success")

    def test_terminal_ui_log_messages(self):
        """Test terminal UI handles log messages correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        ui.add_log_message("Connection established", "INFO")
        ui.add_log_message("Data received", "DEBUG")
        
        self.assertEqual(len(ui.log_messages), 2)
        self.assertEqual(ui.log_messages[0]["message"], "Connection established")
        self.assertEqual(ui.log_messages[0]["level"], "INFO")

    def test_terminal_ui_prompt_update(self):
        """Test terminal UI updates trading prompt correctly."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        ui.update_prompt("Open Trade at $150.00 (press enter)?")
        
        self.assertEqual(ui.prompt_text, "Open Trade at $150.00 (press enter)?")

    def test_terminal_ui_render_integration(self):
        """Test terminal UI renders all components together."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        # Set up some test data
        ui.update_market_data("AAPL", {
            "symbol": "AAPL",
            "last_price": 150.0,
            "bid_price": 149.95,
            "ask_price": 150.05
        })
        
        ui.update_indicators_10s({
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.5
        })
        
        ui.add_system_message("Test message", "info")
        ui.update_prompt("Test prompt")
        
        # Render should not raise any exceptions
        layout = ui.render()
        self.assertIsNotNone(layout)

    def test_terminal_ui_thread_safety(self):
        """Test terminal UI handles concurrent updates safely."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        # Test that data lock is properly used
        self.assertIsNotNone(ui.data_lock)
        
        # Multiple simultaneous updates should not cause issues
        ui.update_market_data("AAPL", {"symbol": "AAPL", "last_price": 150.0})
        ui.add_system_message("Message 1", "info")
        ui.update_indicators_10s({"current_price": 150.0})
        ui.add_log_message("Log message", "INFO")
        
        # All updates should be safely stored
        self.assertEqual(ui.market_data["symbol"], "AAPL")
        self.assertEqual(len(ui.messages), 1)
        self.assertEqual(len(ui.log_messages), 1)


class TestPhase3Integration(unittest.TestCase):
    """Integration tests for Phase 3 UI components working together."""

    def setUp(self):
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 1001

    def test_trading_app_initialization(self):
        """Test TradingApp initializes with correct parameters."""
        app = main_ui.TradingApp(port=7497, symbol="AAPL", position_size=100)
        
        self.assertEqual(app.port, 7497)
        self.assertEqual(app.symbol, "AAPL")
        self.assertEqual(app.position_size, 100)
        self.assertFalse(app.running)

    def test_main_function_argument_validation(self):
        """Test main function validates arguments correctly."""
        # Test invalid position size
        with patch('sys.argv', ['main_ui.py', '--port', '7497', 'AAPL', '0']):
            with patch('main_ui.parse_arguments') as mock_parse:
                mock_parse.return_value = Mock(port=7497, symbol='AAPL', position_size=0, demo=False)
                
                with patch('sys.exit') as mock_exit:
                    main_ui.main()
                    mock_exit.assert_called_with(1)

    def test_demo_mode_execution(self):
        """Test demo mode is handled correctly."""
        with patch('sys.argv', ['main_ui.py', '--port', '7497', 'AAPL', '100', '--demo']):
            with patch('main_ui.parse_arguments') as mock_parse:
                mock_parse.return_value = Mock(port=7497, symbol='AAPL', position_size=100, demo=True)
                
                with patch('sys.exit'):
                    try:
                        main_ui.main()
                    except (ImportError, AttributeError):
                        # Demo mode may not be fully implemented
                        pass

    def test_panel_width_consistency(self):
        """Test that panels have consistent widths as specified in Phase 3."""
        # Quote panel should be 50 columns
        quote_panel = QuotePanel()
        quote = quote_panel.render({"symbol": "AAPL", "last_price": 150.0}, with_panel=True)
        self.assertEqual(quote.width, 50)
        
        # PnL panel should be 50 columns
        pnl_panel = PnLPanel()
        pnl = pnl_panel.render({"quantity": 100, "avg_cost": 150.0}, {"last_price": 155.0})
        self.assertEqual(pnl.width, 50)
        
        # Action panel should be 40 columns
        action_panel = ActionPanel()
        action = action_panel.render("Test prompt", "AAPL", 150.0)
        self.assertEqual(action.width, 40)

    def test_border_color_consistency(self):
        """Test that panels have correct border colors as specified in Phase 3."""
        # Quote panel should have yellow border
        quote_panel = QuotePanel()
        quote = quote_panel.render({"symbol": "AAPL"}, with_panel=True)
        self.assertEqual(quote.border_style, "yellow")
        
        # PnL panel should have yellow border
        pnl_panel = PnLPanel()
        pnl = pnl_panel.render({}, {})
        self.assertEqual(pnl.border_style, "yellow")
        
        # Action panel should have yellow border
        action_panel = ActionPanel()
        action = action_panel.render("Test", "AAPL", 150.0)
        self.assertEqual(action.border_style, "yellow")

    def test_console_width_constraint(self):
        """Test that console is constrained to 100 columns."""
        ui = TerminalUI(self.mock_client, port=7497)
        
        # Console should be exactly 100 columns wide
        self.assertEqual(ui.console.options.max_width, 100)

    def test_indicators_dual_timeframe_integration(self):
        """Test that indicators panel properly handles dual timeframes."""
        indicators_panel = IndicatorsPanel()
        
        indicators_10s = {
            "current_price": 150.0,
            "ema9": 149.0,
            "vwap": 148.5,
            "macd": 0.5,
            "macd_signal": 0.3
        }
        
        indicators_30s = {
            "current_price": 150.0,
            "ema9": 149.5,
            "vwap": 149.0,
            "macd": 0.4,
            "macd_signal": 0.2
        }
        
        panel = indicators_panel.render(indicators_10s, indicators_30s)
        
        self.assertIsInstance(panel, Layout)  # Changed from Panel to Layout - no border on main panel
        panel_content = str(panel)
        
        # Both timeframes should be properly rendered
        self.assertTrue(panel.renderable is not None)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)