# Project Plan

## AI Directive
1. Create comprehensive project plan (if not already exisit)
2. If project plan already exist, modify and update as work progress.
3. Modify and update tasks.md as needed as project progress.
4. Use tws-test-agent when testing.
5. Do not build project structure unless it is explicitly directed in this project plan.
6. Bash scripts should be saved to `scripts` folder.
7. Documentation should be saved to `docs` folder.

## Project Type and Structure
- This is a **standalone application**, NOT a distributable library
- Use a flat module structure directly in src/ folder
- Do NOT create nested package folders (no src/ibxpy_ai/)
- Main entry point should be src/main.py
- Import pattern: modules are imported directly from src/

## Goal
- Build a python app to trade stock using interactive broker trader workstation.
- Use the python package ibapi which is published by interactive broker. 
- Do not use third party package such as ib_async, ib_insync or ibridepy.

## Feature 1 - Documenting Requirements  
- Create a file call requirements.md.
- In the requirements, explain what are the technical requirements that are
needed for development of trading app.
- In another section, list the python packages that are needed and why this is
required.
- Please feel free to add additional sections to explain anything else.


## Feature 2 - Setup Virtual Environment
- Build python virtual environment using uv.
- Install required packages in virtual environments
- If there are changes to the pyproject.toml file, review and install or remove
  unnecessary packages.

## Feature 3 - IBKR native python package ibapi installation
- The ibapi python package is not part of the pypi library.
- This package can be found in `~/Downloads/twsapi/`.
- Install ibapi in the virtual environment
- Follow the instruction provided in the file ibapi_install_guide.md.  Update
this file as needed.

## Feature 4 - IBKR IBGateway Installation
- Item 1: Install IBGateway
- Test: Check whether IBGateway has been installed

## Feature 5 - Established connection to TWS (Trader Workstation)
### Item 1: Connection to TWS
- Implement the connection to TWS on port 7500 on localhost.
### Test 1: Connection to TWS
- Build the test to check connection is successful. 
- Run the test in a virtual environment us uv. 

## Feature 6 - Get Stock quote
### Item 1: Get the current stock quote
- Implement the code that can retrieve the latest real-time stock quote
### Item 2: Integrate Item 1 into main app
- Reimplement main.py to incorporate connection to the app and retrieve the
latest stock quote
### Test 1: Retrieve the current price for AAPL stock
- Build the test for the module
### Test 2: Integration test
- Build the integration test 
- Do not use mock data
- Connect to the TWS as a client and retrieve the stock quore
- Run the main.py for this test

## Feature 7 - Place Stock Order
### Item 1: Refactor
- Give users only 2 options "Begin Trading" and "Exit" at startup.
### Item 2: Prompt User and Place Order
- Implement the code that ask user to buy the stock at latest current stock
price.
- Prompt the user within "Begin Trading" after the user have enter
  name of the stock to track.
- Display this prompt while in quote monitor: 
  - ` **stock** >>> Open Trade at <current price> (press enter) ?`
- If user did not press enter after 1 second, retrieve the latest current price and refresh the screen.
  - Redisplay the prompt with new price.
-  If user press enter, place the limit order for the stock at the current price.
  - Check the current order status.  Relay that information back to the console.
  - Continue to monitor order status until order has been completely filled.
  - If order is partially filled, continue to monitor the progress and inform
  the user through the console
  - Display order status with one of the following format in the console:
        - \*\*Stock\*\* \[TWS Open Order Status\] Filled at <price> 
        - Do not continuously update the timestamp.  Display the datetime when
        the order status has reached filled status.
        - \*\*Stock\*\* \[TWS Open Order Status\] Partialed Filled 
        - \*\*Stock\*\* \[TWS Open Order Status\] <status>
  - Once the order is filled, continuously displayed this order status throughout
    the life of the trading app.  
- Do not prompt me to press enter so that that I can continue to monitor the position. 
- Automatically transition into pnl monitor mode.

### Item 3: Integrate Item 1 into main app
- Reimplement main.py to incorporate user prompt inside quote monitor and place
  order if user press enter to open the stock position at 100 shares.
