"""
Comprehensive test suite for Trading Panel Feature 6 implementation
Tests all position scenarios and dynamic content requirements
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from io import StringIO
from rich.console import Console
from src.ui.panels.action_panel import ActionPanel


class TestTradingPanelFeature6:
    """Test suite for Trading Panel Feature 6 requirements"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.action_panel = ActionPanel()
        self.test_symbol = "AAPL"
        self.test_price = 150.75
        
        # Mock indicators for signal testing
        self.test_indicators = {
            "ema9": 148.50,
            "vwap": 149.25,
            "macd": 0.5,
            "macd_signal": 0.3
        }
        
        # Mock position data for different scenarios
        self.zero_position = {"quantity": 0, "avg_cost": 0}
        self.partial_position = {"quantity": 50, "avg_cost": 150.25}
        self.full_position = {"quantity": 100, "avg_cost": 150.00}
        
        # Mock order data
        self.test_order = {
            "order_id": "12345",
            "status": "Submitted",
            "filled_qty": 0,
            "total_qty": 100,
            "avg_price": 0
        }
    
    def _render_panel_to_string(self, panel):
        """Helper method to render Rich panel to string for testing"""
        console = Console(file=StringIO(), width=100, legacy_windows=False)
        console.print(panel)
        return console.file.getvalue()

    def test_panel_title_changes_with_symbol(self):
        """Test 1: Panel title changes dynamically based on stock symbol"""
        # Test with AAPL symbol
        panel = self.action_panel.render(
            prompt_text="test",
            symbol="AAPL",
            price=self.test_price,
            position_data=self.zero_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "AAPL Trade" in panel_str
        
        # Test with different symbol
        panel = self.action_panel.render(
            prompt_text="test",
            symbol="TSLA",
            price=250.50,
            position_data=self.zero_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "TSLA Trade" in panel_str
        
        # Test with no symbol
        panel = self.action_panel.render(
            prompt_text="test",
            symbol="",
            price=0,
            position_data=self.zero_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "Trade" in panel_str

    @patch('src.ui.panels.action_panel.datetime')
    def test_position_zero_display(self, mock_datetime):
        """Test 2: When position is 0 - shows time, signal, and buy prompt"""
        # Mock current time
        mock_datetime.now.return_value.strftime.return_value = "14:30:15"
        
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            indicators=self.test_indicators,
            position_data=self.zero_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        
        # Check first line contains time
        assert "[ 14:30:15 ]" in panel_str
        
        # Check signal is displayed (Buy signal expected with test indicators)
        assert "** Signal: Buy **" in panel_str
        
        # Check second line shows buy prompt
        assert f"Buy {self.test_symbol} at {self.test_price:.2f}" in panel_str
        assert "(press enter) ?" in panel_str

    @patch('src.ui.panels.action_panel.datetime')
    def test_partial_position_display(self, mock_datetime):
        """Test 3: When position is between 0 and 100 - shows opening position status"""
        # Mock current time
        mock_datetime.now.return_value.strftime.return_value = "14:30:15"
        
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=self.partial_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        
        # Check first line contains time and opening position message
        assert "[ 14:30:15 ]" in panel_str
        assert "** Opening position ... **" in panel_str
        
        # Check second line shows review message
        assert "Review position status (see panel to the right)" in panel_str

    @patch('src.ui.panels.action_panel.datetime')
    def test_full_position_display(self, mock_datetime):
        """Test 4: When position is 100 or more - shows filled position and sell prompt"""
        # Mock current time
        mock_datetime.now.return_value.strftime.return_value = "14:30:15"
        
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=self.full_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        
        # Check first line contains time and filled message
        assert "[ 14:30:15 ]" in panel_str
        assert "** Position is filled! **" in panel_str
        
        # Check second line shows sell prompt
        assert f"Sell {self.test_symbol} at {self.test_price:.2f}" in panel_str
        assert "(press enter) ?" in panel_str

    def test_signal_determination_buy(self):
        """Test 5: Signal determination logic - Buy signal"""
        # Price above all indicators should give Buy signal
        buy_indicators = {
            "ema9": 148.00,  # Below current price
            "vwap": 149.00,  # Below current price
            "macd": 0.5,     # Above signal line
            "macd_signal": 0.3
        }
        
        signal_text = self.action_panel._determine_signal(buy_indicators, 150.00)
        assert "** Signal: Buy **" in str(signal_text)

    def test_signal_determination_sell(self):
        """Test 6: Signal determination logic - Sell signal"""
        # Price below all indicators should give Sell signal
        sell_indicators = {
            "ema9": 152.00,  # Above current price
            "vwap": 151.50,  # Above current price
            "macd": 0.3,     # Below signal line
            "macd_signal": 0.5
        }
        
        signal_text = self.action_panel._determine_signal(sell_indicators, 150.00)
        assert "** Signal: Sell **" in str(signal_text)

    def test_signal_determination_hold(self):
        """Test 7: Signal determination logic - Hold signal"""
        # Mixed signals should give Hold signal
        hold_indicators = {
            "ema9": 148.00,  # Below current price (bullish)
            "vwap": 152.00,  # Above current price (bearish)
            "macd": 0.3,     # Below signal line (bearish)
            "macd_signal": 0.3  # Equal (neutral)
        }
        
        signal_text = self.action_panel._determine_signal(hold_indicators, 150.00)
        assert "** Signal: Hold **" in str(signal_text)

    def test_panel_styling_and_layout(self):
        """Test 8: Panel styling and layout requirements"""
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=self.zero_position,
            order_data=self.test_order
        )
        
        panel_str = self._render_panel_to_string(panel)
        
        # Check yellow border styling
        assert "yellow" in str(panel.border_style)
        
        # Check panel width
        assert panel.width == 100
        
        # Check position/orders section is included
        assert "Order ID:" in panel_str
        assert "Size:" in panel_str

    def test_edge_cases(self):
        """Test 9: Edge cases and error handling"""
        # Test with no symbol or price
        panel = self.action_panel.render(
            prompt_text="test",
            symbol="",
            price=0,
            position_data=None
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "Waiting for market data..." in panel_str
        
        # Test with None indicators
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            indicators=None,
            position_data=self.zero_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "** Signal: - **" in panel_str

    def test_position_quantities_boundary(self):
        """Test 10: Position quantity boundary conditions"""
        # Test exactly 100 shares
        exactly_100_position = {"quantity": 100, "avg_cost": 150.00}
        
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=exactly_100_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "** Position is filled! **" in panel_str
        assert f"Sell {self.test_symbol}" in panel_str
        
        # Test exactly 1 share
        one_share_position = {"quantity": 1, "avg_cost": 150.00}
        
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=one_share_position
        )
        
        panel_str = self._render_panel_to_string(panel)
        assert "** Opening position ... **" in panel_str

    def test_time_format_display(self):
        """Test 11: Time format is HH:MM:SS as specified"""
        with patch('src.ui.panels.action_panel.datetime') as mock_datetime:
            # Test different time formats
            test_times = ["09:05:30", "14:30:15", "23:59:59"]
            
            for test_time in test_times:
                mock_datetime.now.return_value.strftime.return_value = test_time
                
                panel = self.action_panel.render(
                    prompt_text="test",
                    symbol=self.test_symbol,
                    price=self.test_price,
                    position_data=self.zero_position
                )
                
                panel_str = self._render_panel_to_string(panel)
                assert f"[ {test_time} ]" in panel_str

    def test_position_orders_integration(self):
        """Test 12: Position and orders section integration"""
        panel = self.action_panel.render(
            prompt_text="test",
            symbol=self.test_symbol,
            price=self.test_price,
            position_data=self.partial_position,
            order_data=self.test_order
        )
        
        panel_str = self._render_panel_to_string(panel)
        
        # Check order information is displayed
        assert "Order ID:" in panel_str
        assert "12345" in panel_str
        assert "Status:" in panel_str
        assert "Submitted" in panel_str
        
        # Check position information is displayed
        assert "Size:" in panel_str
        assert "50" in panel_str  # Position quantity
        assert "Avg Cost:" in panel_str
        assert "150.25" in panel_str  # Position avg cost


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main(["-v", __file__])