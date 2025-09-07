"""
Technical indicators panel displaying EMA9, VWAP, and MACD
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from typing import Dict, Any


class IndicatorsPanel:
    def __init__(self):
        pass
    
    def render(self, indicators: Dict[str, Any]) -> Panel:
        """Render the technical indicators panel"""
        
        table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
        table.add_column("Indicator", style="cyan", width=15)
        table.add_column("Value", style="white", width=20)
        table.add_column("Signal", style="white", width=25)
        table.add_column("Details", style="dim white")
        
        if not indicators:
            table.add_row("", "No indicator data available", "", "")
            return Panel(
                table,
                title="TECHNICAL INDICATORS",
                title_align="center",
                border_style="green",
                style="on black"
            )
        
        ema9_value = indicators.get("ema9", 0)
        ema9_signal = indicators.get("ema9_signal", "NEUTRAL")
        current_price = indicators.get("current_price", 0)
        
        ema_text = Text()
        ema_text.append(f"${ema9_value:.2f}", style="white")
        
        if current_price > ema9_value:
            ema_text.append(" ▲ Bullish", style="green")
            ema_signal = Text("Signal: BUY", style="bold green")
        elif current_price < ema9_value:
            ema_text.append(" ▼ Bearish", style="red")
            ema_signal = Text("Signal: SELL", style="bold red")
        else:
            ema_text.append(" ─ Neutral", style="yellow")
            ema_signal = Text("Signal: HOLD", style="bold yellow")
        
        price_vs_ema = current_price - ema9_value
        ema_detail = f"Price vs EMA9: {'+' if price_vs_ema >= 0 else ''}${price_vs_ema:.2f} ({'Above' if price_vs_ema >= 0 else 'Below'})"
        
        table.add_row("EMA(9):", ema_text, ema_signal, ema_detail)
        
        vwap_value = indicators.get("vwap", 0)
        vwap_text = Text()
        vwap_text.append(f"${vwap_value:.2f}", style="white")
        
        if current_price > vwap_value:
            vwap_text.append(" ▲ Above VWAP", style="green")
            vwap_signal = f"Avg Price: ${vwap_value:.2f}"
        elif current_price < vwap_value:
            vwap_text.append(" ▼ Below VWAP", style="red")
            vwap_signal = f"Avg Price: ${vwap_value:.2f}"
        else:
            vwap_text.append(" ─ At VWAP", style="yellow")
            vwap_signal = f"Avg Price: ${vwap_value:.2f}"
        
        price_vs_vwap = current_price - vwap_value
        vwap_detail = f"Price vs VWAP: {'+' if price_vs_vwap >= 0 else ''}${price_vs_vwap:.2f} ({'Above' if price_vs_vwap >= 0 else 'Below'})"
        
        table.add_row("VWAP:", vwap_text, vwap_signal, vwap_detail)
        
        macd_value = indicators.get("macd", 0)
        macd_signal_line = indicators.get("macd_signal", 0)
        macd_histogram = macd_value - macd_signal_line
        
        macd_text = Text()
        macd_text.append(f"{macd_value:.2f} / {macd_signal_line:.2f}", style="white")
        
        if macd_histogram > 0:
            macd_text.append(" ▲ Positive", style="green")
            macd_signal = Text("Signal: BULLISH CROSSOVER", style="bold green")
        elif macd_histogram < 0:
            macd_text.append(" ▼ Negative", style="red")
            macd_signal = Text("Signal: BEARISH CROSSOVER", style="bold red")
        else:
            macd_text.append(" ─ Neutral", style="yellow")
            macd_signal = Text("Signal: NEUTRAL", style="bold yellow")
        
        macd_detail = f"Histogram: {macd_histogram:.3f}"
        
        table.add_row("MACD:", macd_text, macd_signal, macd_detail)
        
        table.add_row("", "", "", "")
        
        volume_trend = indicators.get("volume_trend", "neutral")
        rsi_value = indicators.get("rsi", 50)
        
        volume_text = Text()
        if volume_trend == "increasing":
            volume_text.append("▲ Increasing", style="green")
        elif volume_trend == "decreasing":
            volume_text.append("▼ Decreasing", style="red")
        else:
            volume_text.append("─ Stable", style="yellow")
        
        rsi_text = Text()
        rsi_text.append(f"{rsi_value:.1f}", style="white")
        if rsi_value > 70:
            rsi_text.append(" (Overbought)", style="red")
        elif rsi_value < 30:
            rsi_text.append(" (Oversold)", style="green")
        else:
            rsi_text.append(" (Neutral)", style="yellow")
        
        additional_info = f"Volume Trend: {volume_text.plain}    RSI: {rsi_text.plain}"
        
        bottom_row = Table(show_header=False, box=None, expand=True)
        bottom_row.add_column()
        bottom_row.add_column()
        bottom_row.add_row(
            Text(f"Volume Trend: ", style="cyan") + volume_text,
            Text(f"RSI: ", style="cyan") + rsi_text
        )
        
        main_container = Table(show_header=False, box=None, expand=True)
        main_container.add_column()
        main_container.add_row(table)
        main_container.add_row(bottom_row)
        
        return Panel(
            main_container,
            title="TECHNICAL INDICATORS",
            title_align="center",
            border_style="green",
            style="on black"
        )