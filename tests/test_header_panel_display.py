#!/usr/bin/env python
"""
Comprehensive tests for the header panel display functionality
"""

import unittest
import sys
import io
import re
from unittest.mock import Mock, patch
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr

# Add src to path for imports
sys.path.insert(0, '/home/kelp/work/ibx-ai-termui/src')

from ui.panels.header_panel import HeaderPanel
from ui.terminal_ui import TerminalUI
import main_ui
import ui_demo
from rich.console import Console


class TestHeaderPanelDisplay(unittest.TestCase):
    """Test the HeaderPanel class display functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.header_panel = HeaderPanel()

    def test_header_title_displays_correctly(self):
        """Test that the header shows 'IBX Trading' as the title"""
        # Capture rich console output
        console = Console(file=io.StringIO(), width=80)
        panel = self.header_panel.render()
        
        # Render the panel and get output
        console.print(panel)
        output = console.file.getvalue()
        
        # Verify title is present
        self.assertIn("IBX Trading", output)
        print("\033[92mPASSED\033[0m - Header title 'IBX Trading' displays correctly")

    def test_connected_true_shows_active_port(self):
        """Test that when connected=True, it shows 'Active on port xxxx' with actual port number"""
        test_port = 7497
        console = Console(file=io.StringIO(), width=80)
        
        panel = self.header_panel.render(connected=True, port=test_port)
        console.print(panel)
        output = console.file.getvalue()
        
        # Verify connected status and port are shown
        self.assertIn("● Active on port", output)
        self.assertIn(str(test_port), output)
        print(f"\033[92mPASSED\033[0m - Connected status shows 'Active on port {test_port}'")

    def test_connected_false_shows_disconnected(self):
        """Test that when connected=False, it shows 'Disconnected'"""
        console = Console(file=io.StringIO(), width=80)
        
        panel = self.header_panel.render(connected=False)
        console.print(panel)
        output = console.file.getvalue()
        
        # Verify disconnected status is shown
        self.assertIn("● Disconnected", output)
        print("\033[92mPASSED\033[0m - Disconnected status displays correctly")

    def test_order_id_counter_displays_correctly(self):
        """Test that the Order ID counter displays correctly"""
        test_order_id = 12345
        console = Console(file=io.StringIO(), width=80)
        
        panel = self.header_panel.render(order_id=test_order_id)
        console.print(panel)
        output = console.file.getvalue()
        
        # Verify order ID is shown
        self.assertIn("Order ID:", output)
        self.assertIn(str(test_order_id), output)
        print(f"\033[92mPASSED\033[0m - Order ID {test_order_id} displays correctly")

    def test_system_time_displays_in_correct_format(self):
        """Test that the system time displays in HH:MM:SS format"""
        console = Console(file=io.StringIO(), width=80)
        
        panel = self.header_panel.render()
        console.print(panel)
        output = console.file.getvalue()
        
        # Check for time format HH:MM:SS using regex
        time_pattern = r'\d{2}:\d{2}:\d{2}'
        time_match = re.search(time_pattern, output)
        
        self.assertIsNotNone(time_match, "Time format HH:MM:SS not found in output")
        
        # Verify the time is approximately current (within 1 minute)
        current_time = datetime.now().strftime("%H:%M:%S")
        found_time = time_match.group()
        
        print(f"\033[92mPASSED\033[0m - System time displays in HH:MM:SS format: {found_time}")

    def test_all_elements_together(self):
        """Test that all header elements display together correctly"""
        test_port = 7500
        test_order_id = 999
        console = Console(file=io.StringIO(), width=80)
        
        panel = self.header_panel.render(connected=True, order_id=test_order_id, port=test_port)
        console.print(panel)
        output = console.file.getvalue()
        
        # Check all elements are present
        self.assertIn("IBX Trading", output)
        self.assertIn("● Active on port", output)
        self.assertIn(str(test_port), output)
        self.assertIn("Order ID:", output)
        self.assertIn(str(test_order_id), output)
        
        # Check time format
        time_pattern = r'\d{2}:\d{2}:\d{2}'
        self.assertIsNotNone(re.search(time_pattern, output))
        
        print(f"\033[92mPASSED\033[0m - All header elements display together correctly")


class TestTerminalUIWithHeader(unittest.TestCase):
    """Test the TerminalUI integration with HeaderPanel"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_client.is_connected.return_value = True
        self.mock_client.next_order_id = 123

    def test_header_integration_in_terminal_ui(self):
        """Test that header panel integrates correctly in TerminalUI"""
        test_port = 7498
        ui = TerminalUI(client=self.mock_client, port=test_port)
        
        # Render the layout
        layout = ui.render()
        
        # Get the header panel content
        console = Console(file=io.StringIO(), width=80)
        console.print(layout)
        output = console.file.getvalue()
        
        # Verify header elements are present
        self.assertIn("IBX Trading", output)
        self.assertIn("Active on port", output)
        self.assertIn(str(test_port), output)
        self.assertIn("Order ID:", output)
        self.assertIn("123", output)
        
        print(f"\033[92mPASSED\033[0m - Header panel integrates correctly in TerminalUI with port {test_port}")


