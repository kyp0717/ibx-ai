"""
Trading panel with integrated signal display and nested position/orders
"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.columns import Columns
from datetime import datetime
from typing import Dict, Any


class TradingPanel:
    def __init__(self):
        pass
        
    def render(self, prompt_text: str, symbol: str = "", price: float = 0,
               indicators: Dict[str, Any] = None, position_data: Dict[str, Any] = None,
               order_data: Dict[str, Any] = None) -> Panel:
        """Render the Trading panel with signal, prompt, and position/orders"""
        
        # Left side content (main prompts)
        left_content = Table(show_header=False, box=None, padding=(0, 0), expand=False)
        left_content.add_column(justify="left", width=50)
        
        # Get position quantity
        position_qty = position_data.get("quantity", 0) if position_data else 0
        
        # First line: Time and Status/Signal
        first_line = Text()
        
        # Current time
        current_time = datetime.now().strftime("%H:%M:%S")
        first_line.append(f"[ {current_time} ]", style="cyan")
        first_line.append("  ", style="")
        
        # Determine status based on position
        if position_qty == 0:
            # No position - show signal
            signal_text = self._determine_signal(indicators, price)
            first_line.append(signal_text)
        elif 0 < position_qty < 100:
            # Partial position
            first_line.append("** Opening position ... **", style="bold yellow")
        elif position_qty >= 100:
            # Full position
            first_line.append("** Position is filled! **", style="bold green")
        
        left_content.add_row(first_line)
        
        # Second line: Action prompt based on position
        prompt_line = Text()
        
        if symbol and price > 0:
            if position_qty == 0:
                # No position - prompt to buy
                prompt_line.append(f"Buy {symbol} at {price:.2f} ", style="bold white")
                prompt_line.append("(press enter) ?", style="yellow")
            elif 0 < position_qty < 100:
                # Partial position - review status
                prompt_line.append("Review position status (see panel to the right)", style="white")
            elif position_qty >= 100:
                # Full position - prompt to sell
                prompt_line.append(f"Sell {symbol} at {price:.2f} ", style="bold white")
                prompt_line.append("(press enter) ?", style="yellow")
        else:
            prompt_line = Text("Waiting for market data...", style="dim white")
        
        left_content.add_row(prompt_line)
        
        # Right side content (position and orders)
        right_content = self._create_position_orders_table(position_data, order_data)
        
        # Create side-by-side layout
        side_by_side = Table(show_header=False, box=None, padding=0, expand=True)
        side_by_side.add_column(justify="left", width=50)  # Left column for prompts
        side_by_side.add_column(justify="left", width=46)  # Right column for position/orders
        
        # Add both contents side by side
        side_by_side.add_row(left_content, right_content)
        
        # Dynamic title based on symbol
        panel_title = f"{symbol} Trade" if symbol else "Trade"
        
        return Panel(
            side_by_side,
            title=panel_title,
            title_align="center",
            border_style="yellow",
            style="on black",
            padding=(1, 2),
            width=100  # Full width since it's at the bottom
        )
    
    def _determine_signal(self, indicators: Dict[str, Any], current_price: float) -> Text:
        """Determine trading signal based on indicators"""
        signal_text = Text()
        
        if indicators and current_price > 0:
            ema9_value = indicators.get("ema9", 0)
            vwap_value = indicators.get("vwap", 0)
            macd_value = indicators.get("macd", 0)
            macd_signal_line = indicators.get("macd_signal", 0)
            
            bullish_signals = 0
            bearish_signals = 0
            
            # EMA9 signal
            if ema9_value > 0:
                if current_price > ema9_value:
                    bullish_signals += 1
                elif current_price < ema9_value:
                    bearish_signals += 1
            
            # VWAP signal
            if vwap_value > 0:
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
        
        return signal_text
    
    def _create_position_orders_table(self, position_data: Dict[str, Any], 
                                     order_data: Dict[str, Any]) -> Table:
        """Create orders display with position info (no border)"""
        # Create table without headers
        table = Table(show_header=False, box=None, padding=(0, 0))
        
        # Order section (moved to top)
        table.add_column("Label", style="cyan", width=10)
        table.add_column("Value", style="white", width=10)
        table.add_column("", width=2)  # Vertical separator column
        table.add_column("Label2", style="cyan", width=10)
        table.add_column("Value2", style="white", width=10)
        
        # Order data
        order_id = order_data.get("order_id", "-") if order_data else "-"
        order_status = order_data.get("status", "-") if order_data else "-"
        filled_qty = order_data.get("filled_qty", 0) if order_data else 0
        total_qty = order_data.get("total_qty", 0) if order_data else 0
        order_avg_price = order_data.get("avg_price", 0) if order_data else 0
        
        # Position data
        pos_qty = position_data.get("quantity", 0) if position_data else 0
        pos_avg = position_data.get("avg_cost", 0) if position_data else 0
        
        # Add rows with vertical separator
        table.add_row(
            "Order ID:", f"{order_id}",
            "│",  # Vertical line separator
            "Size:", f"{pos_qty}"  # Changed from Position to Size
        )
        table.add_row(
            "Status:", order_status,
            "│",
            "Avg Cost:", f"${pos_avg:.2f}" if pos_avg > 0 else "-"
        )
        table.add_row(
            "Filled:", f"{filled_qty}/{total_qty}",
            "│",
            "Fill Price:", f"${order_avg_price:.2f}" if order_avg_price > 0 else "-"
        )
        
        return table  # Return table without Panel wrapper