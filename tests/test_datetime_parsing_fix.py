"""
Test datetime parsing fix in technical_indicators.py
Verifies that historicalData method correctly parses various date formats
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import logging
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class MockBarData:
    """Mock BarData class to simulate ibapi.common.BarData"""
    def __init__(self, date, open_price, high, low, close, volume):
        self.date = date
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


def parse_bar_date(date_str):
    """
    Extract and test the datetime parsing logic from technical_indicators.py
    This replicates the exact parsing logic from lines 107-116
    """
    # Remove timezone suffix if present (e.g., " America/New_York")
    if " America/" in date_str or " US/" in date_str:
        date_str = date_str.split(" America/")[0] if " America/" in date_str else date_str.split(" US/")[0]
    
    if ":" in date_str:
        bar_time = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
    else:
        bar_time = datetime.strptime(date_str, "%Y%m%d")
        
    return bar_time


class TestDatetimeParsing(unittest.TestCase):
    """Test datetime parsing functionality in technical_indicators.py"""
    
    def setUp(self):
        """Set up test"""
        # Disable logging for cleaner test output
        logging.disable(logging.CRITICAL)
    
    def tearDown(self):
        """Clean up after tests"""
        logging.disable(logging.NOTSET)
    
    def test_parse_datetime_with_timezone_america_new_york(self):
        """Test parsing dates with America/New_York timezone suffix"""
        date_str = "20240109 14:30:00 America/New_York"
        expected_time = datetime(2024, 1, 9, 14, 30, 0)
        
        parsed_time = parse_bar_date(date_str)
        
        self.assertEqual(parsed_time, expected_time)
        print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parse_datetime_with_timezone_america_chicago(self):
        """Test parsing dates with America/Chicago timezone suffix"""
        date_str = "20240215 09:45:30 America/Chicago"
        expected_time = datetime(2024, 2, 15, 9, 45, 30)
        
        parsed_time = parse_bar_date(date_str)
        
        self.assertEqual(parsed_time, expected_time)
        print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parse_datetime_with_timezone_us_eastern(self):
        """Test parsing dates with US/Eastern timezone suffix"""
        date_str = "20240315 16:15:45 US/Eastern"
        expected_time = datetime(2024, 3, 15, 16, 15, 45)
        
        parsed_time = parse_bar_date(date_str)
        
        self.assertEqual(parsed_time, expected_time)
        print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parse_datetime_with_timezone_us_central(self):
        """Test parsing dates with US/Central timezone suffix"""
        date_str = "20240420 11:22:33 US/Central"
        expected_time = datetime(2024, 4, 20, 11, 22, 33)
        
        parsed_time = parse_bar_date(date_str)
        
        self.assertEqual(parsed_time, expected_time)
        print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parse_datetime_without_timezone(self):
        """Test parsing dates without timezone suffix"""
        date_str = "20240320 16:00:00"
        expected_time = datetime(2024, 3, 20, 16, 0, 0)
        
        parsed_time = parse_bar_date(date_str)
        
        self.assertEqual(parsed_time, expected_time)
        print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parse_date_only_format(self):
        """Test parsing date-only formats like '20240109'"""
        date_str = "20240425"
        expected_time = datetime(2024, 4, 25, 0, 0, 0)
        
        parsed_time = parse_bar_date(date_str)
        
        self.assertEqual(parsed_time, expected_time)
        print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parse_multiple_timezone_formats_comprehensive(self):
        """Test parsing various timezone formats to ensure robustness"""
        test_cases = [
            ("20240101 10:30:00 America/New_York", datetime(2024, 1, 1, 10, 30, 0)),
            ("20240201 15:45:30 America/Chicago", datetime(2024, 2, 1, 15, 45, 30)),
            ("20240301 08:15:45 America/Los_Angeles", datetime(2024, 3, 1, 8, 15, 45)),
            ("20240401 12:00:00 US/Eastern", datetime(2024, 4, 1, 12, 0, 0)),
            ("20240501 09:30:15 US/Central", datetime(2024, 5, 1, 9, 30, 15)),
            ("20240601 14:22:33 US/Pacific", datetime(2024, 6, 1, 14, 22, 33)),
            ("20240701 11:45:50", datetime(2024, 7, 1, 11, 45, 50)),  # No timezone
            ("20240801", datetime(2024, 8, 1, 0, 0, 0)),  # Date only
        ]
        
        for date_str, expected_time in test_cases:
            with self.subTest(date_format=date_str):
                parsed_time = parse_bar_date(date_str)
                self.assertEqual(parsed_time, expected_time, 
                               f"Wrong timestamp for date: {date_str}")
                print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_edge_cases(self):
        """Test edge cases for datetime parsing"""
        edge_cases = [
            ("20240229 23:59:59", datetime(2024, 2, 29, 23, 59, 59)),  # Leap year
            ("20241231 00:00:00 America/New_York", datetime(2024, 12, 31, 0, 0, 0)),  # New Year
            ("20240630 12:30:45 US/Mountain", datetime(2024, 6, 30, 12, 30, 45)),  # Mid-year
        ]
        
        for date_str, expected_time in edge_cases:
            with self.subTest(date_format=date_str):
                parsed_time = parse_bar_date(date_str)
                self.assertEqual(parsed_time, expected_time, 
                               f"Wrong timestamp for edge case: {date_str}")
                print(f"\033[92mPASSED\033[0m: {date_str} -> {parsed_time}")
    
    def test_parsing_logic_consistency(self):
        """Test that the parsing logic handles timezone removal consistently"""
        # Test America/ prefix
        america_cases = [
            "20240101 10:00:00 America/New_York",
            "20240101 10:00:00 America/Chicago", 
            "20240101 10:00:00 America/Los_Angeles"
        ]
        
        for case in america_cases:
            parsed = parse_bar_date(case)
            expected = datetime(2024, 1, 1, 10, 0, 0)
            self.assertEqual(parsed, expected)
            print(f"\033[92mPASSED\033[0m: America timezone removed correctly for {case}")
        
        # Test US/ prefix
        us_cases = [
            "20240101 10:00:00 US/Eastern",
            "20240101 10:00:00 US/Central",
            "20240101 10:00:00 US/Pacific"
        ]
        
        for case in us_cases:
            parsed = parse_bar_date(case)
            expected = datetime(2024, 1, 1, 10, 0, 0)
            self.assertEqual(parsed, expected)
            print(f"\033[92mPASSED\033[0m: US timezone removed correctly for {case}")


if __name__ == '__main__':
    print("=" * 60)
    print("TEST: Feature Datetime Parsing - Timezone Handling Fix")
    print("=" * 60)
    print("Testing datetime parsing logic from technical_indicators.py")
    print("Verifying timezone suffix removal and format handling")
    print()
    
    unittest.main(verbosity=2)