"""
Interactive trading prompt panel for buy/sell actions with enhanced visual feedback
"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
import time


class TradingPrompt:
    def __init__(self):
        self.pulse_state = True
        self.last_pulse_time = time.time()
        self.is_awaiting_input = False
        
    def render(self, prompt_text: str, symbol: str = "", price: float = 0) -> Panel:
        """Render the trading prompt panel with enhanced visual indicators"""
        
        # Update pulse state every 0.5 seconds
        current_time = time.time()
        if current_time - self.last_pulse_time > 0.5:
            self.pulse_state = not self.pulse_state
            self.last_pulse_time = current_time
        
        # Create main container
        container = Table(show_header=False, box=None, padding=0, expand=True)
        container.add_column(width=None)
        
        # Determine if we're awaiting input
        self.is_awaiting_input = symbol and price > 0
        
        if self.is_awaiting_input:
            # Build the prompt with enhanced formatting
            prompt_line = Text()
            
            # Add pulsing indicator
            if self.pulse_state:
                prompt_line.append("● ", style="bold green blink")
            else:
                prompt_line.append("○ ", style="dim green")
            
            # Add symbol
            prompt_line.append(f"{symbol} ", style="bold cyan")
            prompt_line.append(">>> ", style="bold white")
            
            # Add action with enhanced styling
            if "Open Trade" in prompt_text or "buy" in prompt_text.lower():
                prompt_line.append("BUY", style="bold green on dark_green")
                prompt_line.append(f" at ${price:.2f} ", style="bold white")
                action_type = "buy"
                border_color = "green"
            elif "Close position" in prompt_text or "sell" in prompt_text.lower():
                prompt_line.append("SELL", style="bold red on dark_red")
                prompt_line.append(f" at ${price:.2f} ", style="bold white")
                action_type = "sell"
                border_color = "red"
            elif "Exit" in prompt_text:
                prompt_line.append("EXIT", style="bold yellow on rgb(80,60,0)")
                prompt_line.append(" the trade ", style="bold white")
                action_type = "exit"
                border_color = "yellow"
            else:
                prompt_line.append(prompt_text, style="yellow")
                action_type = "custom"
                border_color = "yellow"
            
            # Add keyboard hint with emphasis
            keyboard_hint = Text()
            keyboard_hint.append(" Press ", style="dim white")
            keyboard_hint.append("[ENTER]", style="bold white on rgb(0,50,100)")
            keyboard_hint.append(" to confirm", style="dim white")
            
            # Add both lines to container
            container.add_row(Align.center(prompt_line))
            container.add_row(Align.center(keyboard_hint))
            
            # Panel title with status
            if self.pulse_state:
                title = "⚡ AWAITING INPUT ⚡"
            else:
                title = "   AWAITING INPUT   "
                
        else:
            # Idle state - no active prompt
            prompt_line = Text(prompt_text, style="dim white")
            container.add_row(Align.center(prompt_line))
            border_color = "dim white"
            title = "PROMPT"
        
        # Return panel with dynamic border color
        return Panel(
            container,
            border_style=border_color if self.is_awaiting_input else "dim white",
            title=title,
            title_align="center",
            style="bold on black" if self.is_awaiting_input else "on black",
            padding=(0, 1)
        )