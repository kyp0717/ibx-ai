"""
Unit tests for deque slice fix in technical_indicators.py
Tests that historicalDataEnd properly handles deque objects and slice operations
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch, MagicMock
from collections import deque

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from technical_indicators import (
    TechnicalAnalysisClient, 
    BarDataPoint, 
    TechnicalIndicators
)


class TestDequeSliceFix(unittest.TestCase):
    """Test deque slice fix in historicalDataEnd method"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TechnicalAnalysisClient()
        
        # Mock the TWS connection methods
        self.client.reqHistoricalData = Mock()
        self.client.cancelHistoricalData = Mock()
        
    def create_sample_bars(self, count: int, start_price: float = 150.0) -> list:
        """Create sample bar data for testing"""
        bars = []
        base_time = datetime(2023, 1, 1, 9, 30, 0)
        
        for i in range(count):
            timestamp = base_time + timedelta(seconds=i*10)
            price = start_price + (i * 0.5)  # Gradually increasing price
            bar = BarDataPoint(
                timestamp=timestamp,
                open=price,
                high=price + 0.5,
                low=price - 0.3,
                close=price + 0.2,
                volume=1000 + (i * 10)
            )
            bars.append(bar)
        return bars
        
    def test_deque_to_list_conversion_10sec(self):
        """Test that deque is properly converted to list for 10-second bars"""
        # Create sample bars and populate the deque
        sample_bars = self.create_sample_bars(5)
        
        # Populate the deque
        for bar in sample_bars:
            self.client.bars_10sec.append(bar)
            
        # Verify deque is populated correctly
        self.assertEqual(len(self.client.bars_10sec), 5)
        self.assertIsInstance(self.client.bars_10sec, deque)
        
        # Set up active request to simulate historicalDataEnd scenario
        req_id = 1001
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Test that deque slice operations would fail without conversion
        with self.assertRaises(TypeError):
            # This should fail because deques don't support slicing
            _ = self.client.bars_10sec[:-1]
            
        # Call historicalDataEnd to test the fix
        self.client.historicalDataEnd(req_id, "20230101 09:30:00", "20230101 10:30:00")
        
        # Verify that EMA values were calculated (proving the slice operations worked)
        self.assertIsNotNone(self.client.ema9_10sec)
        self.assertIsNotNone(self.client.ema12_10sec)
        self.assertIsNotNone(self.client.ema26_10sec)
        
        # Verify loading flag was reset
        self.assertFalse(self.client.loading_historical_10sec)
        
    def test_deque_to_list_conversion_30sec(self):
        """Test that deque is properly converted to list for 30-second bars"""
        # Create sample bars and populate the deque
        sample_bars = self.create_sample_bars(5)
        
        # Populate the deque
        for bar in sample_bars:
            self.client.bars_30sec.append(bar)
            
        # Verify deque is populated correctly
        self.assertEqual(len(self.client.bars_30sec), 5)
        self.assertIsInstance(self.client.bars_30sec, deque)
        
        # Set up active request to simulate historicalDataEnd scenario
        req_id = 1002
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '30 secs',
            'start_time': datetime.now()
        }
        
        # Call historicalDataEnd to test the fix
        self.client.historicalDataEnd(req_id, "20230101 09:30:00", "20230101 10:30:00")
        
        # Verify that EMA values were calculated (proving the slice operations worked)
        self.assertIsNotNone(self.client.ema9_30sec)
        self.assertIsNotNone(self.client.ema12_30sec)
        self.assertIsNotNone(self.client.ema26_30sec)
        
        # Verify loading flag was reset
        self.assertFalse(self.client.loading_historical_30sec)
        
    def test_ema_calculations_with_converted_list(self):
        """Test that EMA calculations work correctly with converted list"""
        # Create predictable sample data
        sample_bars = []
        prices = [100.0, 101.0, 102.0, 103.0, 104.0]
        base_time = datetime(2023, 1, 1, 9, 30, 0)
        
        for i, price in enumerate(prices):
            timestamp = base_time + timedelta(seconds=i*10)
            bar = BarDataPoint(
                timestamp=timestamp,
                open=price,
                high=price + 0.1,
                low=price - 0.1,
                close=price,
                volume=1000
            )
            sample_bars.append(bar)
            self.client.bars_10sec.append(bar)
            
        # Set up active request
        req_id = 1003
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Call historicalDataEnd
        self.client.historicalDataEnd(req_id, "20230101 09:30:00", "20230101 10:30:00")
        
        # Verify EMA values are reasonable
        self.assertIsNotNone(self.client.ema9_10sec)
        self.assertGreater(self.client.ema9_10sec, 100.0)
        self.assertLess(self.client.ema9_10sec, 105.0)
        
        # Verify indicators were created
        self.assertIsNotNone(self.client.indicators_10sec)
        self.assertIsInstance(self.client.indicators_10sec, TechnicalIndicators)
        
    def test_empty_deque_handling(self):
        """Test that empty deques are handled gracefully"""
        # Set up active request with empty deque
        req_id = 1004
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Verify deque is empty
        self.assertEqual(len(self.client.bars_10sec), 0)
        
        # Call historicalDataEnd with empty deque
        self.client.historicalDataEnd(req_id, "20230101 09:30:00", "20230101 10:30:00")
        
        # Verify loading flag was reset even with empty deque
        self.assertFalse(self.client.loading_historical_10sec)
        
        # Verify EMA values remain None (no calculations possible)
        self.assertIsNone(self.client.ema9_10sec)
        self.assertIsNone(self.client.ema12_10sec)
        self.assertIsNone(self.client.ema26_10sec)
        
    def test_single_bar_deque_handling(self):
        """Test that deques with only one element are handled correctly"""
        # Create single bar
        bar = BarDataPoint(
            timestamp=datetime(2023, 1, 1, 9, 30, 0),
            open=150.0,
            high=150.5,
            low=149.5,
            close=150.2,
            volume=1000
        )
        self.client.bars_10sec.append(bar)
        
        # Set up active request
        req_id = 1005
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Call historicalDataEnd
        self.client.historicalDataEnd(req_id, "20230101 09:30:00", "20230101 10:30:00")
        
        # With single bar, bars_list[:-1] should be empty list, bars_list[-1] should be the single bar
        # EMA should be initialized to the close price of the single bar
        self.assertIsNotNone(self.client.ema9_10sec)
        self.assertEqual(self.client.ema9_10sec, 150.2)  # First EMA value equals the price
        
        # Verify indicators were created
        self.assertIsNotNone(self.client.indicators_10sec)
        self.assertEqual(self.client.indicators_10sec.timestamp, bar.timestamp)
        
    def test_deque_slice_operations_fail_without_conversion(self):
        """Test that slice operations fail on deque objects directly"""
        # Create sample bars
        sample_bars = self.create_sample_bars(3)
        
        # Populate deque
        for bar in sample_bars:
            self.client.bars_10sec.append(bar)
            
        # Test that direct slicing on deque fails
        with self.assertRaises(TypeError):
            _ = self.client.bars_10sec[:-1]
            
        with self.assertRaises(TypeError):
            _ = self.client.bars_10sec[0:2]
            
        # But individual indexing should work
        self.assertEqual(self.client.bars_10sec[-1], sample_bars[-1])
        self.assertEqual(self.client.bars_10sec[0], sample_bars[0])
        
        # Converting to list should allow slicing
        bars_list = list(self.client.bars_10sec)
        self.assertEqual(len(bars_list[:-1]), 2)  # Should work without error
        self.assertEqual(bars_list[-1], sample_bars[-1])
        
    def test_list_conversion_preserves_order(self):
        """Test that converting deque to list preserves the correct order"""
        # Create sample bars with identifiable data
        sample_bars = []
        for i in range(5):
            bar = BarDataPoint(
                timestamp=datetime(2023, 1, 1, 9, 30, i*10),
                open=100.0 + i,
                high=100.5 + i,
                low=99.5 + i,
                close=100.2 + i,
                volume=1000 * (i + 1)
            )
            sample_bars.append(bar)
            self.client.bars_10sec.append(bar)
            
        # Convert to list
        bars_list = list(self.client.bars_10sec)
        
        # Verify order is preserved
        self.assertEqual(len(bars_list), 5)
        for i in range(5):
            self.assertEqual(bars_list[i].close, 100.2 + i)
            self.assertEqual(bars_list[i].volume, 1000 * (i + 1))
            
        # Test slice operations work correctly
        first_four = bars_list[:-1]
        self.assertEqual(len(first_four), 4)
        self.assertEqual(first_four[-1].close, 103.2)  # Last element should be 4th bar
        
        last_bar = bars_list[-1]
        self.assertEqual(last_bar.close, 104.2)  # Last bar should be 5th bar


