#!/usr/bin/env python
"""
Test script to verify header panel functionality
"""

from src.ui.panels.header_panel import HeaderPanel
from rich.console import Console

def test_header():
    console = Console()
    header = HeaderPanel()
    
    print("\nTest 1: Disconnected state")
    print("-" * 50)
    panel = header.render(connected=False, order_id=0, port=7497)
    console.print(panel)
    
    print("\nTest 2: Connected state on port 7497")
    print("-" * 50)
    panel = header.render(connected=True, order_id=12345, port=7497)
    console.print(panel)
    
    print("\nTest 3: Connected state on port 7500")
    print("-" * 50)
    panel = header.render(connected=True, order_id=99999, port=7500)
    console.print(panel)

if __name__ == "__main__":
    test_header()