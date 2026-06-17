import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class StatsTracker:
    def __init__(self):
        self.stats_file = 'stats.json'
        self.stats = self.load_stats()

    def load_stats(self) -> Dict:
        """Load statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {'history': []}

    def save_stats(self):
        """Save statistics to file"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def track_command(self, command: str, success: bool):
        """Track command execution"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.stats:
            self.stats[today] = {
                'commands': {},
                'total_commands': 0,
                'successful_commands': 0,
                'failed_commands': 0
            }
        
        self.stats[today]['commands'][command] = self.stats[today]['commands'].get(command, 0) + 1
        self.stats[today]['total_commands'] += 1
        
        if success:
            self.stats[today]['successful_commands'] += 1
        else:
            self.stats[today]['failed_commands'] += 1
            
        self.save_stats()

    def get_daily_summary(self) -> Dict:
        """Get summary for today"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.stats.get(today, {})

    def get_weekly_summary(self) -> Dict:
        """Get summary for the past week"""
        week_start = datetime.now() - timedelta(days=7)
        weekly_data = {}
        
        for date_str, data in self.stats.items():
            if isinstance(data, dict) and 'commands' in data:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                if date >= week_start:
                    weekly_data[date_str] = data
                    
        return weekly_data

    def get_command_breakdown(self) -> Dict:
        """Get breakdown of commands used"""
        breakdown = {}
        for date, data in self.stats.items():
            if isinstance(data, dict) and 'commands' in data:
                for cmd, count in data['commands'].items():
                    breakdown[cmd] = breakdown.get(cmd, 0) + count
        return breakdown

    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        daily_data = self.get_daily_summary()
        total_commands = daily_data.get('total_commands', 0)
        successful = daily_data.get('successful_commands', 0)
        
        success_rate = (successful / total_commands * 100) if total_commands > 0 else 0
        
        return {
            'total_commands': total_commands,
            'success_rate': success_rate,
            'command_breakdown': self.get_command_breakdown()
        }