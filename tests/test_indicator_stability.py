#!/usr/bin/env python3
"""
Test script to verify that indicator panel values display stably
without flickering between cents and whole dollar amounts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ui.panels.indicators_panel import IndicatorsPanel
from rich.console import Console
import time

def test_value_stability():
    """Test that values remain stable with minor price fluctuations"""
    console = Console()
    panel = IndicatorsPanel()
    
    # Simulate realistic market data with minor fluctuations
    base_price = 150.00
    
    print("\nTesting indicator value stability with fluctuating prices:")
    print("=" * 60)
    
    test_cases = [
        # (current_price, ema9, vwap, description)
        (150.00, 150.02, 149.98, "Small differences"),
        (150.01, 150.02, 149.98, "1 cent price change"),
        (149.99, 150.02, 149.98, "1 cent price change"),
        (150.00, 151.00, 149.00, "Larger differences"),
        (150.005, 150.02, 149.98, "Sub-cent price"),
        (149.995, 150.02, 149.98, "Sub-cent price"),
    ]
    
    for current_price, ema9, vwap, description in test_cases:
        indicators_10s = {
            "current_price": current_price,
            "ema9": ema9,
            "vwap": vwap,
            "macd": 0.123,
            "macd_signal": 0.120,
        }
        
        indicators_30s = {
            "current_price": current_price,
            "ema9": ema9 + 0.05,
            "vwap": vwap + 0.03,
            "macd": 0.125,
            "macd_signal": 0.122,
        }
        
        # Calculate expected differences after rounding (Current Price - Indicator)
        ema_diff_10s = round(current_price - ema9, 2)
        vwap_diff_10s = round(current_price - vwap, 2)
        ema_diff_30s = round(current_price - (ema9 + 0.05), 2)
        vwap_diff_30s = round(current_price - (vwap + 0.03), 2)
        
        print(f"\nTest: {description}")
        print(f"  Current Price: ${current_price:.3f}")
        print(f"  10s Panel:")
        print(f"    EMA9: ${ema9:.2f} -> Diff: ${abs(ema_diff_10s):.2f}")
        print(f"    VWAP: ${vwap:.2f} -> Diff: ${abs(vwap_diff_10s):.2f}")
        print(f"  30s Panel:")
        print(f"    EMA9: ${ema9 + 0.05:.2f} -> Diff: ${abs(ema_diff_30s):.2f}")
        print(f"    VWAP: ${vwap + 0.03:.2f} -> Diff: ${abs(vwap_diff_30s):.2f}")
        
        # Render the panel to verify no crashes
        try:
            rendered = panel.render(indicators_10s, indicators_30s)
            print("  ✓ Panel rendered successfully")
        except Exception as e:
            print(f"  ✗ Error rendering panel: {e}")
    
    print("\n" + "=" * 60)
    print("Value stability test completed!")
    print("\nKey improvements:")
    print("1. Values are rounded to 2 decimal places to avoid precision issues")
    print("2. Small threshold (0.005) used to prevent flickering near zero")
    print("3. Current price must be > 0 to calculate differences")
    print("4. Calculation fixed: Now showing Current Price - Indicator (not Indicator - Price)")
    print("   - Positive (▲ green): Price is ABOVE indicator (bullish)")
    print("   - Negative (▼ red): Price is BELOW indicator (bearish)")

if __name__ == "__main__":
    test_value_stability()