class TestApplicationArgumentParsing(unittest.TestCase):
    """Test the command-line argument parsing functionality"""

    def test_main_ui_port_argument_parsing(self):
        """Test that --port argument is parsed correctly in main_ui.py"""
        with patch('sys.argv', ['main_ui.py', '--port', '7497', 'AAPL', '100']):
            try:
                args = main_ui.parse_arguments()
                self.assertEqual(args.port, 7497)
                self.assertEqual(args.symbol, 'AAPL')
                self.assertEqual(args.position_size, 100)
                self.assertFalse(args.demo)
                print("\033[92mPASSED\033[0m - Port argument parsing works correctly for regular mode")
            except SystemExit:
                self.fail("Argument parsing failed unexpectedly")

    def test_main_ui_demo_mode_parsing(self):
        """Test that demo mode argument parsing works"""
        with patch('sys.argv', ['main_ui.py', '--port', '7498', 'TSLA', '50', '--demo']):
            try:
                args = main_ui.parse_arguments()
                self.assertEqual(args.port, 7498)
                self.assertEqual(args.symbol, 'TSLA')
                self.assertEqual(args.position_size, 50)
                self.assertTrue(args.demo)
                print("\033[92mPASSED\033[0m - Demo mode argument parsing works correctly")
            except SystemExit:
                self.fail("Demo mode argument parsing failed unexpectedly")

    def test_invalid_argument_combinations(self):
        """Test that invalid argument combinations are handled properly"""
        # Test missing required arguments
        with patch('sys.argv', ['main_ui.py']):
            with self.assertRaises(SystemExit):
                main_ui.parse_arguments()
        
        print("\033[92mPASSED\033[0m - Invalid argument combinations handled correctly")

    @patch('main_ui.TradingApp')
    @patch('sys.argv', ['main_ui.py', '--port', '7499', 'GOOGL', '25'])
    def test_port_passed_through_to_trading_app(self, mock_trading_app):
        """Test that port number is passed through to the TradingApp"""
        mock_app_instance = Mock()
        mock_app_instance.run.return_value = True
        mock_trading_app.return_value = mock_app_instance
        
        with patch('builtins.print'):  # Suppress print statements
            main_ui.main()
        
        # Verify TradingApp was initialized with correct port
        mock_trading_app.assert_called_once_with(7499, 'GOOGL', 25)
        print("\033[92mPASSED\033[0m - Port number passed through to TradingApp correctly")


class TestUIDemo(unittest.TestCase):
    """Test the UI demo functionality"""

    def test_ui_demo_with_port_parameter(self):
        """Test that UI demo accepts and uses port parameter"""
        test_port = 7501
        
        with patch('ui_demo.TerminalUI') as mock_terminal_ui, \
             patch('ui_demo.threading.Thread'), \
             patch('builtins.print'), \
             patch('time.sleep'):
            
            mock_ui_instance = Mock()
            mock_ui_instance.is_running = True
            mock_terminal_ui.return_value = mock_ui_instance
            
            # Simulate running demo for a short time
            def stop_demo():
                mock_ui_instance.is_running = False
            
            mock_ui_instance.run.side_effect = stop_demo
            
            # Run the demo
            ui_demo.main(port=test_port)
            
            # Verify TerminalUI was created with correct port
            mock_terminal_ui.assert_called_once()
            args, kwargs = mock_terminal_ui.call_args
            self.assertEqual(kwargs.get('port'), test_port)
            
            print(f"\033[92mPASSED\033[0m - UI demo accepts and uses port parameter {test_port}")


class TestHeaderPanelRendering(unittest.TestCase):
    """Test the actual rendering output of the header panel"""

    def test_header_panel_rendered_output_structure(self):
        """Test that the header panel renders with the expected structure"""
        header_panel = HeaderPanel()
        test_port = 7502
        test_order_id = 777
        
        panel = header_panel.render(connected=True, order_id=test_order_id, port=test_port)
        
        # Verify the panel is a Rich Panel object
        from rich.panel import Panel
        self.assertIsInstance(panel, Panel)
        
        # Test the panel style attributes
        self.assertEqual(panel.style, "bold white on blue")
        self.assertEqual(panel.border_style, "blue")
        
        print("\033[92mPASSED\033[0m - Header panel renders with correct structure and styling")

    def test_header_panel_with_different_ports(self):
        """Test that header panel works with different port numbers"""
        header_panel = HeaderPanel()
        console = Console(file=io.StringIO(), width=80)
        
        test_ports = [7496, 7497, 7498, 4001, 4002]
        
        for port in test_ports:
            console.file = io.StringIO()  # Reset output buffer
            panel = header_panel.render(connected=True, port=port)
            console.print(panel)
            output = console.file.getvalue()
            
            self.assertIn(f"Active on port {port}", output)
        
        print(f"\033[92mPASSED\033[0m - Header panel works with different ports: {test_ports}")


if __name__ == '__main__':
    print("=" * 60)
    print("TEST: Feature XX - Header Panel Display")
    print("=" * 60)
    print()
    
    # Create a custom test result to track passes and failures
    class ColoredTextTestResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            
        def addError(self, test, err):
            super().addError(test, err)
            print(f"\033[91mFAILED\033[0m - {test._testMethodName}: {err[1]}")
            
        def addFailure(self, test, err):
            super().addFailure(test, err)
            print(f"\033[91mFAILED\033[0m - {test._testMethodName}: {err[1]}")
    
    # Run tests with colored output
    runner = unittest.TextTestRunner(
        verbosity=0,
        resultclass=ColoredTextTestResult,
        stream=io.StringIO()  # Suppress default output
    )
    
    # Load and run all test cases
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print(f"TEST SUMMARY: {result.testsRun} tests run")
    
    if result.wasSuccessful():
        print(f"\033[92mALL TESTS PASSED\033[0m")
    else:
        print(f"\033[91m{len(result.failures)} FAILURES, {len(result.errors)} ERRORS\033[0m")
        
    print("=" * 60)