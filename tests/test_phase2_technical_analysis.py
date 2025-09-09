"""
Unit tests for Phase 2 Technical Analysis Module
Tests EMA, VWAP, MACD calculations and signal generation
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from collections import deque

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from technical_indicators import (
    TechnicalAnalysisClient, 
    BarDataPoint, 
    TechnicalIndicators
)


class TestBarDataPoint(unittest.TestCase):
    """Test BarDataPoint data class"""
    
    def test_bar_data_point_creation(self):
        """Test creating a BarDataPoint instance"""
        timestamp = datetime.now()
        bar = BarDataPoint(
            timestamp=timestamp,
            open=150.0,
            high=155.0,
            low=148.0,
            close=152.0,
            volume=10000
        )
        
        self.assertEqual(bar.timestamp, timestamp)
        self.assertEqual(bar.open, 150.0)
        self.assertEqual(bar.high, 155.0)
        self.assertEqual(bar.low, 148.0)
        self.assertEqual(bar.close, 152.0)
        self.assertEqual(bar.volume, 10000)
        
        # Test typical price calculation (post_init)
        expected_typical = (155.0 + 148.0 + 152.0) / 3
        self.assertAlmostEqual(bar.typical_price, expected_typical, places=2)


class TestTechnicalIndicators(unittest.TestCase):
    """Test TechnicalIndicators data class"""
    
    def test_technical_indicators_creation(self):
        """Test creating TechnicalIndicators instance"""
        timestamp = datetime.now()
        indicators = TechnicalIndicators(
            timestamp=timestamp,
            ema9=150.5,
            vwap=151.2,
            macd=0.25,
            macd_signal=0.18,
            macd_histogram=0.07,
            signal_strength=75.0,
            signal_direction="BUY"
        )
        
        self.assertEqual(indicators.timestamp, timestamp)
        self.assertEqual(indicators.ema9, 150.5)
        self.assertEqual(indicators.vwap, 151.2)
        self.assertEqual(indicators.macd, 0.25)
        self.assertEqual(indicators.macd_signal, 0.18)
        self.assertEqual(indicators.macd_histogram, 0.07)
        self.assertEqual(indicators.signal_strength, 75.0)
        self.assertEqual(indicators.signal_direction, "BUY")


class TestTechnicalAnalysisClient(unittest.TestCase):
    """Test TechnicalAnalysisClient functionality"""
    
    def setUp(self):
        """Set up test client"""
        with patch('technical_indicators.TWSConnection.__init__', return_value=None):
            self.client = TechnicalAnalysisClient()
        
        # Mock IBAPI methods
        self.client.reqHistoricalData = Mock()
        self.client.cancelHistoricalData = Mock()
        
    def test_initial_state(self):
        """Test initial state of TechnicalAnalysisClient"""
        self.assertEqual(len(self.client.bars_10sec), 0)
        self.assertEqual(len(self.client.bars_30sec), 0)
        self.assertIsNone(self.client.indicators_10sec)
        self.assertIsNone(self.client.indicators_30sec)
        self.assertIsNone(self.client.ema9_10sec)
        self.assertIsNone(self.client.ema9_30sec)
        self.assertEqual(self.client.cumulative_volume_10sec, 0)
        self.assertEqual(self.client.cumulative_pv_10sec, 0)
        
    def test_get_next_request_id(self):
        """Test request ID generation"""
        first_id = self.client.get_next_request_id()
        second_id = self.client.get_next_request_id()
        
        self.assertEqual(first_id, 1000)
        self.assertEqual(second_id, 1001)
        
    def test_calculate_ema(self):
        """Test EMA calculation with known values"""
        # First EMA value (no previous)
        first_ema = self.client._calculate_ema(100.0, None, 9)
        self.assertEqual(first_ema, 100.0)
        
        # Second EMA value
        multiplier = 2 / (9 + 1)  # 0.2
        expected_second = (105.0 * multiplier) + (100.0 * (1 - multiplier))
        second_ema = self.client._calculate_ema(105.0, 100.0, 9)
        self.assertAlmostEqual(second_ema, expected_second, places=5)
        
        # Test with real values
        self.assertAlmostEqual(second_ema, 101.0, places=1)
        
    def test_calculate_vwap(self):
        """Test VWAP calculation with sample data"""
        # Create test bars - method only processes the last bar
        bars = [
            BarDataPoint(datetime.now(), 100, 102, 99, 101, 1000),
            BarDataPoint(datetime.now(), 101, 103, 100, 102, 1500),
        ]
        
        # Test VWAP calculation - only latest bar (second one) is processed
        vwap, cum_vol, cum_pv = self.client._calculate_vwap(bars, 0, 0)
        
        # Calculate expected VWAP for latest bar only
        # Latest bar: typical_price = (103+100+102)/3 = 101.67, volume = 1500
        # VWAP = 101.67 (since it's the only bar processed)
        
        self.assertEqual(cum_vol, 1500)  # Only latest bar volume
        expected_typical = (103 + 100 + 102) / 3
        self.assertAlmostEqual(vwap, expected_typical, places=2)
        
    def test_calculate_macd(self):
        """Test MACD calculation and signal line"""
        ema12 = 105.5
        ema26 = 104.2
        previous_signal = None
        
        macd, signal, histogram = self.client._calculate_macd(ema12, ema26, previous_signal)
        
        expected_macd = ema12 - ema26  # 1.3
        self.assertAlmostEqual(macd, expected_macd, places=5)
        self.assertEqual(signal, macd)  # First signal equals MACD
        self.assertAlmostEqual(histogram, 0, places=5)  # First histogram is 0
        
        # Test with previous signal
        macd2, signal2, histogram2 = self.client._calculate_macd(106.0, 104.5, signal)
        expected_macd2 = 1.5
        self.assertAlmostEqual(macd2, expected_macd2, places=5)
        self.assertTrue(signal2 != macd2)  # Signal should be smoothed
        self.assertNotAlmostEqual(histogram2, 0, places=5)  # Histogram should be non-zero
        
    def test_extrapolate_signal_bullish(self):
        """Test signal extrapolation for bullish scenario"""
        price = 105.0
        ema = 100.0  # Price above EMA (bullish)
        vwap = 102.0  # Price above VWAP (bullish)
        macd = 0.5
        histogram = 0.3  # Positive histogram (bullish)
        
        strength, direction = self.client._extrapolate_signal(price, ema, vwap, macd, histogram)
        
        self.assertEqual(direction, "BUY")
        self.assertTrue(strength > 0)
        
    def test_extrapolate_signal_bearish(self):
        """Test signal extrapolation for bearish scenario"""
        price = 95.0
        ema = 100.0  # Price below EMA (bearish)
        vwap = 98.0   # Price below VWAP (bearish)
        macd = -0.5
        histogram = -0.3  # Negative histogram (bearish)
        
        strength, direction = self.client._extrapolate_signal(price, ema, vwap, macd, histogram)
        
        self.assertEqual(direction, "SELL")
        self.assertTrue(strength > 0)
        
    def test_extrapolate_signal_neutral(self):
        """Test signal extrapolation for neutral scenario"""
        price = 100.0
        ema = 100.0  # Price at EMA
        vwap = 100.0  # Price at VWAP
        macd = 0.0
        histogram = 0.0  # No histogram signal
        
        strength, direction = self.client._extrapolate_signal(price, ema, vwap, macd, histogram)
        
        self.assertEqual(direction, "NEUTRAL")
        
    @patch('technical_indicators.logger')
    def test_historical_data_10sec(self, mock_logger):
        """Test handling of 10-second historical data"""
        # Set up request tracking
        req_id = 1001
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Create mock BarData
        mock_bar = Mock()
        mock_bar.date = "20250904 10:30:00"
        mock_bar.open = 150.0
        mock_bar.high = 152.0
        mock_bar.low = 149.0
        mock_bar.close = 151.0
        mock_bar.volume = 1000
        
        # Process the bar
        self.client.historicalData(req_id, mock_bar)
        
        # Check that bar was added to 10sec collection
        self.assertEqual(len(self.client.bars_10sec), 1)
        self.assertEqual(len(self.client.bars_30sec), 0)
        
        # Check that indicators were updated
        self.assertIsNotNone(self.client.indicators_10sec)
        self.assertIsNone(self.client.indicators_30sec)
        self.assertIsNotNone(self.client.ema9_10sec)
        
    @patch('technical_indicators.logger')
    def test_historical_data_30sec(self, mock_logger):
        """Test handling of 30-second historical data"""
        # Set up request tracking
        req_id = 1002
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '30 secs',
            'start_time': datetime.now()
        }
        
        # Create mock BarData
        mock_bar = Mock()
        mock_bar.date = "20250904 10:30:00"
        mock_bar.open = 150.0
        mock_bar.high = 152.0
        mock_bar.low = 149.0
        mock_bar.close = 151.0
        mock_bar.volume = 2000
        
        # Process the bar
        self.client.historicalData(req_id, mock_bar)
        
        # Check that bar was added to 30sec collection
        self.assertEqual(len(self.client.bars_30sec), 1)
        self.assertEqual(len(self.client.bars_10sec), 0)
        
        # Check that indicators were updated
        self.assertIsNotNone(self.client.indicators_30sec)
        self.assertIsNone(self.client.indicators_10sec)
        self.assertIsNotNone(self.client.ema9_30sec)
        
    def test_historical_data_update(self):
        """Test real-time bar updates"""
        with patch.object(self.client, 'historicalData') as mock_hist:
            mock_bar = Mock()
            self.client.historicalDataUpdate(1003, mock_bar)
            mock_hist.assert_called_once_with(1003, mock_bar)
            
    def test_get_relative_values_10sec(self):
        """Test relative values calculation for 10-second timeframe"""
        # Set up mock indicators
        self.client.indicators_10sec = TechnicalIndicators(
            timestamp=datetime.now(),
            ema9=100.0,
            vwap=101.0,
            macd=0.5,
            macd_histogram=0.2
        )
        
        current_price = 105.0
        relative_values = self.client.get_relative_values(current_price, "10sec")
        
        self.assertAlmostEqual(relative_values['ema9_diff'], 5.0)
        self.assertAlmostEqual(relative_values['ema9_diff_pct'], 5.0)
        self.assertAlmostEqual(relative_values['vwap_diff'], 4.0)
        self.assertAlmostEqual(relative_values['vwap_diff_pct'], 3.96, places=2)
        self.assertEqual(relative_values['macd'], 0.5)
        self.assertEqual(relative_values['macd_histogram'], 0.2)
        
    def test_get_relative_values_30sec(self):
        """Test relative values calculation for 30-second timeframe"""
        # Set up mock indicators
        self.client.indicators_30sec = TechnicalIndicators(
            timestamp=datetime.now(),
            ema9=98.0,
            vwap=99.0,
            macd=-0.3,
            macd_histogram=-0.1
        )
        
        current_price = 95.0
        relative_values = self.client.get_relative_values(current_price, "30sec")
        
        self.assertAlmostEqual(relative_values['ema9_diff'], -3.0)
        self.assertAlmostEqual(relative_values['ema9_diff_pct'], -3.06, places=2)
        self.assertAlmostEqual(relative_values['vwap_diff'], -4.0)
        self.assertAlmostEqual(relative_values['vwap_diff_pct'], -4.04, places=2)
        self.assertEqual(relative_values['macd'], -0.3)
        self.assertEqual(relative_values['macd_histogram'], -0.1)
        
    def test_get_combined_signal_both_timeframes(self):
        """Test combined signal from both timeframes"""
        # Set up indicators for both timeframes
        self.client.indicators_10sec = TechnicalIndicators(
            timestamp=datetime.now(),
            signal_strength=80.0,
            signal_direction="BUY"
        )
        
        self.client.indicators_30sec = TechnicalIndicators(
            timestamp=datetime.now(),
            signal_strength=60.0,
            signal_direction="BUY"
        )
        
        strength, direction = self.client.get_combined_signal()
        
        # Expected weighted strength: (80 * 0.6) + (60 * 0.4) = 72
        self.assertAlmostEqual(strength, 72.0)
        self.assertEqual(direction, "BUY")
        
    def test_get_combined_signal_conflicting(self):
        """Test combined signal with conflicting timeframes"""
        # Set up conflicting indicators
        self.client.indicators_10sec = TechnicalIndicators(
            timestamp=datetime.now(),
            signal_strength=70.0,
            signal_direction="BUY"
        )
        
        self.client.indicators_30sec = TechnicalIndicators(
            timestamp=datetime.now(),
            signal_strength=80.0,
            signal_direction="SELL"
        )
        
        strength, direction = self.client.get_combined_signal()
        
        # BUY score: 0.6, SELL score: 0.4 -> BUY wins
        self.assertEqual(direction, "BUY")
        
    def test_get_combined_signal_single_timeframe(self):
        """Test combined signal with only one timeframe"""
        self.client.indicators_10sec = TechnicalIndicators(
            timestamp=datetime.now(),
            signal_strength=75.0,
            signal_direction="SELL"
        )
        
        strength, direction = self.client.get_combined_signal()
        
        self.assertEqual(strength, 75.0)
        self.assertEqual(direction, "SELL")
        
    def test_get_combined_signal_no_data(self):
        """Test combined signal with no indicator data"""
        strength, direction = self.client.get_combined_signal()
        
        self.assertEqual(strength, 0)
        self.assertEqual(direction, "NEUTRAL")
        
    @patch('technical_indicators.Contract')
    def test_request_bar_data(self, mock_contract_class):
        """Test bar data request setup"""
        mock_contract = Mock()
        mock_contract_class.return_value = mock_contract
        
        result = self.client.request_bar_data("AAPL", "10 secs", "1800 S")
        
        self.assertTrue(result)
        self.client.reqHistoricalData.assert_called_once()
        
        # Check request was tracked
        self.assertEqual(len(self.client.active_requests), 1)
        req_info = list(self.client.active_requests.values())[0]
        self.assertEqual(req_info['symbol'], "AAPL")
        self.assertEqual(req_info['bar_size'], "10 secs")
        
    @patch('technical_indicators.Contract')
    def test_start_technical_analysis(self, mock_contract_class):
        """Test starting technical analysis for both timeframes"""
        mock_contract_class.return_value = Mock()
        
        result = self.client.start_technical_analysis("AAPL")
        
        self.assertTrue(result)
        # Should make two requests (10sec and 30sec)
        self.assertEqual(self.client.reqHistoricalData.call_count, 2)
        
    def test_stop_analysis(self):
        """Test stopping all active requests"""
        # Add some mock requests
        self.client.active_requests[1001] = {'symbol': 'AAPL', 'bar_size': '10 secs'}
        self.client.active_requests[1002] = {'symbol': 'AAPL', 'bar_size': '30 secs'}
        
        self.client.stop_analysis()
        
        # Check that cancel was called for both requests
        self.assertEqual(self.client.cancelHistoricalData.call_count, 2)
        self.assertEqual(len(self.client.active_requests), 0)


class TestTechnicalAnalysisIntegration(unittest.TestCase):
    """Integration tests for technical analysis workflow"""
    
    def setUp(self):
        """Set up integration test client"""
        with patch('technical_indicators.TWSConnection.__init__', return_value=None):
            self.client = TechnicalAnalysisClient()
        
        # Mock IBAPI methods
        self.client.reqHistoricalData = Mock()
        self.client.cancelHistoricalData = Mock()
        
    def test_multi_bar_ema_calculation(self):
        """Test EMA calculation across multiple bars"""
        bars = []
        ema_values = []
        
        # Simulate 20 bars with varying prices
        base_time = datetime.now()
        prices = [100, 101, 99, 102, 105, 103, 106, 104, 107, 109,
                 108, 110, 112, 111, 113, 115, 114, 116, 118, 120]
        
        for i, price in enumerate(prices):
            bar_time = base_time + timedelta(seconds=10 * i)
            bar = BarDataPoint(bar_time, price-1, price+1, price-2, price, 1000)
            bars.append(bar)
            
            # Calculate EMA manually
            if i == 0:
                ema = price
            else:
                ema = self.client._calculate_ema(price, ema, 9)
            ema_values.append(ema)
            
        # Verify EMA trend follows price trend
        self.assertTrue(ema_values[-1] > ema_values[0])  # EMA should increase
        self.assertTrue(ema_values[-1] < prices[-1])     # EMA should lag price
        
    def test_vwap_accumulation(self):
        """Test VWAP calculation with accumulating volume"""
        cum_vol = 0
        cum_pv = 0
        
        bars = [
            BarDataPoint(datetime.now(), 100, 102, 98, 101, 1000),
            BarDataPoint(datetime.now(), 101, 103, 99, 102, 1500),
            BarDataPoint(datetime.now(), 102, 104, 100, 103, 2000),
        ]
        
        # Calculate VWAP step by step (each call processes one bar)
        for bar in bars:
            vwap, cum_vol, cum_pv = self.client._calculate_vwap([bar], cum_vol, cum_pv)
            
        # Final VWAP should be weighted average of all bars
        expected_total_vol = 1000 + 1500 + 2000  # 4500
        self.assertEqual(cum_vol, expected_total_vol)
        
        # Calculate expected VWAP manually
        # Bar1: typical_price = (102+98+101)/3 = 100.33, pv = 100330
        # Bar2: typical_price = (103+99+102)/3 = 101.33, pv = 152000
        # Bar3: typical_price = (104+100+103)/3 = 102.33, pv = 204660
        # Total PV = 456990, Total Vol = 4500, VWAP = 101.553
        expected_vwap = 456990 / 4500
        self.assertAlmostEqual(vwap, expected_vwap, places=2)
        
    def test_signal_consistency(self):
        """Test signal consistency across timeframes"""
        # Set up consistent bullish scenario
        timestamp = datetime.now()
        
        # Both timeframes show bullish signals
        bullish_indicators_10sec = TechnicalIndicators(
            timestamp=timestamp,
            ema9=100.0,
            vwap=99.5,
            macd=0.5,
            macd_histogram=0.2,
            signal_strength=80.0,
            signal_direction="BUY"
        )
        
        bullish_indicators_30sec = TechnicalIndicators(
            timestamp=timestamp,
            ema9=101.0,
            vwap=100.0,
            macd=0.3,
            macd_histogram=0.1,
            signal_strength=70.0,
            signal_direction="BUY"
        )
        
        self.client.indicators_10sec = bullish_indicators_10sec
        self.client.indicators_30sec = bullish_indicators_30sec
        
        # Test combined signal
        strength, direction = self.client.get_combined_signal()
        self.assertEqual(direction, "BUY")
        self.assertTrue(strength > 70)  # Should be strong signal
        
        # Test relative values
        current_price = 105.0
        rel_10sec = self.client.get_relative_values(current_price, "10sec")
        rel_30sec = self.client.get_relative_values(current_price, "30sec")
        
        # Both timeframes should show price above indicators (bullish)
        self.assertTrue(rel_10sec['ema9_diff'] > 0)
        self.assertTrue(rel_10sec['vwap_diff'] > 0)
        self.assertTrue(rel_30sec['ema9_diff'] > 0)
        self.assertTrue(rel_30sec['vwap_diff'] > 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        """Set up test client for edge cases"""
        with patch('technical_indicators.TWSConnection.__init__', return_value=None):
            self.client = TechnicalAnalysisClient()
            
    def test_empty_bars_vwap(self):
        """Test VWAP calculation with empty bars"""
        vwap, cum_vol, cum_pv = self.client._calculate_vwap([], 0, 0)
        
        self.assertEqual(vwap, 0)
        self.assertEqual(cum_vol, 0)
        self.assertEqual(cum_pv, 0)
        
    def test_zero_volume_vwap(self):
        """Test VWAP calculation with zero volume bar"""
        bar = BarDataPoint(datetime.now(), 100, 101, 99, 100, 0)
        vwap, cum_vol, cum_pv = self.client._calculate_vwap([bar], 0, 0)
        
        # Should use typical price when volume is zero
        self.assertEqual(vwap, bar.typical_price)
        
    def test_invalid_bar_date_format(self):
        """Test handling of invalid date formats"""
        req_id = 1001
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Mock bar with date-only format
        mock_bar = Mock()
        mock_bar.date = "20250904"  # Date without time
        mock_bar.open = 150.0
        mock_bar.high = 152.0
        mock_bar.low = 149.0
        mock_bar.close = 151.0
        mock_bar.volume = 1000
        
        # Should handle gracefully
        with patch('technical_indicators.logger'):
            self.client.historicalData(req_id, mock_bar)
        
        self.assertEqual(len(self.client.bars_10sec), 1)
        
    def test_unknown_request_id(self):
        """Test handling of unknown request IDs"""
        mock_bar = Mock()
        mock_bar.date = "20250904 10:30:00"
        
        # Should not crash with unknown request ID
        with patch('technical_indicators.logger'):
            self.client.historicalData(9999, mock_bar)
        
        # Should not add any bars
        self.assertEqual(len(self.client.bars_10sec), 0)
        self.assertEqual(len(self.client.bars_30sec), 0)
        
    def test_get_relative_values_no_indicators(self):
        """Test relative values with no indicators"""
        relative_values = self.client.get_relative_values(100.0, "10sec")
        
        self.assertEqual(len(relative_values), 0)
        
    def test_signal_extrapolation_no_indicators(self):
        """Test signal extrapolation with no indicator values"""
        strength, direction = self.client._extrapolate_signal(100.0, None, None, 0, 0)
        
        self.assertEqual(strength, 0)
        self.assertEqual(direction, "NEUTRAL")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST: Feature Phase 2 - Technical Analysis Unit Tests")
    print("="*60 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestBarDataPoint,
        TestTechnicalIndicators,
        TestTechnicalAnalysisClient,
        TestTechnicalAnalysisIntegration,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("\033[92mPASSED: All Phase 2 Technical Analysis tests passed!\033[0m")
    else:
        print(f"\033[91mFAILED: {len(result.failures)} failures, {len(result.errors)} errors\033[0m")
        
        if result.failures:
            print("\nFailures:")
            for test, failure in result.failures:
                print(f"- {test}: {failure.split('AssertionError: ')[-1]}")
                
        if result.errors:
            print("\nErrors:")
            for test, error in result.errors:
                print(f"- {test}: {error.split('Exception: ')[-1]}")
    print("="*60)
    
    sys.exit(0 if result.wasSuccessful() else 1)