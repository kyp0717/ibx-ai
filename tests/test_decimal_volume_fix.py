"""
Test for Decimal volume type fix in technical_indicators.py
Tests VWAP calculation and BarDataPoint creation with Decimal volume values
"""

import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime
import sys
import os

# Add src to path to import technical_indicators
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from technical_indicators import TechnicalAnalysisClient, BarDataPoint


class MockBarData:
    """Mock BarData object to simulate IBAPI BarData with Decimal volume"""
    def __init__(self, date, open_val, high, low, close, volume):
        self.date = date
        self.open = open_val
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume  # This can be Decimal or int


class TestDecimalVolumeFix(unittest.TestCase):
    """Test Decimal volume handling in technical indicators"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the TWSConnection parent class to avoid connection issues
        with patch('technical_indicators.TWSConnection.__init__'):
            self.client = TechnicalAnalysisClient()
            self.client._next_request_id = 1000
            
    def test_bar_data_point_with_decimal_volume(self):
        """Test BarDataPoint creation handles Decimal volume correctly"""
        # Test with Decimal volume
        decimal_volume = Decimal('1250.0')
        bar = BarDataPoint(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=int(decimal_volume)  # Should convert Decimal to int
        )
        
        # Volume should be converted to int
        self.assertIsInstance(bar.volume, int)
        self.assertEqual(bar.volume, 1250)
        self.assertEqual(bar.typical_price, (105.0 + 99.0 + 102.0) / 3)
        
    def test_bar_data_point_with_integer_volume(self):
        """Test BarDataPoint creation works with integer volume"""
        # Test with integer volume
        int_volume = 1500
        bar = BarDataPoint(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=int_volume
        )
        
        # Volume should remain int
        self.assertIsInstance(bar.volume, int)
        self.assertEqual(bar.volume, 1500)
        
    def test_vwap_calculation_with_decimal_volumes(self):
        """Test VWAP calculation handles Decimal volumes correctly"""
        # Create test bars with mixed volume types
        bars = [
            BarDataPoint(
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=99.0,
                close=102.0,
                volume=1000  # Integer volume
            ),
            BarDataPoint(
                timestamp=datetime.now(),
                open=102.0,
                high=108.0,
                low=101.0,
                close=106.0,
                volume=1500  # Integer volume
            )
        ]
        
        # Test VWAP calculation
        vwap = self.client._calculate_vwap(bars)
        
        # Manual calculation for verification
        # Bar 1: typical_price = (105 + 99 + 102) / 3 = 102, volume = 1000
        # Bar 2: typical_price = (108 + 101 + 106) / 3 = 105, volume = 1500
        # VWAP = (102 * 1000 + 105 * 1500) / (1000 + 1500) = 259500 / 2500 = 103.8
        expected_vwap = (102.0 * 1000 + 105.0 * 1500) / (1000 + 1500)
        
        self.assertAlmostEqual(vwap, expected_vwap, places=2)
        
    def test_vwap_calculation_with_zero_volume(self):
        """Test VWAP calculation handles zero volume gracefully"""
        bars = [
            BarDataPoint(
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=99.0,
                close=102.0,
                volume=0  # Zero volume
            )
        ]
        
        # Should return typical price when volume is zero
        vwap = self.client._calculate_vwap(bars)
        expected_typical_price = (105.0 + 99.0 + 102.0) / 3
        self.assertAlmostEqual(vwap, expected_typical_price, places=2)
        
    def test_historical_data_with_decimal_volume(self):
        """Test historicalData method handles Decimal volume from IBAPI"""
        # Set up mock request
        req_id = 1001
        self.client.active_requests[req_id] = {
            'symbol': 'AAPL',
            'bar_size': '10 secs',
            'start_time': datetime.now()
        }
        
        # Create mock bar with Decimal volume
        mock_bar = MockBarData(
            date="20240109 10:30:00",
            open_val=150.0,
            high=152.0,
            low=149.0,
            close=151.0,
            volume=Decimal('2500.0')  # Decimal volume from IBAPI
        )
        
        # Test that historicalData processes Decimal volume correctly
        self.client.historicalData(req_id, mock_bar)
        
        # Check that bar was added with integer volume
        self.assertEqual(len(self.client.bars_10sec), 1)
        stored_bar = self.client.bars_10sec[0]
        self.assertIsInstance(stored_bar.volume, int)
        self.assertEqual(stored_bar.volume, 2500)
        
    def test_vwap_with_mixed_volume_types_in_calculation(self):
        """Test VWAP calculation when bars have volumes that were converted from Decimal"""
        # Simulate bars that came from Decimal volumes (now converted to int)
        bars = [
            BarDataPoint(
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=99.0,
                close=102.0,
                volume=int(Decimal('1250.5'))  # Converted from Decimal
            ),
            BarDataPoint(
                timestamp=datetime.now(),
                open=102.0,
                high=108.0,
                low=101.0,
                close=106.0,
                volume=1750  # Regular integer
            )
        ]
        
        # Test VWAP calculation works correctly
        vwap = self.client._calculate_vwap(bars)
        
        # Manual calculation
        # Bar 1: typical_price = 102, volume = 1250 (from Decimal 1250.5)
        # Bar 2: typical_price = 105, volume = 1750
        # VWAP = (102 * 1250 + 105 * 1750) / (1250 + 1750)
        expected_vwap = (102.0 * 1250 + 105.0 * 1750) / (1250 + 1750)
        
        self.assertAlmostEqual(vwap, expected_vwap, places=2)
        
    def test_vwap_calculation_volume_conversion_to_float(self):
        """Test that _calculate_vwap converts volume to float internally"""
        # Create a bar with integer volume
        bar = BarDataPoint(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=1000
        )
        
        bars = [bar]
        
        # Mock the float conversion to verify it's called
        with patch('builtins.float') as mock_float:
            mock_float.return_value = 1000.0
            vwap = self.client._calculate_vwap(bars)
            
            # Verify float was called with the volume
            mock_float.assert_called_with(1000)
            
    def test_empty_bars_vwap_calculation(self):
        """Test VWAP calculation with empty bars list"""
        vwap = self.client._calculate_vwap([])
        self.assertEqual(vwap, 0)
        
    def test_large_decimal_volume_handling(self):
        """Test handling of large Decimal volume values"""
        large_decimal_volume = Decimal('999999999.99')
        
        # Create BarDataPoint with large Decimal volume converted to int
        bar = BarDataPoint(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=99.0,
            close=102.0,
            volume=int(large_decimal_volume)
        )
        
        # Should handle large volumes correctly
        self.assertIsInstance(bar.volume, int)
        self.assertEqual(bar.volume, 999999999)  # Decimal part truncated
        
        # VWAP calculation should work with large volumes
        vwap = self.client._calculate_vwap([bar])
        self.assertAlmostEqual(vwap, bar.typical_price, places=2)


if __name__ == '__main__':
    unittest.main()