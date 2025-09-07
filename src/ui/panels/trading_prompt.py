"""
Interactive trading prompt panel for buy/sell actions
"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align


class TradingPrompt:
    def __init__(self):
        pass
    
    def render(self, prompt_text: str, symbol: str = "", price: float = 0) -> Panel:
        """Render the trading prompt panel"""
        
        if symbol and price > 0:
            prompt = Text()
            prompt.append(f"{symbol} >>> ", style="bold cyan")
            
            if "Open Trade" in prompt_text or "buy" in prompt_text.lower():
                prompt.append(f"Open Trade at ${price:.2f} ", style="bold yellow")
                prompt.append("(press enter)?", style="yellow")
            elif "Close position" in prompt_text or "sell" in prompt_text.lower():
                prompt.append(f"Close position at ${price:.2f} ", style="bold yellow")
                prompt.append("(press enter)?", style="yellow")
            elif "Exit" in prompt_text:
                prompt.append("Exit the trade ", style="bold yellow")
                prompt.append("(press enter)?", style="yellow")
            else:
                prompt.append(prompt_text, style="yellow")
        else:
            prompt = Text(prompt_text, style="dim white")
        
        return Panel(
            Align.left(prompt),
            border_style="yellow",
            style="bold on black",
            padding=(0, 1)
        )