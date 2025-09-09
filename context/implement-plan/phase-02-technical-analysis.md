# Phase 02 - Technical Analysis

## Feature 01 - Retrieve 10-Second Minute Bar
- Using reqHistoricalData with keepUpToDate=True, get 10-Second bar
- Calculate EMA9, VWAP and MACD and update values every 10 seconds
- Recalculate these values when a new bar is received.
- Extrapolate the signal

## Feature 02 - Retrieve 30-Second Minute Bar
- Using reqHistoricalData with keepUpToDate=True, get 30-Second bar
- Calculate EMA9, VWAP and MACD and update values every 30 seconds
- Recalculate these values when a new bar is received.
- Extrapolate the signal

## Feature 03 - Handle Deque Slice Operations
**Purpose**: Properly handle deque data structures that don't support slice notation

**Problem When Not Handled Correctly**:
- **Application Crash**: TypeError exception ("sequence index must be integer, not 'slice'") in historicalDataEnd
- **EMA Initialization Failure**: Cannot process historical bars to build up EMA values
- **Indicator Calculation Blocked**: Without processing historical bars, initial indicators cannot be calculated
- **Missing Technical Analysis**: No EMA, VWAP, or MACD values available at startup

**Implementation Details**:
- Bars are stored in `deque` objects (bars_10sec, bars_30sec) with maxlen=500
- Deques don't support slice notation like `[:-1]` or `[1:5]`
- Must convert deque to list before using slice operations

**Items**:
- Convert deque to list: `bars_list = list(self.bars_10sec)`
- Then use slice operations: `bars_list[:-1]` for all except last, `bars_list[-1]` for last element
- Implementation location: `technical_indicators.py`, lines 171-177 and 187-193

**Critical Code Pattern**:
```python
# Wrong - causes TypeError
for bar in self.bars_10sec[:-1]:  # deque doesn't support slice

# Correct
bars_list = list(self.bars_10sec)
for bar in bars_list[:-1]:  # list supports slice
```

## Feature 04 - Handle Decimal Volume Type
**Purpose**: Properly handle Decimal type volumes returned by TWS API

**Problem When Not Handled Correctly**:
- **Application Crash**: TypeError exception ("unsupported operand type(s) for *: 'float' and 'decimal.Decimal'")
- **VWAP Calculation Failure**: Cannot multiply typical_price (float) with volume (Decimal)
- **Indicator Display Issues**: VWAP values cannot be calculated or displayed
- **Data Type Mismatch**: Incompatible types in mathematical operations

**Implementation Details**:
- TWS API returns bar.volume as `decimal.Decimal` type
- BarDataPoint expects volume as int type
- VWAP calculation needs consistent numeric types for multiplication

**Items**:
- Convert Decimal to int when creating BarDataPoint: `volume=int(bar.volume)`
- Convert volume to float in VWAP calculation: `volume = float(bar.volume)`
- Implementation location: `technical_indicators.py`, lines 124 and 274

**Type Conversion Strategy**:
1. At data ingestion (line 124): Convert Decimal → int for storage
2. At calculation time (line 274): Convert to float for mathematical operations
3. Maintains backward compatibility with integer volumes

## Feature 05 - Handle Timezone in Historical Data
**Purpose**: Properly parse datetime strings with timezone suffixes from TWS API

**Problem When Not Handled Correctly**:
- **Application Crash**: ValueError exception ("unconverted data remains: America/New_York") causes thread crash
- **Data Pipeline Failure**: Historical bar data cannot be processed or stored
- **No Indicators**: Without bar data, EMA9, VWAP, and MACD cannot be calculated
- **Empty UI Panels**: Indicators panel displays no values, preventing technical analysis
- **Trading Impact**: Cannot make informed trading decisions without technical indicators
- **User Experience**: Application appears broken with no visible indicators despite active connection

**Implementation Details**:
- TWS API returns bar timestamps with timezone suffixes (e.g., "20240109 14:30:00 America/New_York")
- The datetime parser in `historicalData()` method must strip timezone suffixes before parsing
- Supports both "America/" and "US/" timezone prefix formats

**Items**:
- Strip timezone suffix from bar.date before datetime parsing
- Handle formats: "YYYYMMDD HH:MM:SS America/Timezone" and "YYYYMMDD HH:MM:SS US/Timezone"
- Maintain support for non-timezone formats: "YYYYMMDD HH:MM:SS" and "YYYYMMDD"
- Implementation location: `technical_indicators.py`, lines 107-116

**Common Timezone Suffixes from TWS**:
- America/New_York (Eastern Time)
- America/Chicago (Central Time)
- America/Los_Angeles (Pacific Time)
- US/Eastern, US/Central, US/Pacific, US/Mountain

**Critical Data Flow**:
1. TWS sends historical data with timezone → 
2. historicalData() parses timestamp → 
3. Bar data stored in lists → 
4. Indicators calculated → 
5. UI panels updated
(Failure at step 2 cascades through entire pipeline)

