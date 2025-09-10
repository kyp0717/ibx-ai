"""
Technical Indicators Module - Phase 02
Handles calculation of EMA, VWAP, MACD and signal generation
"""

import logging
import threading
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import numpy as np

try:
    from ibapi.contract import Contract
    from ibapi.common import BarData
except ImportError:
    raise ImportError(
        "ibapi package not found. Please install it using the install_ibapi.sh script"
    )

from connection import TWSConnection

logger = logging.getLogger(__name__)


@dataclass
class BarDataPoint:
    """Single bar data point with OHLCV"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    typical_price: float = field(init=False)
    
    def __post_init__(self):
        self.typical_price = (self.high + self.low + self.close) / 3


@dataclass
class TechnicalIndicators:
    """Container for all technical indicator values"""
    timestamp: datetime
    ema9: Optional[float] = None
    vwap: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    signal_strength: Optional[float] = None
    signal_direction: Optional[str] = None  # 'BUY', 'SELL', 'NEUTRAL'


class TechnicalAnalysisClient(TWSConnection):
    """Client for technical analysis with different timeframes"""
    
    def __init__(self):
        super().__init__()
        self._next_request_id = 1000
        
        # Bar data storage for different timeframes
        self.bars_10sec: deque = deque(maxlen=500)
        self.bars_30sec: deque = deque(maxlen=500)
        
        # Indicator values and timestamps
        self.indicators_10sec: Optional[TechnicalIndicators] = None
        self.indicators_30sec: Optional[TechnicalIndicators] = None
        self.last_10sec_update: Optional[datetime] = None
        self.last_30sec_update: Optional[datetime] = None
        
        # EMA tracking
        self.ema9_10sec: Optional[float] = None
        self.ema9_30sec: Optional[float] = None
        self.ema12_10sec: Optional[float] = None
        self.ema26_10sec: Optional[float] = None
        self.ema12_30sec: Optional[float] = None
        self.ema26_30sec: Optional[float] = None
        
        # MACD signal line EMAs
        self.macd_signal_10sec: Optional[float] = None
        self.macd_signal_30sec: Optional[float] = None
        
        # Request tracking
        self.active_requests: Dict[int, Dict] = {}
        self._data_ready = threading.Event()
        
        # Track if we're loading initial historical data
        self.loading_historical_10sec = False
        self.loading_historical_30sec = False
        
    def get_next_request_id(self) -> int:
        """Get next unique request ID"""
        req_id = self._next_request_id
        self._next_request_id += 1
        return req_id
        
    def historicalData(self, reqId: int, bar: BarData):
        """Handle historical bar data - only update indicators when new bar received"""
        if reqId not in self.active_requests:
            logger.warning(f"Received bar for unknown request ID: {reqId}")
            return
            
        request_info = self.active_requests[reqId]
        bar_size = request_info['bar_size']
        
        # Parse timestamp - handle timezone if present
        date_str = bar.date
        # Remove timezone suffix if present (e.g., " America/New_York")
        if " America/" in date_str or " US/" in date_str:
            date_str = date_str.split(" America/")[0] if " America/" in date_str else date_str.split(" US/")[0]
        
        if ":" in date_str:
            bar_time = datetime.strptime(date_str, "%Y%m%d %H:%M:%S")
        else:
            bar_time = datetime.strptime(date_str, "%Y%m%d")
            
        bar_data = BarDataPoint(
            timestamp=bar_time,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=int(bar.volume)  # Convert Decimal to int
        )
        
        # Store bar based on timeframe
        if bar_size == "10 secs":
            # Check if this is a new bar (not a duplicate)
            if not self.bars_10sec or bar_data.timestamp > self.bars_10sec[-1].timestamp:
                self.bars_10sec.append(bar_data)
                # Log first few bars during loading
                if len(self.bars_10sec) <= 3:
                    logger.info(f"10-sec bar #{len(self.bars_10sec)}: {bar_time} C:{bar.close:.2f}")
                # Only calculate indicators if not loading historical data
                if not self.loading_historical_10sec:
                    self._update_indicators_10sec(bar_data)
                    logger.info(f"New 10-sec bar received at {bar_time}, recalculating indicators")
        elif bar_size == "30 secs":
            # Check if this is a new bar (not a duplicate)
            if not self.bars_30sec or bar_data.timestamp > self.bars_30sec[-1].timestamp:
                self.bars_30sec.append(bar_data)
                # Log first few bars during loading
                if len(self.bars_30sec) <= 3:
                    logger.info(f"30-sec bar #{len(self.bars_30sec)}: {bar_time} C:{bar.close:.2f}")
                # Only calculate indicators if not loading historical data
                if not self.loading_historical_30sec:
                    self._update_indicators_30sec(bar_data)
                    logger.info(f"New 30-sec bar received at {bar_time}, recalculating indicators")
            
        logger.debug(f"{bar_size} Bar: {bar_time} C:{bar.close:.2f} V:{bar.volume}")
        
    def historicalDataUpdate(self, reqId: int, bar: BarData):
        """Handle real-time bar updates when keepUpToDate=True - this is called for new bars"""
        # This method is called when a new bar is complete
        logger.debug(f"Real-time bar update received for request {reqId}")
        self.historicalData(reqId, bar)
        
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        """Handle end of historical data"""
        if reqId in self.active_requests:
            request_info = self.active_requests[reqId]
            bar_size = request_info['bar_size']
            
            if bar_size == "10 secs":
                logger.info(f"10-second bars initialized: {len(self.bars_10sec)} bars")
                self.loading_historical_10sec = False
                # Calculate indicators from all historical bars
                if self.bars_10sec and len(self.bars_10sec) > 0:
                    # Process all bars EXCEPT the last one to build up EMA values
                    bars_list = list(self.bars_10sec)
                    for i, bar in enumerate(bars_list[:-1]):
                        self.ema9_10sec = self._calculate_ema(bar.close, self.ema9_10sec, 9)
                        self.ema12_10sec = self._calculate_ema(bar.close, self.ema12_10sec, 12)
                        self.ema26_10sec = self._calculate_ema(bar.close, self.ema26_10sec, 26)
                    # Now calculate final indicators with the last bar (this will also update EMAs)
                    self._update_indicators_10sec(bars_list[-1])
                    ema9_value = self.ema9_10sec if self.ema9_10sec else 0
                    logger.info(f"10-second indicators initialized: EMA9={ema9_value:.2f}")
                else:
                    logger.warning(f"No 10-second bars received for initialization")
            elif bar_size == "30 secs":
                logger.info(f"30-second bars initialized: {len(self.bars_30sec)} bars")
                self.loading_historical_30sec = False
                # Calculate indicators from all historical bars
                if self.bars_30sec and len(self.bars_30sec) > 0:
                    # Process all bars EXCEPT the last one to build up EMA values
                    bars_list = list(self.bars_30sec)
                    for i, bar in enumerate(bars_list[:-1]):
                        self.ema9_30sec = self._calculate_ema(bar.close, self.ema9_30sec, 9)
                        self.ema12_30sec = self._calculate_ema(bar.close, self.ema12_30sec, 12)
                        self.ema26_30sec = self._calculate_ema(bar.close, self.ema26_30sec, 26)
                    # Now calculate final indicators with the last bar (this will also update EMAs)
                    self._update_indicators_30sec(bars_list[-1])
                    ema9_value = self.ema9_30sec if self.ema9_30sec else 0
                    logger.info(f"30-second indicators initialized: EMA9={ema9_value:.2f}")
                else:
                    logger.warning(f"No 30-second bars received for initialization")
                
            self._data_ready.set()
            
    def request_bar_data(self, symbol: str, bar_size: str, duration: str = "1800 S") -> bool:
        """Request historical bar data with specified bar size"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        
        req_id = self.get_next_request_id()
        
        # Store request info
        self.active_requests[req_id] = {
            'symbol': symbol,
            'bar_size': bar_size,
            'start_time': datetime.now()
        }
        
        # Mark as loading historical data
        if bar_size == "10 secs":
            self.loading_historical_10sec = True
        elif bar_size == "30 secs":
            self.loading_historical_30sec = True
        
        logger.info(f"Requesting {bar_size} bars for {symbol}")
        
        self.reqHistoricalData(
            reqId=req_id,
            contract=contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=0,
            formatDate=1,
            keepUpToDate=True,  # Keep updating with real-time data
            chartOptions=[]
        )
        
        return True
        
    def start_technical_analysis(self, symbol: str) -> bool:
        """Start technical analysis for both timeframes"""
        # Request 10-second bars
        if not self.request_bar_data(symbol, "10 secs", "1800 S"):
            return False
            
        # Request 30-second bars
        if not self.request_bar_data(symbol, "30 secs", "3600 S"):
            return False
            
        logger.info(f"Started technical analysis for {symbol}")
        return True
        
    def _calculate_ema(self, current_value: float, previous_ema: Optional[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if previous_ema is None:
            return current_value
        
        multiplier = 2 / (period + 1)
        return (current_value * multiplier) + (previous_ema * (1 - multiplier))
        
    def _calculate_vwap(self, bars: List[BarDataPoint]) -> float:
        """Calculate VWAP (Volume Weighted Average Price) from all bars"""
        if not bars:
            return 0
            
        # Calculate VWAP from all bars in the collection
        total_volume = 0
        total_pv = 0
        
        for bar in bars:
            # Convert volume to float to handle both int and Decimal types
            volume = float(bar.volume)
            total_volume += volume
            total_pv += bar.typical_price * volume
        
        if total_volume > 0:
            vwap = total_pv / total_volume
        else:
            vwap = bars[-1].typical_price if bars else 0
            
        return vwap
        
    def _calculate_macd(self, ema12: float, ema26: float, 
                       macd_signal: Optional[float]) -> Tuple[float, float, float]:
        """Calculate MACD, Signal Line, and Histogram"""
        macd = ema12 - ema26
        
        # Calculate signal line (9-period EMA of MACD)
        signal = self._calculate_ema(macd, macd_signal, 9)
        
        # Calculate histogram
        histogram = macd - signal
        
        return macd, signal, histogram
        
    def _update_indicators_10sec(self, bar: BarDataPoint):
        """Recalculate indicators for 10-second timeframe when new bar is received"""
        # Recalculate EMA9 with new bar
        self.ema9_10sec = self._calculate_ema(bar.close, self.ema9_10sec, 9)
        
        # Calculate EMA12 and EMA26 for MACD
        self.ema12_10sec = self._calculate_ema(bar.close, self.ema12_10sec, 12)
        self.ema26_10sec = self._calculate_ema(bar.close, self.ema26_10sec, 26)
        
        # Calculate VWAP from all bars
        vwap = self._calculate_vwap(list(self.bars_10sec))
        
        # Calculate MACD
        macd, signal, histogram = (0, 0, 0)
        if self.ema12_10sec and self.ema26_10sec:
            macd, signal, histogram = self._calculate_macd(
                self.ema12_10sec, 
                self.ema26_10sec, 
                self.macd_signal_10sec
            )
            self.macd_signal_10sec = signal
            
        # Calculate signal
        signal_strength, signal_direction = self._extrapolate_signal(
            bar.close, self.ema9_10sec, vwap, macd, histogram
        )
        
        # Update indicators and timestamp
        self.indicators_10sec = TechnicalIndicators(
            timestamp=bar.timestamp,
            ema9=self.ema9_10sec,
            vwap=vwap,
            macd=macd,
            macd_signal=signal,
            macd_histogram=histogram,
            signal_strength=signal_strength,
            signal_direction=signal_direction
        )
        self.last_10sec_update = bar.timestamp
        
        logger.info(f"10s Indicators Recalculated at {bar.timestamp.strftime('%H:%M:%S')} - "
                   f"EMA9: {self.ema9_10sec:.2f}, VWAP: {vwap:.2f}, "
                   f"MACD: {macd:.4f}, Signal: {signal_direction}")
        
    def _update_indicators_30sec(self, bar: BarDataPoint):
        """Recalculate indicators for 30-second timeframe when new bar is received"""
        # Recalculate EMA9 with new bar
        self.ema9_30sec = self._calculate_ema(bar.close, self.ema9_30sec, 9)
        
        # Calculate EMA12 and EMA26 for MACD
        self.ema12_30sec = self._calculate_ema(bar.close, self.ema12_30sec, 12)
        self.ema26_30sec = self._calculate_ema(bar.close, self.ema26_30sec, 26)
        
        # Calculate VWAP from all bars
        vwap = self._calculate_vwap(list(self.bars_30sec))
        
        # Calculate MACD
        macd, signal, histogram = (0, 0, 0)
        if self.ema12_30sec and self.ema26_30sec:
            macd, signal, histogram = self._calculate_macd(
                self.ema12_30sec, 
                self.ema26_30sec, 
                self.macd_signal_30sec
            )
            self.macd_signal_30sec = signal
            
        # Calculate signal
        signal_strength, signal_direction = self._extrapolate_signal(
            bar.close, self.ema9_30sec, vwap, macd, histogram
        )
        
        # Update indicators and timestamp
        self.indicators_30sec = TechnicalIndicators(
            timestamp=bar.timestamp,
            ema9=self.ema9_30sec,
            vwap=vwap,
            macd=macd,
            macd_signal=signal,
            macd_histogram=histogram,
            signal_strength=signal_strength,
            signal_direction=signal_direction
        )
        self.last_30sec_update = bar.timestamp
        
        logger.info(f"30s Indicators Recalculated at {bar.timestamp.strftime('%H:%M:%S')} - "
                   f"EMA9: {self.ema9_30sec:.2f}, VWAP: {vwap:.2f}, "
                   f"MACD: {macd:.4f}, Signal: {signal_direction}")
        
    def _extrapolate_signal(self, price: float, ema: float, vwap: float, 
                           macd: float, histogram: float) -> Tuple[float, str]:
        """
        Extrapolate trading signal from indicators
        Returns signal strength (0-100) and direction (BUY/SELL/NEUTRAL)
        """
        signals = []
        
        # EMA Signal: Price vs EMA
        if ema:
            ema_diff_pct = ((price - ema) / ema) * 100
            signals.append(ema_diff_pct)
            
        # VWAP Signal: Price vs VWAP
        if vwap and vwap > 0:
            vwap_diff_pct = ((price - vwap) / vwap) * 100
            signals.append(vwap_diff_pct)
            
        # MACD Signal: Histogram value
        if macd != 0:
            macd_signal_strength = histogram * 10  # Scale for visibility
            signals.append(macd_signal_strength)
            
        # Calculate average signal strength
        if signals:
            avg_signal = np.mean(signals)
            signal_strength = min(100, abs(avg_signal) * 10)  # Scale to 0-100
            
            # Determine direction
            if avg_signal > 0.5:
                signal_direction = "BUY"
            elif avg_signal < -0.5:
                signal_direction = "SELL"
            else:
                signal_direction = "NEUTRAL"
        else:
            signal_strength = 0
            signal_direction = "NEUTRAL"
            
        return signal_strength, signal_direction
        
    def get_relative_values(self, price: float, timeframe: str = "10sec") -> Dict[str, float]:
        """Get indicator values relative to current stock price"""
        indicators = self.indicators_10sec if timeframe == "10sec" else self.indicators_30sec
        
        if not indicators:
            return {}
            
        relative_values = {}
        
        if indicators.ema9:
            relative_values['ema9_diff'] = price - indicators.ema9
            relative_values['ema9_diff_pct'] = ((price - indicators.ema9) / indicators.ema9) * 100
            
        if indicators.vwap:
            relative_values['vwap_diff'] = price - indicators.vwap
            relative_values['vwap_diff_pct'] = ((price - indicators.vwap) / indicators.vwap) * 100
            
        if indicators.macd:
            relative_values['macd'] = indicators.macd
            relative_values['macd_histogram'] = indicators.macd_histogram
            
        return relative_values
        
    def get_combined_signal(self) -> Tuple[float, str]:
        """Get combined signal from both timeframes"""
        signals = []
        
        if self.indicators_10sec and self.indicators_10sec.signal_strength:
            signals.append((self.indicators_10sec.signal_strength, 
                          self.indicators_10sec.signal_direction))
            
        if self.indicators_30sec and self.indicators_30sec.signal_strength:
            signals.append((self.indicators_30sec.signal_strength, 
                          self.indicators_30sec.signal_direction))
            
        if not signals:
            return 0, "NEUTRAL"
            
        # Weight 10-second signal more heavily (60/40)
        if len(signals) == 2:
            strength = (signals[0][0] * 0.6) + (signals[1][0] * 0.4)
            
            # Determine direction based on weighted signals
            buy_score = 0
            sell_score = 0
            
            if signals[0][1] == "BUY":
                buy_score += 0.6
            elif signals[0][1] == "SELL":
                sell_score += 0.6
                
            if signals[1][1] == "BUY":
                buy_score += 0.4
            elif signals[1][1] == "SELL":
                sell_score += 0.4
                
            if buy_score > sell_score and buy_score > 0.5:
                direction = "BUY"
            elif sell_score > buy_score and sell_score > 0.5:
                direction = "SELL"
            else:
                direction = "NEUTRAL"
        else:
            strength = signals[0][0]
            direction = signals[0][1]
            
        return strength, direction
        
    def stop_analysis(self):
        """Stop all active data requests"""
        for req_id in list(self.active_requests.keys()):
            self.cancelHistoricalData(req_id)
            
        self.active_requests.clear()
        logger.info("Stopped technical analysis")