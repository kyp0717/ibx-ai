# Feature: Timezone Parsing Fix for Historical Data

## Date: 2025-01-09
## Component: Technical Indicators
## File: src/technical_indicators.py

### Issue Discovered
- TWS API returns historical bar timestamps with timezone suffixes
- Example: "20240109 14:30:00 America/New_York"
- Python datetime.strptime() cannot parse timezone suffix
- Results in ValueError: "unconverted data remains: America/New_York"

### Impact
- Application crashes when receiving historical data
- Technical indicators cannot be calculated
- Indicators panel displays no data
- Complete data pipeline failure

### Root Cause
- historicalData() method in technical_indicators.py attempted to parse timestamps without handling timezone suffixes
- Original parsing code only expected formats: "YYYYMMDD HH:MM:SS" or "YYYYMMDD"

### Solution Implemented
- Added timezone suffix detection and removal before parsing
- Handles both "America/" and "US/" timezone prefixes
- Maintains backward compatibility with non-timezone formats

### Data Flow Impact
When timezone parsing fails:
1. Historical data reception crashes with ValueError
2. Bar data never gets stored in bars_10sec/bars_30sec lists
3. Indicator calculations never execute
4. UI indicators panel remains empty
5. Trading decisions cannot use technical indicators

### Testing Completed
- Verified parsing of various timezone formats
- Tested backward compatibility with non-timezone formats
- Confirmed indicators now display correctly in UI
- All 9 test cases pass for datetime parsing scenarios