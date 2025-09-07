# Simulation Mode Enhancement Guide

## Overview
This guide outlines how to enhance the existing `test_mode` functionality to create a comprehensive simulation mode for off-hours testing without TWS connection.

## Current Implementation

The app already has `test_mode` parameter in:
- `order_placement.py`: Functions accept `test_mode=True` to simulate user input
- Mock responses in test files for unit testing

## Proposed Enhancements

### 1. Market Data Simulator

Create a new module `src/market_simulator.py`:

```python
class MarketDataSimulator:
    """Generates realistic market data for testing"""
    
    def __init__(self, symbol: str, base_price: float = 100.0):
        self.symbol = symbol
        self.base_price = base_price
        self.volatility = 0.02  # 2% daily volatility
        
    def generate_quote(self) -> dict:
        """Generate random bid/ask quote"""
        # Add random walk with volatility
        
    def generate_bar(self, interval: str) -> MinuteBar:
        """Generate OHLCV bar data"""
        # Create realistic bar patterns
        
    def stream_quotes(self, callback, frequency_ms: int = 1000):
        """Stream quotes at specified frequency"""
        # Continuous quote generation
```

### 2. Order Execution Simulator

Enhance `src/order_placement.py`:

```python
class OrderSimulator:
    """Simulates order execution without TWS"""
    
    def __init__(self, initial_balance: float = 100000):
        self.balance = initial_balance
        self.positions = {}
        self.orders = []
        
    def place_order(self, symbol: str, quantity: int, 
                   order_type: str = "MKT") -> OrderResult:
        """Simulate order placement and execution"""
        # Simulate fill based on current market
        # Update positions and balance
        # Return realistic OrderResult
        
    def get_positions(self) -> dict:
        """Return current positions"""
        
    def calculate_pnl(self, current_prices: dict) -> float:
        """Calculate P&L based on simulated prices"""
```

### 3. Configuration Integration

Update `.env` handling in `src/config.py`:

```python
from pydantic_settings import BaseSettings

class SimulationSettings(BaseSettings):
    enable_simulation: bool = False
    simulation_data_file: str = "mock_data/sample_quotes.json"
    simulation_volatility: float = 0.02
    simulation_fill_probability: float = 0.95
    simulation_slippage_bps: int = 5  # basis points
    
    class Config:
        env_file = ".env"
```

### 4. Main Application Integration

Modify `src/main.py` to support simulation mode:

```python
def create_client(args):
    """Create appropriate client based on mode"""
    if config.enable_simulation:
        return SimulatedTWSClient()
    elif config.trading_mode == "PAPER":
        return TWSConnection(port=7497)  # Paper trading
    else:
        return TWSConnection(port=7496)  # Live trading
```

### 5. Historical Data Playback

Create `src/data_playback.py`:

```python
class DataPlayback:
    """Replay historical data for backtesting"""
    
    def __init__(self, data_file: str):
        self.data = pd.read_csv(data_file)
        self.current_index = 0
        
    def get_next_bar(self) -> MinuteBar:
        """Get next historical bar"""
        
    def replay_session(self, callback, speed_multiplier: float = 1.0):
        """Replay full trading session"""
```

## Implementation Steps

### Phase 1: Basic Simulation (1-2 days)
1. Create `market_simulator.py` with quote generation
2. Add `OrderSimulator` class to `order_placement.py`
3. Update configuration to read simulation settings

### Phase 2: Integration (1 day)
1. Modify `main.py` to detect and use simulation mode
2. Create factory functions for client creation
3. Add simulation status display to UI

### Phase 3: Advanced Features (2-3 days)
1. Implement historical data playback
2. Add realistic market patterns (gaps, trends, volatility clusters)
3. Create performance metrics tracking
4. Add slippage and commission simulation

### Phase 4: Testing Tools (1 day)
1. Create test scenarios (bull/bear markets, high volatility)
2. Build comparison tools (simulated vs real results)
3. Add debugging and visualization tools

## Usage Examples

### Basic Simulation Mode
```bash
# Enable simulation in .env
ENABLE_SIMULATION=true

# Run with simulation
uv run python src/main.py AAPL 100
```

### With Historical Playback
```bash
# Use historical data file
SIMULATION_DATA_FILE=data/AAPL_20240101.csv

# Run backtest
uv run python src/main.py AAPL 100 --backtest
```

### Custom Volatility Testing
```bash
# High volatility scenario
SIMULATION_VOLATILITY=0.05  # 5% volatility

# Run stress test
uv run python src/main.py AAPL 100 --stress-test
```

## Testing the Simulation

### Unit Tests
Create `tests/test_simulation.py`:
```python
def test_market_simulator():
    """Test quote generation"""
    
def test_order_simulator():
    """Test simulated execution"""
    
def test_pnl_calculation():
    """Test P&L accuracy"""
```

### Integration Tests
```python
def test_full_simulation_cycle():
    """Test complete trading cycle in simulation"""
    # Place orders
    # Check positions
    # Verify P&L
    # Test risk limits
```

## Benefits

1. **24/7 Testing**: No market hours restrictions
2. **Rapid Development**: Instant feedback without TWS delays
3. **Scenario Testing**: Test edge cases and extreme conditions
4. **Performance Testing**: Benchmark strategies without risk
5. **CI/CD Integration**: Automated testing in pipelines

## Future Enhancements

1. **Multi-Asset Support**: Simulate portfolios with correlations
2. **Options Simulation**: Add options pricing and Greeks
3. **Network Latency**: Simulate realistic delays
4. **Market Events**: Simulate halts, circuit breakers
5. **ML Integration**: Use ML models for realistic price generation

## Conclusion

This simulation mode enhancement provides comprehensive off-hours testing capability, enabling:
- Development without TWS connection
- Strategy validation before paper trading
- Performance benchmarking
- Risk scenario analysis

The modular design allows incremental implementation while maintaining compatibility with existing code.