### Test 2: Prompt and order placement
- Build the test and place the order
### Test 3: Integration testing
- Integrate Item 2 into main.py

## Feature 8 - Monitor Filled Order and Close Position
### Item 1: Track the PnL for the current asset (i.e. stock)
- Display the PnL for asset as another line item on the console.
- Display with this format
    - If pnl is negative for the asset, display in red 
      -  \*\*Stock\*\* \[TWS PnL] $<pnl value for asset> --- LOSS
      - Do not display negative sign in the pnl value.  Display only the amount.
    - If pnl is positive or zero display in green.
      -  \*\*Stock\*\* \[TWS PnL] $<pnl value for asset> --- GAIN
      - Do not display positive sign in the pnl value.  Display only the amount.
### Item 2: Prompt User to close the position
- Prompt the user with this format:
      -  `**Stock** >>> Close position at <current stock price> (press enter)?`
- If user does not press enter after 1 second:
  - Display the Pnl in the format specifiy in Item 1.
  - Display the prompt to close the position once again with the latest stock
  price.
- If user press enter, close the position by placing a sell order for the stock.
- When closing the position, place the limit sell order for the stock at the current price.
  - Check the current order status.  Relay that information back to the console.
  - Continue to monitor order status until order has been completely filled.
  - If order is partially filled, continue to monitor the progress and inform
  the user through the console
  - Display order status with one of the following format in the console:
        - \*\*Stock\*\* \[TWS Close Order Status\] Filled at <price> 
        - Do not continuously update the timestamp.  Display the datetime when
        the order status has reached filled status.
        - \*\*Stock\*\* \[TWS Close Order Status\] Partialed Filled 
        - \*\*Stock\*\* \[TWS Close Order Status\] <status>
  - Once the order is filled, continuously displayed this order status throughout
    the life of the trading app.  
### Test 1: PnL Tracking and Closing
- Build the test for Feature 8 - Item 1 and 2
### Test 2: Integrate testing
- Integrate Item into main.py

## Feature 9 - Audit
### Item 1: Verify that the position is closed
- Check that the current position for asset is 0.
- Implement reqPosition for asset.
### Item 2: Check the final PnL for the asset if the position is 0
- Check that the final pnl for the asset 
### Item 3: Determine the total cost for the trade
- Calculate both the cost to buy and sell.  
- Calculate the cost for the total trading lifecycle.
### Item 4: Display the total commission for the trading lifecycle
### Item 5: Display Audit
- Diplay the result of the audit:
        - \*\*Stock\*\* \[TWS Audit\] Final Position <number of shares>
        - \*\*Stock\*\* \[TWS Audit\] Commision Cost <amount>
        - \*\*Stock\*\* \[TWS Audit\] Final PnL <loss or gain>
        - \*\*Stock\*\* \[TWS Audit\] Final PnL - Commission <loss or gain>
### Test 1: test the audit
- Build the test for audit

## Feature 10 - Exit Trade for asset
### Item: Prompt User to Exit the trade 
      -  `**Stock** >>> Exit the trade (press enter)?`
### Test 1: test the exit for this asset
- Build the test for exit 

## Feature 11 - Refactor
### Item 1: Modified the app to take 2 arguments
- Remove the prompt "Enter symbol ...?".  Instead, inputs will come from
arguments in the command line.
- First argument is the symbol such as AAPL
- Second argument is the position (size) of the trade such as 100 quantity
- **REQUIRED**: Both arguments must be provided or the application will exit with an error
- If no symbol and position is provided, trigger an error and do not run the application
- Display clear usage instructions when arguments are missing
### Item 2: Modified first choice at the startup prompt
- Change choice 1:
  - `Begin trading <stock> with size <position>`
### Test 1: 
- Test the changes to the code made in Item 1 and 2.
- Test that application exits with error when arguments are missing
- Test that application runs correctly when both arguments are provided

## Feature 12 - Retrieve 1-Minute Bar Data
### Item 1: Stream or request minute bar
- Item 2: Using minute bar history for the current day, calculate
exponential moving average with 9 minute look back

