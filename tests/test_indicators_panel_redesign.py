#!/usr/bin/env python
"""
Comprehensive tests for the redesigned IndicatorsPanel with 4-column layout
"""

import unittest
import sys
import io
from unittest.mock import Mock, patch
from contextlib import redirect_stdout, redirect_stderr

# Add src to path for imports
sys.path.insert(0, '/home/kelp/work/ibx-ai-termui/src')

from ui.panels.indicators_panel import IndicatorsPanel
from rich.console import Console
from rich.text import Text


class TestIndicatorsPanelRedesign(unittest.TestCase):
    """Test the redesigned IndicatorsPanel with 4-column layout"""

    def setUp(self):
        """Set up test fixtures"""
        self.indicators_panel = IndicatorsPanel()
        self.sample_data = {
            "current_price": 150.50,
            "ema9": 149.85,
            "vwap": 150.20,
            "macd": 0.45,
            "macd_signal": 0.32,
            "volume_trend": "increasing",
            "rsi": 65.0
        }

    def test_render_method_with_sample_data(self):
        """Test that the render method works without errors using sample data"""
        try:
            panel = self.indicators_panel.render(self.sample_data)
            self.assertIsNotNone(panel)
            print("\033[92mPASSED\033[0m - IndicatorsPanel render method executes without errors")
        except Exception as e:
            self.fail(f"Render method failed with error: {str(e)}")

    def test_panel_renders_without_errors(self):
        """Test that the panel renders to console without errors"""
        console = Console(file=io.StringIO(), width=80)
        panel = self.indicators_panel.render(self.sample_data)
        
        try:
            console.print(panel)
            output = console.file.getvalue()
            self.assertIsNotNone(output)
            self.assertGreater(len(output), 0)
            print("\033[92mPASSED\033[0m - Panel renders to console without errors")
        except Exception as e:
            self.fail(f"Panel rendering failed with error: {str(e)}")

    def test_all_three_indicators_displayed(self):
        """Test that all three main indicators (EMA, VWAP, MACD) are displayed"""
        console = Console(file=io.StringIO(), width=100)
        panel = self.indicators_panel.render(self.sample_data)
        console.print(panel)
        output = console.file.getvalue()
        
        # Check for indicator names
        self.assertIn("EMA(9)", output)
        self.assertIn("VWAP", output)
        self.assertIn("MACD", output)
        
        # Check for indicator values
        self.assertIn("149.85", output)  # EMA value
        self.assertIn("150.20", output)  # VWAP value
        self.assertIn("0.450", output)   # MACD value
        
        print("\033[92mPASSED\033[0m - All three indicators (EMA, VWAP, MACD) are displayed correctly")

    def test_ema_signal_calculation(self):
        """Test EMA signal calculation based on price vs EMA"""
        # Test price above EMA (BUY signal)
        test_data = self.sample_data.copy()
        test_data["current_price"] = 151.00
        test_data["ema9"] = 149.85
        
        console = Console(file=io.StringIO(), width=100)
        panel = self.indicators_panel.render(test_data)
        console.print(panel)
        output = console.file.getvalue()
        
        self.assertIn("Above", output)
        self.assertIn("BUY", output)
        print("\033[92mPASSED\033[0m - EMA BUY signal calculated correctly when price above EMA")

    def test_vwap_signal_calculation(self):
        """Test VWAP signal calculation based on price vs VWAP"""
        # Test price below VWAP (BEARISH signal)
        test_data = self.sample_data.copy()
        test_data["current_price"] = 149.50
        test_data["vwap"] = 150.20
        
        console = Console(file=io.StringIO(), width=100)
        panel = self.indicators_panel.render(test_data)
        console.print(panel)
        output = console.file.getvalue()
        
        self.assertIn("Below", output)
        self.assertIn("BEARISH", output)
        print("\033[92mPASSED\033[0m - VWAP BEARISH signal calculated correctly when price below VWAP")

    def test_macd_signal_calculation(self):
        """Test MACD signal calculation based on MACD vs signal line"""
        # Test MACD above signal line (BULLISH)
        test_data = self.sample_data.copy()
        test_data["macd"] = 0.45
        test_data["macd_signal"] = 0.32
        
        console = Console(file=io.StringIO(), width=100)
        panel = self.indicators_panel.render(test_data)
        console.print(panel)
        output = console.file.getvalue()
        
        self.assertIn("Above Signal", output)
        self.assertIn("BULLISH", output)
        print("\033[92mPASSED\033[0m - MACD BULLISH signal calculated correctly when MACD above signal line")

    def test_no_data_edge_case(self):
        """Test panel behavior with no indicator data"""
        console = Console(file=io.StringIO(), width=100)
        panel = self.indicators_panel.render({})
        console.print(panel)
        output = console.file.getvalue()
        
        # Check for truncated text "No indicator data…" due to console width
        self.assertTrue("No indicator data" in output or "No indicator data…" in output)
        self.assertIn("TECHNICAL INDICATORS", output)
        print("\033[92mPASSED\033[0m - Panel handles no data case correctly")

    def test_equal_values_edge_case(self):
        """Test behavior when indicator values equal current price"""
        test_data = {
            "current_price": 150.00,
            "ema9": 150.00,
            "vwap": 150.00,
            "macd": 0.32,
            "macd_signal": 0.32,
            "volume_trend": "neutral",
            "rsi": 50.0
        }
        
        console = Console(file=io.StringIO(), width=100)
        panel = self.indicators_panel.render(test_data)
        console.print(panel)
        output = console.file.getvalue()
        
        # Check for neutral signals when values are equal
        self.assertIn("At EMA", output)
        self.assertIn("At VWAP", output)
        self.assertIn("At Signal", output)
        self.assertIn("HOLD", output)
        self.assertIn("NEUTRAL", output)
        print("\033[92mPASSED\033[0m - Panel handles equal values edge case correctly")

    def test_four_column_structure(self):
        """Test that the panel maintains the 4-column structure"""
        console = Console(file=io.StringIO(), width=120)
        panel = self.indicators_panel.render(self.sample_data)
        console.print(panel)
        output = console.file.getvalue()
        
        # Verify the presence of key elements from each column
        # Column 1: Indicator names
        self.assertIn("EMA(9)", output)
        self.assertIn("VWAP", output)
        self.assertIn("MACD", output)
        
        # Column 2: Values
        self.assertIn("$149.85", output)
        self.assertIn("$150.20", output)
        self.assertIn("0.450", output)
        
        # Column 3: Relative position indicators (based on sample data, price > both EMA and VWAP)
        self.assertIn("Above", output)
        self.assertIn("Above Signal", output)
        
        # Column 4: Trading signals (based on actual calculation with sample data)
        self.assertIn("BUY", output)
        self.assertIn("BULLISH", output)
        
        print("\033[92mPASSED\033[0m - Panel maintains proper 4-column structure")

    def test_additional_indicators_display(self):
        """Test that volume trend and RSI are displayed correctly"""
        console = Console(file=io.StringIO(), width=120)
        panel = self.indicators_panel.render(self.sample_data)
        console.print(panel)
        output = console.file.getvalue()
        
        # Check for volume trend
        self.assertIn("Volume Trend:", output)
        self.assertIn("Increasing", output)
        
        # Check for RSI
        self.assertIn("RSI:", output)
        self.assertIn("65.0", output)
        
        print("\033[92mPASSED\033[0m - Additional indicators (Volume Trend, RSI) display correctly")

    def test_missing_indicators_handling(self):
        """Test behavior with partially missing indicator data"""
        partial_data = {
            "current_price": 150.50,
            "ema9": 149.85
            # Missing vwap, macd, macd_signal
        }
        
        try:
            console = Console(file=io.StringIO(), width=100)
            panel = self.indicators_panel.render(partial_data)
            console.print(panel)
            output = console.file.getvalue()
            
            # Should still render without errors, using default values
            self.assertIn("EMA(9)", output)
            self.assertIn("VWAP", output)
            self.assertIn("MACD", output)
            print("\033[92mPASSED\033[0m - Panel handles missing indicators gracefully")
        except Exception as e:
            self.fail(f"Panel failed with partial data: {str(e)}")

    def test_extreme_values_handling(self):
        """Test panel with extreme indicator values"""
        extreme_data = {
            "current_price": 999999.99,
            "ema9": 0.01,
            "vwap": 500000.50,
            "macd": -999.999,
            "macd_signal": 999.999,
            "volume_trend": "decreasing",
            "rsi": 99.9
        }
        
        try:
            console = Console(file=io.StringIO(), width=120)
            panel = self.indicators_panel.render(extreme_data)
            console.print(panel)
            output = console.file.getvalue()
            
            self.assertIsNotNone(output)
            self.assertGreater(len(output), 0)
            print("\033[92mPASSED\033[0m - Panel handles extreme values without errors")
        except Exception as e:
            self.fail(f"Panel failed with extreme values: {str(e)}")


def run_tests():
    """Run all indicator panel tests"""
    print("TEST: Indicators Panel Redesign - Technical Indicators Panel with 4-Column Layout")
    print("=" * 80)
    
    # Test input display
    print("Test Input:")
    print("- current_price: 150.50")
    print("- ema9: 149.85")
    print("- vwap: 150.20")
    print("- macd: 0.45")
    print("- macd_signal: 0.32")
    print("- volume_trend: increasing")
    print("- rsi: 65.0")
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIndicatorsPanelRedesign)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 80)
    print(f"Tests run: {result.testsRun}")
    
    if result.wasSuccessful():
        print(f"\033[92mALL TESTS PASSED\033[0m ({result.testsRun}/{result.testsRun})")
    else:
        failed = len(result.failures) + len(result.errors)
        print(f"\033[91m{failed} TEST(S) FAILED\033[0m ({result.testsRun - failed}/{result.testsRun} passed)")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
                
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()