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
        if ema9_value is not None:
            ema_value_text = f"${ema9_value:.2f}"
            # Calculate difference: EMA vs Price (not Price vs EMA)
            ema_vs_price = ema9_value - current_price
            
            if ema_vs_price > 0:
                # EMA is above price - use green arrow per requirement
                ema_relative = Text(f"▲ ${abs(ema_vs_price):.2f}", style="green")
                # But for trading signal: price below EMA is bearish
                ema_signal = Text("SELL", style="red")
            elif ema_vs_price < 0:
                # EMA is below price - use red arrow per requirement
                ema_relative = Text(f"▼ ${abs(ema_vs_price):.2f}", style="red")
                # But for trading signal: price above EMA is bullish
                ema_signal = Text("BUY", style="green")
            else:
                ema_relative = Text("─ $0.00", style="yellow")
                ema_signal = Text("HOLD", style="yellow")
            
            table.add_row("EMA9", ema_value_text, ema_relative, ema_signal)
        else:
            # Show placeholder if no EMA data
            table.add_row("EMA9", "-", "-", "-")
        
        # VWAP Row
        vwap_value = indicators.get("vwap", None)
        if vwap_value is not None:
            vwap_value_text = f"${vwap_value:.2f}"
            # Calculate difference: VWAP vs Price (not Price vs VWAP)
            vwap_vs_price = vwap_value - current_price
            
            if vwap_vs_price > 0:
                # VWAP is above price - use green arrow per requirement
                vwap_relative = Text(f"▲ ${abs(vwap_vs_price):.2f}", style="green")
                # But for trading signal: price below VWAP is bearish
                vwap_signal = Text("SELL", style="red")
            elif vwap_vs_price < 0:
                # VWAP is below price - use red arrow per requirement
                vwap_relative = Text(f"▼ ${abs(vwap_vs_price):.2f}", style="red")
                # But for trading signal: price above VWAP is bullish
                vwap_signal = Text("BUY", style="green")
            else:
                vwap_relative = Text("─ $0.00", style="yellow")
                vwap_signal = Text("HOLD", style="yellow")
            
            table.add_row("VWAP", vwap_value_text, vwap_relative, vwap_signal)
        else:
            # Show placeholder if no VWAP data
            table.add_row("VWAP", "-", "-", "-")
        
        # MACD Row
        macd_value = indicators.get("macd", None)
        macd_signal_line = indicators.get("macd_signal", None)
        
        if macd_value is not None and macd_signal_line is not None:
            macd_histogram = macd_value - macd_signal_line
            macd_value_text = f"{macd_value:.3f}"
            
            if macd_histogram > 0:
                # MACD above signal line (bullish) - use green arrow
                macd_relative = Text(f"▲ {abs(macd_histogram):.3f}", style="green")
                macd_signal = Text("BUY", style="green")
            elif macd_histogram < 0:
                # MACD below signal line (bearish) - use red arrow
                macd_relative = Text(f"▼ {abs(macd_histogram):.3f}", style="red")
                macd_signal = Text("SELL", style="red")
            else:
                macd_relative = Text("─ 0.000", style="yellow")
                macd_signal = Text("HOLD", style="yellow")
            
            table.add_row("MACD", macd_value_text, macd_relative, macd_signal)
        else:
            # Show placeholder if no MACD data
            table.add_row("MACD", "-", "-", "-")
        
        return Panel(
            table,
            title=title,
            title_align="center",
            border_style=color
        )