#!/usr/bin/env python
"""Test indicators display logic"""

import sys
sys.path.insert(0, 'src')

from ui.panels.indicators_panel import IndicatorsPanel

# Create test scenarios
test_scenarios = [
    {
        'name': 'EMA below price, VWAP above price',
        'data': {
            'current_price': 150.00,
            'ema9': 149.50,  # EMA is $0.50 below price
            'vwap': 150.50,  # VWAP is $0.50 above price
            'macd': 0.5,
            'macd_signal': 0.3
        }
    },
    {
        'name': 'EMA above price, VWAP below price',
        'data': {
            'current_price': 150.00,
            'ema9': 150.75,  # EMA is $0.75 above price
            'vwap': 149.25,  # VWAP is $0.75 below price
            'macd': -0.2,
            'macd_signal': 0.1
        }
    }
]

panel = IndicatorsPanel()

for scenario in test_scenarios:
    print(f"\nScenario: {scenario['name']}")
    print("="*50)
    
    data = scenario['data']
    price = data['current_price']
    ema = data['ema9']
    vwap = data['vwap']
    
    print(f"Current Price: ${price:.2f}")
    print(f"EMA9: ${ema:.2f} (difference: ${ema - price:+.2f})")
    print(f"VWAP: ${vwap:.2f} (difference: ${vwap - price:+.2f})")
    
    # According to requirements:
    # - When indicator is above stock price, use green arrow
    # - When indicator is below stock price, use red arrow
    
    print("\nExpected arrows per requirements:")
    if ema > price:
        print(f"  EMA9: Green ▲ (indicator above price)")
    elif ema < price:
        print(f"  EMA9: Red ▼ (indicator below price)")
    else:
        print(f"  EMA9: Dash ─ (indicator equals price)")
        
    if vwap > price:
        print(f"  VWAP: Green ▲ (indicator above price)")
    elif vwap < price:
        print(f"  VWAP: Red ▼ (indicator below price)")
    else:
        print(f"  VWAP: Dash ─ (indicator equals price)")
    
    print("\nTrading signals (standard interpretation):")
    if price > ema:
        print(f"  EMA9: BUY (price above EMA is bullish)")
    elif price < ema:
        print(f"  EMA9: SELL (price below EMA is bearish)")
    else:
        print(f"  EMA9: HOLD (price equals EMA)")
        
    if price > vwap:
        print(f"  VWAP: BUY (price above VWAP is bullish)")
    elif price < vwap:
        print(f"  VWAP: SELL (price below VWAP is bearish)")
    else:
        print(f"  VWAP: HOLD (price equals VWAP)")

print("\n" + "="*50)
print("Summary:")
print("- Arrows show indicator position relative to price")
print("- Green ▲ = indicator ABOVE price")
print("- Red ▼ = indicator BELOW price")
print("- Trading signals follow standard interpretation")