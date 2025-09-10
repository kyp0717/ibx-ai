#!/usr/bin/env python
"""
Comprehensive unit tests for enhanced trading prompt panel
Tests pulsing animation, color-coded borders, action types, and visual states
"""

import sys
import unittest
from unittest.mock import Mock, patch
import os
import time
import io
from contextlib import redirect_stdout

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.panels.trading_prompt import TradingPrompt
from rich.panel import Panel
from rich.text import Text
from rich.console import Console


class TestTradingPromptEnhanced(unittest.TestCase):
    """Test the enhanced trading prompt panel functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.trading_prompt = TradingPrompt()
        self.console = Console(file=io.StringIO(), width=80, legacy_windows=False)
        
    def _get_panel_content(self, panel):
        """Helper method to extract text content from Rich Panel"""
        with io.StringIO() as buffer:
            console = Console(file=buffer, width=80, legacy_windows=False, color_system=None)
            console.print(panel)
            return buffer.getvalue()
        
    def test_initialization(self):
        """Test TradingPrompt initializes with correct default values"""
        prompt = TradingPrompt()
        self.assertTrue(prompt.pulse_state)
        self.assertFalse(prompt.is_awaiting_input)
        self.assertIsInstance(prompt.last_pulse_time, float)
        
    def test_pulse_animation_state_changes(self):
        """Test that pulsing indicator alternates every 0.5 seconds"""
        prompt = TradingPrompt()
        
        # Initial state should be True
        self.assertTrue(prompt.pulse_state)
        
        # Mock time in the module where it's used
        with patch('ui.panels.trading_prompt.time') as mock_time:
            # Set initial time
            prompt.last_pulse_time = 0
            mock_time.time.side_effect = [0.6]  # 0.6 seconds elapsed
            
            # Call render to trigger pulse state update
            panel = prompt.render("Test prompt", "AAPL", 150.0)
            
            # Pulse state should have flipped to False
            self.assertFalse(prompt.pulse_state)
            
        # Test another flip
        with patch('ui.panels.trading_prompt.time') as mock_time:
            prompt.last_pulse_time = 0.6
            mock_time.time.side_effect = [1.2]  # Another 0.6 seconds elapsed
            
            panel = prompt.render("Test prompt", "AAPL", 150.0)
            
            # Pulse state should flip back to True
            self.assertTrue(prompt.pulse_state)
            
    def test_buy_prompt_scenario(self):
        """Test BUY prompt: symbol='AAPL', price=150.50, prompt_text='Open Trade'"""
        panel = self.trading_prompt.render("Open Trade", "AAPL", 150.50)
        
        # Verify panel is created
        self.assertIsInstance(panel, Panel)
        
        # Verify awaiting input state
        self.assertTrue(self.trading_prompt.is_awaiting_input)
        
        # Check panel properties
        self.assertEqual(panel.border_style, "green")
        self.assertIn("AWAITING INPUT", panel.title)
        
        # Verify panel content contains expected elements
        panel_content = self._get_panel_content(panel)
        self.assertIn("AAPL", panel_content)
        self.assertIn("BUY", panel_content)
        self.assertIn("150.50", panel_content)
        self.assertIn("ENTER", panel_content)
        
    def test_sell_prompt_scenario(self):
        """Test SELL prompt: symbol='AAPL', price=151.00, prompt_text='Close position'"""
        panel = self.trading_prompt.render("Close position", "AAPL", 151.00)
        
        # Verify panel is created
        self.assertIsInstance(panel, Panel)
        
        # Verify awaiting input state
        self.assertTrue(self.trading_prompt.is_awaiting_input)
        
        # Check panel properties for sell action
        self.assertEqual(panel.border_style, "red")
        self.assertIn("AWAITING INPUT", panel.title)
        
        # Verify panel content contains expected elements
        panel_content = self._get_panel_content(panel)
        self.assertIn("AAPL", panel_content)
        self.assertIn("SELL", panel_content)
        self.assertIn("151.00", panel_content)
        self.assertIn("ENTER", panel_content)
        
    def test_exit_prompt_scenario(self):
        """Test EXIT prompt: symbol='AAPL', price=0, prompt_text='Exit'"""
        panel = self.trading_prompt.render("Exit", "AAPL", 0)
        
        # Verify panel is created
        self.assertIsInstance(panel, Panel)
        
        # For exit, symbol is provided but price is 0, so not awaiting input
        self.assertFalse(self.trading_prompt.is_awaiting_input)
        
        # Check panel properties for exit (idle state since price is 0)
        self.assertEqual(panel.border_style, "dim white")
        self.assertEqual(panel.title, "PROMPT")
        
        # Exit with actual price should trigger awaiting input
        panel2 = self.trading_prompt.render("Exit", "AAPL", 150.0)
        self.assertTrue(self.trading_prompt.is_awaiting_input)
        self.assertEqual(panel2.border_style, "yellow")
        self.assertIn("AWAITING INPUT", panel2.title)
        
    def test_idle_state_no_symbol(self):
        """Test idle state: no symbol, prompt_text='Waiting for market data...'"""
        panel = self.trading_prompt.render("Waiting for market data...")
        
        # Verify panel is created
        self.assertIsInstance(panel, Panel)
        
        # Verify idle state
        self.assertFalse(self.trading_prompt.is_awaiting_input)
        
        # Check panel properties for idle state
        self.assertEqual(panel.border_style, "dim white")
        self.assertEqual(panel.title, "PROMPT")
        
        # Verify panel content
        panel_content = self._get_panel_content(panel)
        self.assertIn("Waiting for market data", panel_content)
        self.assertNotIn("ENTER", panel_content)
        self.assertNotIn("BUY", panel_content)
        self.assertNotIn("SELL", panel_content)
        
    def test_border_colors_change_by_action_type(self):
        """Test that border colors change based on action type"""
        # Test BUY action (green border)
        panel_buy = self.trading_prompt.render("Open Trade", "AAPL", 150.0)
        self.assertEqual(panel_buy.border_style, "green")
        
        # Test SELL action (red border)
        panel_sell = self.trading_prompt.render("Close position", "TSLA", 200.0)
        self.assertEqual(panel_sell.border_style, "red")
        
        # Test EXIT action (yellow border)
        panel_exit = self.trading_prompt.render("Exit", "MSFT", 300.0)
        self.assertEqual(panel_exit.border_style, "yellow")
        
        # Test custom action (yellow border)
        panel_custom = self.trading_prompt.render("Custom action", "GOOGL", 2500.0)
        self.assertEqual(panel_custom.border_style, "yellow")
        
    def test_keyboard_hints_displayed(self):
        """Test that keyboard hints are displayed for active prompts"""
        # Active prompt should show keyboard hint
        panel_active = self.trading_prompt.render("Open Trade", "AAPL", 150.0)
        panel_content = self._get_panel_content(panel_active)
        self.assertIn("ENTER", panel_content)
        self.assertIn("to confirm", panel_content)
        
        # Idle state should not show keyboard hint
        panel_idle = self.trading_prompt.render("Waiting...")
        panel_content_idle = self._get_panel_content(panel_idle)
        self.assertNotIn("ENTER", panel_content_idle)
        self.assertNotIn("to confirm", panel_content_idle)
        
    def test_title_changes_between_active_and_idle(self):
        """Test title changes between active and idle states"""
        # Test active state title
        panel_active = self.trading_prompt.render("Buy now", "AAPL", 150.0)
        self.assertIn("AWAITING INPUT", panel_active.title)
        
        # Test idle state title
        panel_idle = self.trading_prompt.render("No action")
        self.assertEqual(panel_idle.title, "PROMPT")
        
    def test_title_animation_with_pulse_state(self):
        """Test that title animation changes with pulse state"""
        # Test with pulse_state True
        self.trading_prompt.pulse_state = True
        panel1 = self.trading_prompt.render("Trade", "AAPL", 150.0)
        self.assertIn("⚡", panel1.title)
        
        # Test with pulse_state False
        self.trading_prompt.pulse_state = False
        panel2 = self.trading_prompt.render("Trade", "AAPL", 150.0)
        self.assertNotIn("⚡", panel2.title)
        
    def test_symbol_price_formatting(self):
        """Test proper formatting of symbol and price in prompts"""
        # Test price formatting to 2 decimal places
        panel = self.trading_prompt.render("Open Trade", "AAPL", 150.5)
        panel_content = self._get_panel_content(panel)
        self.assertIn("150.50", panel_content)
        
        # Test symbol display
        self.assertIn("AAPL", panel_content)
        
        # Test different price formats
        panel2 = self.trading_prompt.render("Close position", "TSLA", 999.999)
        panel_content2 = self._get_panel_content(panel2)
        self.assertIn("1000.00", panel_content2)  # Python rounds 999.999 to 1000.00
        
    def test_action_type_detection(self):
        """Test detection of different action types from prompt text"""
        # Test BUY detection variations
        buy_prompts = ["Open Trade", "buy now", "Buy Stock", "BUY ACTION"]
        for prompt in buy_prompts:
            panel = self.trading_prompt.render(prompt, "AAPL", 150.0)
            panel_content = self._get_panel_content(panel)
            if "Open Trade" in prompt or "buy" in prompt.lower():
                self.assertIn("BUY", panel_content)
                self.assertEqual(panel.border_style, "green")
        
        # Test SELL detection variations
        sell_prompts = ["Close position", "sell now", "Sell Stock", "SELL ACTION"]
        for prompt in sell_prompts:
            panel = self.trading_prompt.render(prompt, "AAPL", 150.0)
            panel_content = self._get_panel_content(panel)
            if "Close position" in prompt or "sell" in prompt.lower():
                self.assertIn("SELL", panel_content)
                self.assertEqual(panel.border_style, "red")
        
        # Test EXIT detection
        panel_exit = self.trading_prompt.render("Exit", "AAPL", 150.0)
        panel_content = self._get_panel_content(panel_exit)
        self.assertIn("EXIT", panel_content)
        self.assertEqual(panel_exit.border_style, "yellow")
        
    def test_awaiting_input_logic(self):
        """Test the logic that determines awaiting input state"""
        # Should be awaiting input when symbol and price > 0
        self.trading_prompt.render("Trade", "AAPL", 150.0)
        self.assertTrue(self.trading_prompt.is_awaiting_input)
        
        # Should NOT be awaiting input when no symbol
        self.trading_prompt.render("Trade", "", 150.0)
        self.assertFalse(self.trading_prompt.is_awaiting_input)
        
        # Should NOT be awaiting input when price is 0
        self.trading_prompt.render("Trade", "AAPL", 0)
        self.assertFalse(self.trading_prompt.is_awaiting_input)
        
        # Should NOT be awaiting input when both missing
        self.trading_prompt.render("Trade", "", 0)
        self.assertFalse(self.trading_prompt.is_awaiting_input)
        
    def test_pulse_timing_accuracy(self):
        """Test that pulse timing is accurate to 0.5 second intervals"""
        prompt = TradingPrompt()
        
        # Test that pulse doesn't change before 0.5 seconds
        with patch('ui.panels.trading_prompt.time') as mock_time:
            prompt.last_pulse_time = 0
            mock_time.time.side_effect = [0.4]  # Less than 0.5 seconds elapsed
            initial_state = prompt.pulse_state
            prompt.render("Test", "AAPL", 150.0)
            self.assertEqual(prompt.pulse_state, initial_state)
            
        # Test that pulse changes after more than 0.5 seconds
        with patch('ui.panels.trading_prompt.time') as mock_time:
            prompt.last_pulse_time = 0
            mock_time.time.side_effect = [0.51]  # More than 0.5 seconds elapsed
            initial_state = prompt.pulse_state
            prompt.render("Test", "AAPL", 150.0)
            self.assertEqual(prompt.pulse_state, not initial_state)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)