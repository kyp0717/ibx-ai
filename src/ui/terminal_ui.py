#!/usr/bin/env python
"""
Terminal UI orchestrator using Rich library for multi-panel display
"""

import asyncio
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from threading import Lock

from .panels.header_panel import HeaderPanel
from .panels.system_message_panel import SystemMessagePanel
from .panels.log_panel import LogPanel
from .panels.market_data_panel import MarketDataPanel
from .panels.position_orders_panel import PositionOrdersPanel
from .panels.indicators_panel import IndicatorsPanel
from .panels.trading_prompt import TradingPrompt


class TerminalUI:
    def __init__(self, client=None, port: int = 7497):
        self.console = Console()
        self.client = client
        self.port = port
        self.layout = Layout()
        self.data_lock = Lock()
        
        self.market_data = {}
        self.position_data = {}
        self.order_data = {}
        self.indicators_data = {}
        self.messages = []
        self.log_messages = []
        self.prompt_text = ""
        self.is_running = False
        
        self._setup_layout()
        self._init_panels()
    
    def _setup_layout(self):
        """Setup the main layout structure"""
        self.layout.split(
            Layout(name="header", size=4),
            Layout(name="top_panels", size=5),
            Layout(name="main", size=15),
            Layout(name="indicators", size=7),
            Layout(name="prompt", size=3)
        )
        
        # Split top panels into system messages and logs side by side
        self.layout["top_panels"].split_row(
            Layout(name="messages", ratio=1),
            Layout(name="logs", ratio=1)
        )
        
        self.layout["main"].split_row(
            Layout(name="market", ratio=1),
            Layout(name="position", ratio=1)
        )
    
    def _init_panels(self):
        """Initialize all panel instances"""
        self.header_panel = HeaderPanel()
        self.message_panel = SystemMessagePanel()
        self.log_panel = LogPanel()
        self.market_panel = MarketDataPanel()
        self.position_panel = PositionOrdersPanel()
        self.indicators_panel = IndicatorsPanel()
        self.trading_prompt = TradingPrompt()
    
    def update_market_data(self, symbol: str, data: Dict[str, Any]):
        """Update market data for display"""
        with self.data_lock:
            self.market_data = {
                "symbol": symbol,
                "last_price": data.get("last_price", 0),
                "bid_price": data.get("bid_price", 0),
                "bid_size": data.get("bid_size", 0),
                "ask_price": data.get("ask_price", 0),
                "ask_size": data.get("ask_size", 0),
                "volume": data.get("volume", 0),
                "high": data.get("high", 0),
                "low": data.get("low", 0),
                "open": data.get("open", 0),
                "close": data.get("close", 0),
                "change": data.get("change", 0),
                "change_pct": data.get("change_pct", 0)
            }
    
    def update_position_data(self, data: Dict[str, Any]):
        """Update position and order data"""
        with self.data_lock:
            self.position_data = data
    
    def update_order_status(self, order_id: int, status: str, filled_qty: int, 
                           total_qty: int, avg_price: float):
        """Update order status information"""
        with self.data_lock:
            self.order_data = {
                "order_id": order_id,
                "status": status,
                "filled_qty": filled_qty,
                "total_qty": total_qty,
                "avg_price": avg_price
            }
    
    def update_indicators(self, indicators: Dict[str, Any]):
        """Update technical indicators"""
        with self.data_lock:
            self.indicators_data = indicators
    
    def add_system_message(self, message: str, msg_type: str = "info"):
        """Add a system message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self.data_lock:
            self.messages.append({
                "time": timestamp,
                "message": message,
                "type": msg_type
            })
            if len(self.messages) > 50:
                self.messages = self.messages[-50:]
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """Add a log message to the log panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with self.data_lock:
            self.log_messages.append({
                "time": timestamp,
                "message": message,
                "level": level
            })
            if len(self.log_messages) > 50:
                self.log_messages = self.log_messages[-50:]
    
    def update_prompt(self, prompt_text: str):
        """Update the trading prompt text"""
        with self.data_lock:
            self.prompt_text = prompt_text
    
    def render(self) -> Layout:
        """Render the complete UI layout"""
        with self.data_lock:
            self.layout["header"].update(
                self.header_panel.render(
                    connected=self.client.is_connected() if self.client else False,
                    order_id=self.client.next_order_id if (self.client and self.client.next_order_id) else 0,
                    port=self.port
                )
            )
            
            self.layout["messages"].update(
                self.message_panel.render(self.messages)
            )
            
            self.layout["logs"].update(
                self.log_panel.render(self.log_messages)
            )
            
            self.layout["market"].update(
                self.market_panel.render(self.market_data)
            )
            
            self.layout["position"].update(
                self.position_panel.render(
                    self.position_data,
                    self.order_data
                )
            )
            
            self.layout["indicators"].update(
                self.indicators_panel.render(self.indicators_data)
            )
            
            self.layout["prompt"].update(
                self.trading_prompt.render(
                    self.prompt_text or "Waiting for market data...",
                    self.market_data.get("symbol", ""),
                    self.market_data.get("ask_price", 0)
                )
            )
        
        return self.layout
    
    async def run_async(self):
        """Run the UI with async updates"""
        self.is_running = True
        with Live(self.render(), console=self.console, refresh_per_second=2) as live:
            while self.is_running:
                live.update(self.render())
                await asyncio.sleep(0.5)
    
    def run(self):
        """Run the UI in blocking mode"""
        self.is_running = True
        try:
            with Live(self.render(), console=self.console, refresh_per_second=2) as live:
                while self.is_running:
                    live.update(self.render())
                    import time
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the UI"""
        self.is_running = False