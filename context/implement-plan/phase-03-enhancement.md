# Phase 03: Terminal UI Enhancement

## Overview
Multi-panel terminal user interface using Rich framework for professional trading display with real-time updates and interactive controls.

## Key Implementation Concepts
### Message Types
1. **System Messages (TWS Messages)**: Trading-related messages from TWS (connections, orders, fills)
   - Added via: `terminal_ui.add_system_message(message, type)`
   - Stored in: `terminal_ui.messages` list
   - Displayed in: TWS Message Panel (nested in header panel, top-right)
   - Examples: "Connected to TWS", "Order filled", "Position closed"

2. **Log Messages**: General application logging (debug, info, warnings, errors)
   - Added via: `terminal_ui.add_log_message(message, level)`
   - Stored in: `terminal_ui.log_messages` list
   - Displayed in: Log Panel (bottom of terminal)
   - Examples: Debug traces, application errors, general info

### Layout Structure (top to bottom)
1. Header Panel (size: 8) - Contains TWS Message Panel on right side
2. Indicators Panel (size: 10)
3. Middle Panels (size: 8) - Quote Panel (left) and PnL Panel (right)
4. Action Panel (size: 12)
5. Log Panel (size: 12) - At the very bottom

## Features Enhancement

### 1. Port Number Argument
**Purpose**: Port number must be specified as argument on command line
**Items**:
- When starting the app, the port number must be specified with the flag `--port`
- It must be the first argument specified.

### 2. Header with Integrated Status Bar
**Purpose**: Display application title and critical connection information
**Items**:
- Line 1: No content (blank space)
- Line 2: Application title (IBX Trading)
- Line 3: Display TWS connection port number
  - Display Connection status indicator
  - Display format : ● Active on port xxxx or ● Disconnected
  - Color-coded connection status (green=connected, red=disconnected)
- Line 4: Display 2 items side by side separated by `|`
  - Current order ID counter
  - System time (HH:MM:SS format)
  
### 3. TWS Message Panel (nested inside header panel)
**Purpose**: Display TWS system messages
**Implementation Notes**:
- TWS messages are added via the `add_system_message()` method in terminal_ui.py
- These are system messages related to TWS operations (connections, orders, fills, etc.)
- The messages are stored in the `self.messages` list in terminal_ui.py
**Items**:
- Display the system messages (TWS messages)
- Insert 1 space between timestamp and message
- Fix the message panel at 60 columns
- TWS Message panel should be justified right within the header panel
- Display only the time and message (no log level or type)
- Display the latest 4 messages only
- Messages are passed from terminal_ui.py to header_panel.py via the render method
- Format: "HH:MM:SS message_content" with single space separator

### 4. Buy and Sell after manual cancellation
**Purpose**: Allow order placement to work after manual order cancelation in TWS


### 6. Action  Panel Redesign
**Purpose**: Let user know that the app is awaiting user respond
**Items**:
- Move Action panel below the Quote and PnL Panel (above the Log Panel)
- Yellow border.
- Name the panel ACTION
- Content should be justified left
- All content inside this action panel
- Prompt format:
  - First line: 
    - Item 1: [ <current time with format HH:MM:SS> ]
    - Item 2: [ <stock symbol> ]
    - Item 3:
      - ** Signal: Buy **  (green)
      - or ** Signal: Sell ** (red)
      - or ** Signal: Hold ** (yellow)
  - Second line: 
    - Buy <stock> at <current stock quote> (press enter) ?
    - Sell <stock> at <current stock quote> (press enter) ?
- Move the Position and Order Panel to inside the Action panel.
  - Change the Position and Order Panel to Order
  - Move Order panel to the top.
  - Remove the column headers
  - Create a vertical line to separate position and order section inside the Order pane.
  - Remove the border on the Order Panel
  

### 7. Indicator Panel
**Purpose**: Create indicator panel to display 10 seconds and 30 seconds bar indicators 
**Items**:
- Create 2 sub panels inside the indicator panels.
- Remove the border in the main panel.
- Sub panel 1:  10 Second Bar
  - Display EMA9, VWAP and MACD and update values every 10 seconds
  - The values remain static between bar updates
  - They only change every 10 seconds (for the 10s panel) or 30 seconds (for the 30s panel)
  - This would require tracking when the last bar was received and only updating then
  - Show the signal
  - When indicator is above stock price, use green arrow next to price difference
  - When indicator is below stock price, use red arrow next to price difference
- Sub panel 2:  10 Second Bar
  - Display EMA9, VWAP and MACD and update values every 30 seconds
  - The values remain static between bar updates
  - They only change every 10 seconds (for the 10s panel) or 30 seconds (for the 30s panel)
  - This would require tracking when the last bar was received and only updating then
  - Show the signal
  - When indicator is above stock price, use green arrow next to price difference
  - When indicator is below stock price, use red arrow next to price difference
- Within each sub panel, align the columns of all three indicators
  - First column in the name of the indicator
  - Second column is value of the indicator
  - Third column indicator relative to price
  - Fourth column should be signal 
- In the 10-Second Bar and 30-Second Bar panel, when updating the value, keep all three indicators visible.
  - Do not display only the indicator that are currently changing.  
  - Show all three indicators at all time and update the only the indicator that have changed.
  - 
### 8. Quote Panel
**Purpose**: Create the quote panel
**Items**:
- Create Quote Panel to the left of the PnL Panel (side by side)
- Width should be 50 columns.
- Only display quotes (do not display OHLC)
- Yellow border

### 9. Create a panel call PnL
**Purpose**: PnL panel 
**Items**:
- Create PnL panel.  This panel should reside next to the quote panel (side by side)
- Fixed teh width of the panel at 50 columns.
- Remove the blank line at the top.
- Yellow border
- Place PnL panel to the left of the Quote Panel(side by side).
- PnL values should be lived updated.
- Show the PnL values even when at $0 when there are no position.
- If trade has opened, the position should show the size (quantity) of stock, not the price.
  - Do not show the word 'share' in the size.
- Show the cost basis.  This is the amount it cost to enter the position.
- Show the unrealized pnl in dollars.
  - Name the metric 'Unrealized'  
  - Update the unrealized pnl as stock price changes.
- Remove 'Unreal Gain' metric (it was the same as 'Unrealized')
- Show commission. Derived the commsion from TWS if possible.  Do not calculate manually.
  
### 10. Fixed the width of the console app to 100 columns

### 11. Log Panel 
**Purpose**: Display logging information 
**Implementation Notes**:
- Log messages are added via the `add_log_message()` method in terminal_ui.py
- These are general application log messages (debug, info, warning, error)
- The messages are stored in the `self.log_messages` list in terminal_ui.py
- Separate from TWS system messages which appear in the header panel
**Items**:
- Display the log messages 
- Insert 1 space between timestamp and message
- The Log Panel should appear at the bottom of the terminal
- Remove the log type/level after the timestamp
- Display only the time and message
- Display the latest 10 messages only
- Panel height: 12 rows
- Border style: cyan
- Format: "HH:MM:SS message_content" with single space separator
