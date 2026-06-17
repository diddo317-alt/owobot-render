import random
import time
from datetime import datetime
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class HumanEngine:
    def __init__(self, config: Dict):
        self.config = config['human_mimicry']
        self.active_start_time = None
        self.active_duration = 0
        self.daily_activity_level = 1.0
        self.mood = "normal"

    def calculate_activity_level(self) -> float:
        """Calculate current activity level based on various factors"""
        # Base level
        level = self.daily_activity_level

        # Fatigue simulation after 4 hours
        if self.active_duration > 4 * 3600:  # 4 hours in seconds
            fatigue = self.config['fatigue_drop_percent'] / 100
            fatigue_factor = min(1.0, (self.active_duration - 4*3600) / 3600)
            level *= (1 - fatigue * fatigue_factor)

        # Random mood variance
        if self.mood == "lazy":
            level *= 0.7
        elif self.mood == "energetic":
            level *= 1.2

        return max(0.3, min(1.0, level))

    def get_command_delay(self) -> int:
        """Get human-like delay between commands"""
        base_delay = random.randint(
            self.config['min_delay_seconds'],
            self.config['max_delay_seconds']
        )
        
        # Apply activity level modifier
        activity_level = self.calculate_activity_level()
        adjusted_delay = base_delay / activity_level
        
        # Add jitter
        jitter = random.uniform(-0.15, 0.15)  # ±15% jitter
        final_delay = adjusted_delay * (1 + jitter)
        
        return int(max(30, final_delay))

    def should_execute_command(self) -> bool:
        """Decide if bot should execute a command now"""
        activity_level = self.calculate_activity_level()
        chance = 0.7 * activity_level  # Base 70% chance, modified by activity
        
        # Weekend boost
        if datetime.now().weekday() >= 5:  # Saturday/Sunday
            chance *= 1.2

        return random.random() < chance

    def get_batch_size(self) -> int:
        """Determine batch size for command batching"""
        if random.random() < self.config['batch_chance']:
            # Batch of 2-3 commands
            return random.randint(2, 3)
        return 1

    def set_mood(self):
        """Set random daily mood"""
        if random.random() < self.config['lazy_day_chance']:
            self.mood = "lazy"
            logger.info("Lazy day mode activated")
        elif random.random() < self.config['energetic_day_chance']:
            self.mood = "energetic"
            logger.info("Energetic day mode activated")
        else:
            self.mood = "normal"

    def update_active_duration(self):
        """Update active duration tracking"""
        if self.active_start_time:
            self.active_duration = (datetime.now() - self.active_start_time).total_seconds()

    def start_session(self):
        """Start a new active session"""
        self.active_start_time = datetime.now()
        self.active_duration = 0
        self.set_mood()
        logger.info(f"Session started with mood: {self.mood}")

    def end_session(self):
        """End the current session"""
        self.active_start_time = None
        self.active_duration = 0
        self.mood = "normal"
        logger.info("Session ended")