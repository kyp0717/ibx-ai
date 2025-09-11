"""
Technical indicators panel displaying 10s and 30s bars with EMA9, VWAP, and MACD
"""

from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.panel import Panel
from rich.layout import Layout
from typing import Dict, Any


class IndicatorsPanel:
    def __init__(self):
        pass
    
    def render(self, indicators_10s: Dict[str, Any] = None, 
               indicators_30s: Dict[str, Any] = None) -> Panel:
        """Render the technical indicators panel with 10s and 30s sub-panels"""
        
        # Create layout for two sub-panels
        layout = Layout()
        layout.split_row(
            Layout(name="10s", size=50),
            Layout(name="30s", size=50)
        )
        
        # Create 10-second bar panel
        layout["10s"].update(self._create_indicator_subpanel(
            indicators_10s or {}, 
            "10 Second Bar", 
            "cyan"
        ))
        
        # Create 30-second bar panel
        layout["30s"].update(self._create_indicator_subpanel(
            indicators_30s or {}, 
            "30 Second Bar", 
            "magenta"
        ))
        
        # Return layout without Panel wrapper (no border on main panel)
        return layout
    
    def _create_indicator_subpanel(self, indicators: Dict[str, Any], 
                                  title: str, color: str) -> Panel:
        """Create a sub-panel for indicators with aligned columns"""
        
        table = Table(show_header=False, box=None, padding=(0, 1), expand=True)
        table.add_column("Indicator", style="cyan", width=8)
        table.add_column("Value", style="white", width=10)
        table.add_column("Relative", style="white", width=14)
        table.add_column("Signal", style="white", width=8)
        
        if not indicators:
            table.add_row("", "No data", "", "")
            return Panel(table, title=title, title_align="center", 
                        border_style=color)
        
        current_price = indicators.get("current_price", 0)
        
        # Always show all three indicators (EMA9, VWAP, MACD)
        # EMA(9) Row
        ema9_value = indicators.get("ema9", None)
        if ema9_value is not None and current_price > 0:
            ema_value_text = f"${ema9_value:.2f}"
            # Calculate difference: Current Price - EMA
            # Round to avoid floating point precision issues
            price_vs_ema = round(current_price - ema9_value, 2)
            
            if price_vs_ema > 0.005:  # Use small threshold to avoid flickering
                # Price is above EMA - use green arrow for positive difference
                ema_relative = Text(f"▲ ${abs(price_vs_ema):.2f}", style="green")
                # Trading signal: price above EMA is bullish
                ema_signal = Text("BUY", style="green")
            elif price_vs_ema < -0.005:  # Use small threshold to avoid flickering
                # Price is below EMA - use red arrow for negative difference
                ema_relative = Text(f"▼ ${abs(price_vs_ema):.2f}", style="red")
                # Trading signal: price below EMA is bearish
                ema_signal = Text("SELL", style="red")
            else:
                ema_relative = Text("─ $0.00", style="yellow")
                ema_signal = Text("HOLD", style="yellow")
            
            table.add_row("EMA9", ema_value_text, ema_relative, ema_signal)
        else:
            # Show placeholder if no EMA data
            table.add_row("EMA9", "-", "-", "-")
        
        # VWAP Row
        vwap_value = indicators.get("vwap", None)
        if vwap_value is not None and current_price > 0:
            vwap_value_text = f"${vwap_value:.2f}"
            # Calculate difference: Current Price - VWAP
            # Round to avoid floating point precision issues
            price_vs_vwap = round(current_price - vwap_value, 2)
            
            if price_vs_vwap > 0.005:  # Use small threshold to avoid flickering
                # Price is above VWAP - use green arrow for positive difference
                vwap_relative = Text(f"▲ ${abs(price_vs_vwap):.2f}", style="green")
                # Trading signal: price above VWAP is bullish
                vwap_signal = Text("BUY", style="green")
            elif price_vs_vwap < -0.005:  # Use small threshold to avoid flickering
                # Price is below VWAP - use red arrow for negative difference
                vwap_relative = Text(f"▼ ${abs(price_vs_vwap):.2f}", style="red")
                # Trading signal: price below VWAP is bearish
                vwap_signal = Text("SELL", style="red")
            else:
                vwap_relative = Text("─ $0.00", style="yellow")
                vwap_signal = Text("HOLD", style="yellow")
            
            table.add_row("VWAP", vwap_value_text, vwap_relative, vwap_signal)
        else:
            # Show placeholder if no VWAP data
            table.add_row("VWAP", "-", "-", "-")
        
        # MACD Line Row
        macd_value = indicators.get("macd", None)
        macd_signal_line = indicators.get("macd_signal", None)
        
        if macd_value is not None:
            macd_value_text = f"{macd_value:.3f}"
            
            # For MACD line, show its position relative to zero
            if macd_value > 0.0005:
                macd_relative = Text(f"▲ {abs(macd_value):.3f}", style="green")
            elif macd_value < -0.0005:
                macd_relative = Text(f"▼ {abs(macd_value):.3f}", style="red")
            else:
                macd_relative = Text("─ 0.000", style="yellow")
            
            # Determine signal based on histogram (MACD vs Signal)
            if macd_signal_line is not None:
                macd_histogram = round(macd_value - macd_signal_line, 3)
                if macd_histogram > 0.0005:
                    macd_signal = Text("BUY", style="green")
                elif macd_histogram < -0.0005:
                    macd_signal = Text("SELL", style="red")
                else:
                    macd_signal = Text("HOLD", style="yellow")
            else:
                macd_signal = Text("-", style="white")
            
            table.add_row("MACD", macd_value_text, macd_relative, macd_signal)
        else:
            # Show placeholder if no MACD data
            table.add_row("MACD", "-", "-", "-")
        
        # MACD Signal Line Row
        if macd_signal_line is not None:
            signal_value_text = f"{macd_signal_line:.3f}"
            
            # For Signal line, show histogram (difference between MACD and Signal)
            if macd_value is not None:
                macd_histogram = round(macd_value - macd_signal_line, 3)
                if macd_histogram > 0.0005:
                    # MACD above signal line (bullish)
                    signal_relative = Text(f"▲ {abs(macd_histogram):.3f}", style="green")
                    signal_signal = Text("BUY", style="green")
                elif macd_histogram < -0.0005:
                    # MACD below signal line (bearish)
                    signal_relative = Text(f"▼ {abs(macd_histogram):.3f}", style="red")
                    signal_signal = Text("SELL", style="red")
                else:
                    signal_relative = Text("─ 0.000", style="yellow")
                    signal_signal = Text("HOLD", style="yellow")
            else:
                signal_relative = Text("-", style="white")
                signal_signal = Text("-", style="white")
            
            table.add_row("MACD Sig", signal_value_text, signal_relative, signal_signal)
        else:
            # Show placeholder if no Signal line data
            table.add_row("MACD Sig", "-", "-", "-")
        
        return Panel(
            table,
            title=title,
            title_align="center",
            border_style=color
        )