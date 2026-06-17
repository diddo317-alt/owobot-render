import random
import json
import os
from datetime import datetime, timedelta
import pytz
from typing import Dict, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class ScheduleManager:
    def __init__(self, config: Dict):
        self.config = config['schedule']
        self.timezone = pytz.timezone(config.get('timezone', 'UTC'))
        self.state_file = 'state.json'
        self.schedule_data = self.load_state()
        self.current_schedule = self.generate_weekly_schedule()

    def load_state(self) -> Dict:
        """Load schedule state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_state(self):
        """Save schedule state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(self.schedule_data, f, indent=2)

    def generate_daily_schedule(self) -> Tuple[datetime, datetime]:
        """Generate random schedule for today"""
        start_hour = random.randint(
            self.config['active_window_start_min'],
            self.config['active_window_start_max']
        )
        start_minute = random.randint(0, 59)
        
        # Add day-to-day variance
        variance_hours = random.randint(-self.config['day_to_day_variance'], 
                                       self.config['day_to_day_variance'])
        start_hour = max(6, min(14, start_hour + variance_hours))
        
        duration_hours = random.uniform(
            self.config['active_duration_min'],
            self.config['active_duration_max']
        )
        
        now = datetime.now(self.timezone)
        start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        # If start time has passed, move to tomorrow
        if start_time < now:
            start_time += timedelta(days=1)
            
        end_time = start_time + timedelta(hours=duration_hours)
        
        return start_time, end_time

    def generate_weekly_schedule(self) -> Dict:
        """Generate schedule for the entire week"""
        week_schedule = {}
        today = datetime.now(self.timezone).date()
        
        # Get Monday of current week
        monday = today - timedelta(days=today.weekday())
        
        for i in range(7):
            day = monday + timedelta(days=i)
            start, end = self.generate_daily_schedule()
            # Adjust to the specific day
            start = start.replace(year=day.year, month=day.month, day=day.day)
            end = end.replace(year=day.year, month=day.month, day=day.day)
            
            if end < start:
                end += timedelta(days=1)
                
            week_schedule[day.strftime('%A')] = {
                'date': day.strftime('%Y-%m-%d'),
                'start': start.strftime('%H:%M'),
                'end': end.strftime('%H:%M'),
                'duration': (end - start).total_seconds() / 3600
            }
        
        return week_schedule

    def get_today_schedule(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get today's active schedule"""
        today = datetime.now(self.timezone).date()
        today_name = today.strftime('%A')
        
        if today_name not in self.current_schedule:
            self.current_schedule = self.generate_weekly_schedule()
            
        day_schedule = self.current_schedule[today_name]
        start_time = datetime.strptime(
            f"{day_schedule['date']} {day_schedule['start']}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=self.timezone)
        end_time = datetime.strptime(
            f"{day_schedule['date']} {day_schedule['end']}",
            "%Y-%m-%d %H:%M"
        ).replace(tzinfo=self.timezone)
        
        return start_time, end_time

    def is_active(self) -> bool:
        """Check if bot should be active now"""
        start, end = self.get_today_schedule()
        if not start or not end:
            return False
            
        now = datetime.now(self.timezone)
        return start <= now <= end

    def get_next_active_time(self) -> Optional[datetime]:
        """Get next time bot will be active"""
        now = datetime.now(self.timezone)
        start, end = self.get_today_schedule()
        
        if start and end:
            if now < start:
                return start
            elif now > end:
                # Check tomorrow
                tomorrow = now + timedelta(days=1)
                tomorrow_name = tomorrow.strftime('%A')
                if tomorrow_name in self.current_schedule:
                    day_schedule = self.current_schedule[tomorrow_name]
                    return datetime.strptime(
                        f"{day_schedule['date']} {day_schedule['start']}",
                        "%Y-%m-%d %H:%M"
                    ).replace(tzinfo=self.timezone)
        return None

    def get_weekly_preview(self) -> str:
        """Get formatted weekly schedule preview"""
        preview = "📅 **Weekly Schedule:**\n```text\n"
        for day, schedule in self.current_schedule.items():
            preview += f"{day:10} {schedule['start']} → {schedule['end']}  "
            preview += f"({schedule['duration']:.2f} hours active)\n"
        preview += "```"
        return preview