class TestVWAPCalculationWithConvertedList(unittest.TestCase):
    """Test VWAP calculation works correctly with converted list"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TechnicalAnalysisClient()
        
    def test_vwap_calculation_after_deque_conversion(self):
        """Test VWAP calculation works after deque to list conversion"""
        # Create bars with known VWAP calculation
        bars_data = [
            (100.0, 1000),  # typical_price = 100, volume = 1000
            (101.0, 2000),  # typical_price = 101, volume = 2000  
            (102.0, 1500),  # typical_price = 102, volume = 1500
        ]
        
        # Expected VWAP calculation: typical_price = (high + low + close) / 3
        # For our bars: typical_price = (price + price + price) / 3 = price
        # VWAP = (100*1000 + 101*2000 + 102*1500) / (1000+2000+1500) = (100000 + 202000 + 153000) / 4500 = 455000 / 4500
        expected_vwap = 455000 / 4500
        
        bars = []
        base_time = datetime(2023, 1, 1, 9, 30, 0)
        
        for i, (price, volume) in enumerate(bars_data):
            timestamp = base_time + timedelta(seconds=i*10)
            bar = BarDataPoint(
                timestamp=timestamp,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=volume
            )
            bars.append(bar)
            self.client.bars_10sec.append(bar)
            
        # Test VWAP calculation using the _calculate_vwap method
        # This method should receive a list, not a deque
        bars_list = list(self.client.bars_10sec)
        vwap = self.client._calculate_vwap(bars_list)
        
        self.assertAlmostEqual(vwap, expected_vwap, places=2)


if __name__ == '__main__':
    unittest.main()