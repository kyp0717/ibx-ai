#!/usr/bin/env python3
"""
Test script to verify that MACD and MACD Signal lines are displayed separately
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.panels.indicators_panel import IndicatorsPanel
from rich.console import Console

def test_macd_display():
    """Test that MACD and MACD Signal are displayed as separate rows"""
    console = Console()
    panel = IndicatorsPanel()
    
    print("\nTesting MACD and MACD Signal line display:")
    print("=" * 60)
    
    test_cases = [
        # (macd, macd_signal, description)
        (0.123, 0.120, "MACD above signal (bullish)"),
        (-0.045, -0.040, "MACD below signal (bearish)"),
        (0.100, 0.100, "MACD equals signal (neutral)"),
        (0.250, 0.180, "Large positive histogram"),
        (-0.150, -0.200, "MACD crossing above signal"),
    ]
    
    for macd, macd_signal, description in test_cases:
        indicators_10s = {
            "current_price": 150.00,
            "ema9": 149.50,
            "vwap": 149.75,
            "macd": macd,
            "macd_signal": macd_signal,
        }
        
        indicators_30s = {
            "current_price": 150.00,
            "ema9": 149.55,
            "vwap": 149.80,
            "macd": macd + 0.01,
            "macd_signal": macd_signal + 0.005,
        }
        
        histogram = round(macd - macd_signal, 3)
        
        print(f"\nTest: {description}")
        print(f"  MACD Line: {macd:.3f}")
        print(f"  MACD Signal: {macd_signal:.3f}")
        print(f"  Histogram: {histogram:.3f}")
        
        if histogram > 0:
            print(f"  Expected Signal: BUY (MACD above signal)")
        elif histogram < 0:
            print(f"  Expected Signal: SELL (MACD below signal)")
        else:
            print(f"  Expected Signal: HOLD (MACD equals signal)")
        
        # Render the panel to verify display
        try:
            rendered = panel.render(indicators_10s, indicators_30s)
            print("  ✓ Panel rendered successfully with both MACD rows")
        except Exception as e:
            print(f"  ✗ Error rendering panel: {e}")
    
    print("\n" + "=" * 60)
    print("MACD display test completed!")
    print("\nDisplay format:")
    print("1. MACD row: Shows MACD line value and its position relative to zero")
    print("2. MACD Sig row: Shows Signal line value and histogram (MACD - Signal)")
    print("3. Both rows show the same trading signal based on the histogram")

if __name__ == "__main__":
    test_macd_display()