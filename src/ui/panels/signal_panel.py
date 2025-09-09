"""
Signal panel for displaying trading signals based on technical indicators
"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from typing import Dict, Any


class SignalPanel:
    def __init__(self):
        pass
        
    def render(self, symbol: str = "", indicators: Dict[str, Any] = None) -> Panel:
        """Render the Signal panel with symbol and trading signal"""
        
        # Create main container
        container = Table(show_header=False, box=None, padding=0, expand=True)
        container.add_column(width=None)
        
        # First line: Stock symbol
        if symbol:
            symbol_text = Text(f"[ {symbol} ]", style="bold cyan")
        else:
            symbol_text = Text("[ - ]", style="dim white")
        container.add_row(Align.center(symbol_text))
        
        # Second line: Trading signal based on indicators
        signal_text = Text()
        
        if indicators:
            current_price = indicators.get("current_price", 0)
            ema9_value = indicators.get("ema9", 0)
            vwap_value = indicators.get("vwap", 0)
            macd_value = indicators.get("macd", 0)
            macd_signal_line = indicators.get("macd_signal", 0)
            
            # Determine signal based on multiple indicators
            bullish_signals = 0
            bearish_signals = 0
            
            # EMA9 signal
            if current_price > 0 and ema9_value > 0:
                if current_price > ema9_value:
                    bullish_signals += 1
                elif current_price < ema9_value:
                    bearish_signals += 1
            
            # VWAP signal
            if current_price > 0 and vwap_value > 0:
                if current_price > vwap_value:
                    bullish_signals += 1
                elif current_price < vwap_value:
                    bearish_signals += 1
            
            # MACD signal
            if macd_value != 0 and macd_signal_line != 0:
                if macd_value > macd_signal_line:
                    bullish_signals += 1
                elif macd_value < macd_signal_line:
                    bearish_signals += 1
            
            # Determine overall signal
            if bullish_signals > bearish_signals:
                signal_text.append("** Signal: Buy **", style="bold green")
            elif bearish_signals > bullish_signals:
                signal_text.append("** Signal: Sell **", style="bold red")
            else:
                signal_text.append("** Signal: Hold **", style="bold yellow")
        else:
            signal_text.append("** Signal: - **", style="dim white")
        
        container.add_row(Align.center(signal_text))
        
        return Panel(
            container,
            title="SIGNAL",
            title_align="center",
            border_style="cyan",
            style="on black",
            padding=(0, 1)
        )