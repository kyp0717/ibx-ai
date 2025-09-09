#!/usr/bin/env python
"""
Debug script to test indicator data flow
"""

import sys
import time
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_indicators():
    """Test the technical indicators data flow"""
    
    try:
        from technical_indicators import TechnicalAnalysisClient
        
        logger.info("=" * 60)
        logger.info("Starting Technical Indicators Debug Test")
        logger.info("=" * 60)
        
        # Create client
        client = TechnicalAnalysisClient()
        
        # Add debug logging to track data flow
        original_historicalData = client.historicalData
        def debug_historicalData(reqId, bar):
            logger.debug(f"[historicalData] reqId={reqId}, bar.date={bar.date}, close={bar.close}")
            return original_historicalData(reqId, bar)
        client.historicalData = debug_historicalData
        
        original_historicalDataEnd = client.historicalDataEnd
        def debug_historicalDataEnd(reqId, start, end):
            logger.info(f"[historicalDataEnd] reqId={reqId}, start={start}, end={end}")
            result = original_historicalDataEnd(reqId, start, end)
            
            # Log the current state after historical data ends
            logger.info(f"After historicalDataEnd:")
            logger.info(f"  - bars_10sec count: {len(client.bars_10sec)}")
            logger.info(f"  - bars_30sec count: {len(client.bars_30sec)}")
            logger.info(f"  - indicators_10sec: {client.indicators_10sec}")
            logger.info(f"  - indicators_30sec: {client.indicators_30sec}")
            logger.info(f"  - ema9_10sec: {client.ema9_10sec}")
            logger.info(f"  - ema9_30sec: {client.ema9_30sec}")
            
            return result
        client.historicalDataEnd = debug_historicalDataEnd
        
        original_historicalDataUpdate = client.historicalDataUpdate
        def debug_historicalDataUpdate(reqId, bar):
            logger.info(f"[historicalDataUpdate] NEW REALTIME BAR - reqId={reqId}, bar.date={bar.date}, close={bar.close}")
            return original_historicalDataUpdate(reqId, bar)
        client.historicalDataUpdate = debug_historicalDataUpdate
        
        # Connect
        logger.info("Connecting to TWS on port 7497...")
        if not client.connect_to_tws(host="127.0.0.1", port=7497, client_id=99):
            logger.error("Failed to connect to TWS")
            return False
        
        logger.info("Connected successfully!")
        time.sleep(1)
        
        # Start technical analysis
        symbol = "AAPL"
        logger.info(f"Starting technical analysis for {symbol}...")
        
        if not client.start_technical_analysis(symbol):
            logger.error("Failed to start technical analysis")
            return False
        
        logger.info("Technical analysis started, waiting for data...")
        
        # Monitor for 30 seconds
        start_time = time.time()
        last_log_time = start_time
        
        while time.time() - start_time < 30:
            current_time = time.time()
            
            # Log status every 5 seconds
            if current_time - last_log_time >= 5:
                logger.info("-" * 40)
                logger.info(f"Status after {int(current_time - start_time)} seconds:")
                logger.info(f"  10-sec bars: {len(client.bars_10sec)}")
                logger.info(f"  30-sec bars: {len(client.bars_30sec)}")
                
                if client.indicators_10sec:
                    logger.info(f"  10-sec indicators:")
                    logger.info(f"    - EMA9: {client.indicators_10sec.ema9}")
                    logger.info(f"    - VWAP: {client.indicators_10sec.vwap}")
                    logger.info(f"    - MACD: {client.indicators_10sec.macd}")
                else:
                    logger.info(f"  10-sec indicators: None")
                    
                if client.indicators_30sec:
                    logger.info(f"  30-sec indicators:")
                    logger.info(f"    - EMA9: {client.indicators_30sec.ema9}")
                    logger.info(f"    - VWAP: {client.indicators_30sec.vwap}")
                    logger.info(f"    - MACD: {client.indicators_30sec.macd}")
                else:
                    logger.info(f"  30-sec indicators: None")
                    
                last_log_time = current_time
            
            time.sleep(0.5)
        
        # Final summary
        logger.info("=" * 60)
        logger.info("FINAL SUMMARY:")
        logger.info(f"  Total 10-sec bars received: {len(client.bars_10sec)}")
        logger.info(f"  Total 30-sec bars received: {len(client.bars_30sec)}")
        logger.info(f"  10-sec indicators present: {client.indicators_10sec is not None}")
        logger.info(f"  30-sec indicators present: {client.indicators_30sec is not None}")
        
        if client.bars_10sec:
            logger.info(f"  First 10-sec bar: {client.bars_10sec[0].timestamp}")
            logger.info(f"  Last 10-sec bar: {client.bars_10sec[-1].timestamp}")
            
        if client.bars_30sec:
            logger.info(f"  First 30-sec bar: {client.bars_30sec[0].timestamp}")
            logger.info(f"  Last 30-sec bar: {client.bars_30sec[-1].timestamp}")
        
        logger.info("=" * 60)
        
        # Disconnect
        client.disconnect_from_tws()
        
        return True
        
    except Exception as e:
        logger.error(f"Error in test: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_indicators()
    sys.exit(0 if success else 1)