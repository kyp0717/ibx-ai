# Phase 03: Terminal UI Enhancement

## Overview
Multi-panel terminal user interface using Rich framework for professional trading display with real-time updates and interactive controls.

## Features Enhancement

### 1. Port Number Argument
**Purpose**: Port number must be specified as argument on command line
**Items**:
- When starting the app, the port number must be specified with the flag `--port`
- It must be the first argument specified.

### 2. Header with Integrated Status Bar
**Purpose**: Display application title and critical connection information
**Items**:
- Application title (IBX Trading)
- Display TWS connection port number
- Display Connection status indicator
- Display format : ● Active on port xxxx or ● Disconnected
- Color-coded connection status (green=connected, red=disconnected)
- Current order ID counter
- System time (HH:MM:SS format)
  
### 3. Log Panel
**Purpose**: Display logging information to prevent flickering in the UI
**Items**:
- Display the log message 
- Layout should be side-by-side next to the system message panel.