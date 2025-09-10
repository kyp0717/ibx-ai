# TWS Trading App - Launch Instructions

## Prerequisites
1. **Interactive Brokers TWS or IB Gateway** running with API enabled
   - Port: 7500 (default for paper trading)
   - Enable API connections in TWS Configuration

2. **Python 3.13+** and **uv** installed
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **IB API Python Client** - must be installed manually after downloading from IB

## Setup

1. Install dependencies:
   ```bash
   uv pip install -e .
   # Or for development:
   uv pip install -e ".[dev]"
   ```

2. Install IB API Client:
   ```bash
   # Download TWS API from Interactive Brokers website first
   uv pip install /path/to/TWS_API/source/pythonclient
   ```

3. Configure environment (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Launch Application

### Live Trading Mode
```bash
uv run python src/main_ui.py <SYMBOL> <POSITION_SIZE>

# Example:
uv run python src/main_ui.py AAPL 100
```

### Demo Mode (UI only, no TWS connection)
```bash
uv run python src/main_ui.py AAPL 100 --demo
```

## Usage
- Press **Enter** to confirm trade actions when prompted
- Use **Ctrl+C** to exit the application

## Troubleshooting
- Ensure TWS/IB Gateway is running before launching
- Check API settings in TWS Configuration → API → Settings
- Verify port 7500 is not blocked by firewall
- For connection issues, check TWS API logs