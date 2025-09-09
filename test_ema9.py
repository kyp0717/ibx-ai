#!/usr/bin/env python
"""Test EMA9 calculation and display logic"""

def calculate_ema(values, period=9):
    """Calculate EMA for a series of values"""
    if not values:
        return None
    
    # First value is SMA
    sma = sum(values[:period]) / period if len(values) >= period else values[0]
    ema_values = [sma]
    
    # Calculate EMA for rest
    multiplier = 2 / (period + 1)
    for i in range(period, len(values)):
        ema = (values[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
        ema_values.append(ema)
    
    return ema_values[-1] if ema_values else None

# Test with sample data
test_prices = [150.0, 150.5, 151.0, 150.8, 151.2, 150.9, 151.5, 151.3, 151.8, 152.0, 151.7]

print('Testing EMA9 Calculation:')
print('='*40)
print(f'Test prices: {test_prices}')
print()

# Calculate EMA9
ema9 = calculate_ema(test_prices, 9)
current_price = test_prices[-1]

print(f'Current Price: ${current_price:.2f}')
print(f'EMA9: ${ema9:.2f}')
print(f'Difference: ${(current_price - ema9):.2f}')
print()

# Show what the panel would display
if current_price > ema9:
    print(f'Display: Price ${current_price:.2f} is ABOVE EMA9 ${ema9:.2f}')
    print(f'Signal: ▲ BUY (bullish)')
elif current_price < ema9:
    print(f'Display: Price ${current_price:.2f} is BELOW EMA9 ${ema9:.2f}')
    print(f'Signal: ▼ SELL (bearish)')
else:
    print(f'Display: Price ${current_price:.2f} EQUALS EMA9 ${ema9:.2f}')
    print(f'Signal: ─ HOLD (neutral)')

print()
print('EMA9 Formula Check:')
print(f'  Multiplier = 2 / (9 + 1) = {2/(9+1):.4f}')
print(f'  EMA = (Current * 0.2) + (Previous EMA * 0.8)')