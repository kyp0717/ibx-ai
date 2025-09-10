#!/usr/bin/env python
"""
Test valid bar sizes for IBAPI
"""

import sys
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Valid bar sizes according to IBAPI documentation
VALID_BAR_SIZES = [
    "1 secs", "5 secs", "10 secs", "15 secs", "30 secs",  # Seconds
    "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "20 mins", "30 mins",  # Minutes  
    "1 hour", "2 hours", "3 hours", "4 hours", "8 hours",  # Hours
    "1 day", "1 week", "1 month"  # Days/Weeks/Months
]

def test_bar_size(client, symbol, bar_size):
    """Test if a specific bar size works"""
    from ibapi.contract import Contract
    
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    
    req_id = 5000 + VALID_BAR_SIZES.index(bar_size)
    
    # Track response
    client.test_results[bar_size] = {"requested": True, "received": False, "bars": 0}
    
    logger.info(f"Testing bar size: {bar_size}")
    
    client.reqHistoricalData(
        reqId=req_id,
        contract=contract,
        endDateTime="",
        durationStr="1 D",  # 1 day of data
        barSizeSetting=bar_size,
        whatToShow="TRADES",
        useRTH=0,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )
    
    # Wait for response
    time.sleep(2)
    
    return client.test_results[bar_size]["received"]

def main():
    from technical_indicators import TechnicalAnalysisClient
    
    client = TechnicalAnalysisClient()
    client.test_results = {}
    
    # Override historicalData to track responses
    original_historicalData = client.historicalData
    def track_historicalData(reqId, bar):
        # Find which bar size this is for
        for i, bar_size in enumerate(VALID_BAR_SIZES):
            if reqId == 5000 + i:
                client.test_results[bar_size]["received"] = True
                client.test_results[bar_size]["bars"] += 1
                break
        return original_historicalData(reqId, bar)
    client.historicalData = track_historicalData
    
    # Connect
    logger.info("Connecting to TWS...")
    if not client.connect_to_tws(host="127.0.0.1", port=7497, client_id=99):
        logger.error("Failed to connect")
        return
    
    time.sleep(1)
    
    # Test specific bar sizes
    test_sizes = ["10 secs", "30 secs", "1 min", "5 secs"]
    
    for bar_size in test_sizes:
        success = test_bar_size(client, "AAPL", bar_size)
        if success:
            logger.info(f"✓ {bar_size}: WORKS - Received {client.test_results[bar_size]['bars']} bars")
        else:
            logger.warning(f"✗ {bar_size}: FAILED - No data received")
        time.sleep(1)
    
    # Summary
    logger.info("\nSUMMARY:")
    for bar_size in test_sizes:
        if bar_size in client.test_results:
            result = client.test_results[bar_size]
            logger.info(f"  {bar_size}: {'SUCCESS' if result['received'] else 'FAILED'} ({result['bars']} bars)")
    
    client.disconnect_from_tws()

if __name__ == "__main__":
    main()