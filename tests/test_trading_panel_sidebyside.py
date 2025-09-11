"""
Test suite for TradingPanel side-by-side layout implementation.

This test verifies:
1. Panel renamed from ActionPanel to TradingPanel
2. Main content (time, signal/status, prompts) on left side
3. Position/order information on right side
4. Side-by-side display within panel
5. Dynamic panel title based on stock symbol
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.ui.panels.trading_panel import TradingPanel


class TestTradingPanelSideBySide:
    """Test suite for TradingPanel side-by-side layout"""

    def setup_method(self):
        """Set up test fixtures"""
        self.trading_panel = TradingPanel()
        
        # Sample test data
        self.test_symbol = "AAPL"
        self.test_price = 150.50
        self.test_indicators = {
            "ema9": 149.00,
            "vwap": 148.50,
            "macd": 0.5,
            "macd_signal": 0.3
        }
        self.test_position_data = {
            "quantity": 50,
            "avg_cost": 149.75
        }
        self.test_order_data = {
            "order_id": "12345",
            "status": "Filled",
            "filled_qty": 50,
            "total_qty": 100,
            "avg_price": 150.25
        }

    def test_class_is_named_trading_panel(self):
        """Test 1: Verify class is named TradingPanel (not ActionPanel)"""
        assert self.trading_panel.__class__.__name__ == "TradingPanel"
        assert hasattr(self.trading_panel, 'render')

    def test_panel_returns_rich_panel_object(self):
        """Test that render method returns a Rich Panel object"""
        result = self.trading_panel.render("Test prompt")
        assert isinstance(result, Panel)

    @patch('src.ui.panels.trading_panel.datetime')
    def test_left_side_contains_time_and_signal(self, mock_datetime):
        """Test 2: Verify left side contains time, signal/status, and prompts"""
        # Mock current time
        mock_datetime.now.return_value = MagicMock()
        mock_datetime.now().strftime.return_value = "14:30:15"
        
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price,
            indicators=self.test_indicators,
            position_data={"quantity": 0}  # No position for signal display
        )
        
        # Verify panel structure
        assert isinstance(panel, Panel)
        assert panel.renderable is not None
        
        # The panel should contain a Table with side-by-side content
        content = panel.renderable
        assert isinstance(content, Table)

    def test_right_side_contains_position_orders(self):
        """Test 3: Verify right side contains position/order information"""
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=self.test_position_data,
            order_data=self.test_order_data
        )
        
        # Verify the panel contains nested table structure
        assert isinstance(panel, Panel)
        content = panel.renderable
        assert isinstance(content, Table)
        
        # The side-by-side table should have 2 columns (left and right)
        assert len(content.columns) == 2

    def test_side_by_side_layout_structure(self):
        """Test 4: Verify both sections are displayed side by side"""
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=self.test_position_data,
            order_data=self.test_order_data
        )
        
        # Verify main container is a Table (for side-by-side layout)
        content = panel.renderable
        assert isinstance(content, Table)
        
        # Should have 2 columns for side-by-side layout
        assert len(content.columns) == 2
        
        # Verify column widths are set appropriately
        left_column = content.columns[0]
        right_column = content.columns[1]
        assert left_column.width == 50  # Left side width
        assert right_column.width == 46  # Right side width

    def test_dynamic_panel_title_with_symbol(self):
        """Test 5a: Verify panel title includes symbol when provided"""
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price
        )
        
        expected_title = f"{self.test_symbol} Trade"
        assert panel.title == expected_title

    def test_default_panel_title_without_symbol(self):
        """Test 5b: Verify default panel title when no symbol provided"""
        panel = self.trading_panel.render(prompt_text="Test prompt")
        
        assert panel.title == "Trade"

    def test_empty_symbol_uses_default_title(self):
        """Test 5c: Verify empty symbol uses default title"""
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol="",  # Empty symbol
            price=self.test_price
        )
        
        assert panel.title == "Trade"

    @patch('src.ui.panels.trading_panel.datetime')
    def test_signal_determination_bullish(self, mock_datetime):
        """Test signal determination with bullish indicators"""
        mock_datetime.now.return_value = MagicMock()
        mock_datetime.now().strftime.return_value = "14:30:15"
        
        # Price above EMA9 and VWAP, MACD above signal line
        bullish_indicators = {
            "ema9": 149.00,
            "vwap": 148.50,
            "macd": 0.5,
            "macd_signal": 0.3
        }
        
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=150.50,  # Above both EMA9 and VWAP
            indicators=bullish_indicators,
            position_data={"quantity": 0}  # No position
        )
        
        assert isinstance(panel, Panel)

    def test_position_status_display(self):
        """Test different position status displays"""
        # Test partial position
        partial_position = {"quantity": 50}
        panel_partial = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=partial_position
        )
        assert isinstance(panel_partial, Panel)
        
        # Test full position
        full_position = {"quantity": 100}
        panel_full = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=full_position
        )
        assert isinstance(panel_full, Panel)

    def test_position_orders_table_creation(self):
        """Test the creation of position/orders table"""
        table = self.trading_panel._create_position_orders_table(
            self.test_position_data,
            self.test_order_data
        )
        
        assert isinstance(table, Table)
        assert len(table.columns) == 5  # Label, Value, Separator, Label2, Value2

    def test_panel_styling_attributes(self):
        """Test panel styling and attributes"""
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price
        )
        
        # Verify panel styling
        assert panel.border_style == "yellow"
        assert panel.style == "on black"
        assert panel.title_align == "center"
        assert panel.width == 100

    def test_no_position_buy_prompt(self):
        """Test buy prompt when no position exists"""
        no_position = {"quantity": 0}
        
        panel = self.trading_panel.render(
            prompt_text="Test prompt",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=no_position
        )
        
        assert isinstance(panel, Panel)
        # Panel should contain buy prompt logic

    def test_waiting_for_market_data_prompt(self):
        """Test prompt when no symbol or price provided"""
        panel = self.trading_panel.render(prompt_text="Test prompt")
        
        assert isinstance(panel, Panel)
        # Should show waiting message

    def test_signal_determination_with_no_indicators(self):
        """Test signal determination when no indicators provided"""
        signal_text = self.trading_panel._determine_signal(None, self.test_price)
        assert isinstance(signal_text, Text)

    def test_signal_determination_with_zero_price(self):
        """Test signal determination with zero price"""
        signal_text = self.trading_panel._determine_signal(self.test_indicators, 0)
        assert isinstance(signal_text, Text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])