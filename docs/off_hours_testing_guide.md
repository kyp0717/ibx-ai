# Off-Hours Testing Guide for TWS Trading App

## Overview
This guide explains how to test the TWS Trading App outside regular market hours (Mon-Fri 9:30 AM - 4:00 PM EST).

## Testing Options

### 1. Paper Trading Account (Recommended)

Paper trading works 24/7 and provides the most realistic testing environment.

#### Setup Steps:
1. **Configure IB Gateway/TWS for Paper Trading:**
   - Log into your IB account
   - Select "Paper Trading" mode during login
   - Gateway Paper Port: 4002
   - TWS Paper Port: 7497

2. **Update Connection Settings:**
   - The `.env` file is pre-configured for paper trading
   - Verify `TWS_PORT=7497` for paper trading
   - Change to `TWS_PORT=7496` for live trading (when ready)

3. **Start Paper Trading Session:**
   ```bash
   # Activate virtual environment
   source .venv/bin/activate
   
   # Run the main application
   python src/main.py AAPL 100
   ```

### 2. Run Unit Tests

The test suite includes 18 comprehensive test files covering all features.

#### Execute All Tests:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install pytest if not already installed
uv pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/ -v

# Run specific feature tests
pytest tests/test_feature12_bar_data_unit.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

#### Test Categories:
- **Unit Tests**: Mock TWS responses (no connection needed)
- **Integration Tests**: Test component interactions
- **Live Tests**: Require paper trading connection

### 3. Historical Data Testing

Historical data retrieval works anytime, even when markets are closed.

#### Test Historical Bar Data:
```python
# Example: Fetch historical data for backtesting
from src.bar_data import BarDataClient
from src.connection import TWSConnection

# Connect to paper trading
conn = TWSConnection()
conn.connect("127.0.0.1", 7497, clientId=1)

# Create bar data client
client = BarDataClient(conn)

# Request historical 1-minute bars (works 24/7)
bars = client.get_historical_bars("AAPL", "1 min", "1 D")
```

### 4. Simulation Mode

For testing without any TWS connection:

#### Enable Simulation Mode:
1. Edit `.env` file:
   ```
   ENABLE_SIMULATION=true
   ENABLE_TEST_MODE=true
   ```

2. Run with test mode flag:
   ```python
   # In order_placement.py, test_mode is already implemented
   from src.order_placement import place_order
   
   # Use test_mode=True to simulate order placement
   result = place_order(symbol="AAPL", quantity=100, test_mode=True)
   ```

### 5. Delayed Market Data

IB provides 15-minute delayed data outside market hours.

#### Configure Delayed Data:
1. In TWS/Gateway: Configure → API → Settings → Enable "Use Delayed Market Data"
2. In `.env`: `USE_DELAYED_DATA=true`

## Testing Schedule Recommendations

### Weekday Evening (After 4 PM EST)
- Run unit tests
- Test with paper trading account
- Fetch historical data for analysis

### Weekends
- Full system testing with paper account
- Integration testing
- Performance testing with historical data
- Code refactoring and improvements

### Pre-Market (Before 9:30 AM EST)
- Paper trading with delayed quotes
- Test order placement logic
- Validate risk management rules

## Common Testing Scenarios

### 1. Connection Testing
```bash
# Test connection to paper trading
python -c "from src.connection import test_connection; test_connection(port=7497)"
```

### 2. Order Flow Testing
```bash
# Test order placement without executing
python src/main.py AAPL 100 --test-mode
```

### 3. Data Streaming Testing
```bash
# Test 5-second bar streaming
python src/five_second_bars.py --paper
```

### 4. Historical Data Analysis
```bash
# Test EMA calculation with historical data
python src/bar_data.py --symbol AAPL --period "1 D"
```

## Troubleshooting

### Issue: Cannot connect to TWS/Gateway
**Solution**: 
- Ensure TWS/Gateway is running in Paper Trading mode
- Check firewall settings
- Verify correct port in `.env` file

### Issue: No market data available
**Solution**:
- Enable delayed data in TWS settings
- Use historical data for testing
- Switch to simulation mode

### Issue: Tests failing
**Solution**:
- Ensure virtual environment is activated
- Install all dependencies: `uv pip install -e .[dev]`
- Check if ibapi is properly installed

## Best Practices

1. **Always test in paper trading first** before going live
2. **Use unit tests** for rapid development iteration
3. **Test with historical data** to validate strategies
4. **Document test results** in context/logs/
5. **Run full test suite** before deploying changes

## Next Steps

1. Set up IB Paper Trading account if not already done
2. Run the complete test suite to validate installation
3. Practice order placement in paper trading mode
4. Develop and test trading strategies with historical data
5. Graduate to live trading only after thorough testing

## Support

For issues or questions:
- Review test files in `tests/` directory
- Check logs in `context/logs/`
- Consult IB API documentation
- Review error messages in console output