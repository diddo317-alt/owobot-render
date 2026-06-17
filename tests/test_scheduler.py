import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schedule_manager import ScheduleManager
from core.command_selector import CommandSelector
import json

class TestScheduler(unittest.TestCase):
    def setUp(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        self.schedule_manager = ScheduleManager(self.config)
        self.command_selector = CommandSelector(self.config)

    def test_schedule_generation(self):
        """Test schedule generation"""
        start, end = self.schedule_manager.get_today_schedule()
        self.assertIsNotNone(start)
        self.assertIsNotNone(end)
        self.assertLess(start, end)

    def test_is_active(self):
        """Test active status check"""
        is_active = self.schedule_manager.is_active()
        self.assertIn(is_active, [True, False])

    def test_command_selection(self):
        """Test command selection"""
        command = self.command_selector.select_command()
        self.assertIn(command, self.command_selector.commands)

    def test_command_weights(self):
        """Test command weights"""
        total_weight = sum(self.command_selector.weights)
        self.assertEqual(total_weight, 101)  # Sum of all weights

if __name__ == '__main__':
    unittest.main()