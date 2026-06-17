import random
from typing import Dict, List, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class CommandSelector:
    def __init__(self, config: Dict):
        self.commands_config = config['commands']
        self.commands = list(self.commands_config.keys())
        self.weights = [cmd['weight'] for cmd in self.commands_config.values()]
        self.max_per_day = {cmd: data['max_per_day'] for cmd, data in self.commands_config.items()}
        self.daily_usage = {cmd: 0 for cmd in self.commands}
        self.last_used = {cmd: 0 for cmd in self.commands}

    def select_command(self) -> str:
        """Select a command based on weighted probability"""
        # Check if any command has reached its daily limit
        available_commands = []
        available_weights = []
        
        for cmd in self.commands:
            max_allowed = self.max_per_day.get(cmd)
            if max_allowed is None or self.daily_usage[cmd] < max_allowed:
                available_commands.append(cmd)
                available_weights.append(self.weights[self.commands.index(cmd)])
        
        if not available_commands:
            # Fallback to command with lowest usage
            min_usage = min(self.daily_usage.values())
            fallback_commands = [cmd for cmd, usage in self.daily_usage.items() if usage == min_usage]
            return random.choice(fallback_commands)
        
        return random.choices(available_commands, weights=available_weights, k=1)[0]

    def increment_usage(self, command: str):
        """Increment usage counter for a command"""
        if command in self.daily_usage:
            self.daily_usage[command] += 1
            self.last_used[command] = len(self.daily_usage)

    def reset_daily_counters(self):
        """Reset daily usage counters"""
        self.daily_usage = {cmd: 0 for cmd in self.commands}
        logger.info("Daily command counters reset")

    def get_command_delay(self) -> int:
        """Get random delay between commands (2-45 minutes)"""
        return random.randint(120, 2700)

    def should_batch_commands(self) -> bool:
        """Determine if commands should be batched"""
        return random.random() < 0.3  # 30% chance