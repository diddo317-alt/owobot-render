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
        
        # ✅ FIX: Validate and correct command formats
        self.validate_commands()

    def validate_commands(self):
        """✅ ADD THIS: Ensure all commands have proper 'owo ' prefix"""
        corrected_commands = []
        
        for cmd in self.commands:
            # Check if command already has 'owo ' prefix
            if not cmd.startswith('owo '):
                # Check if it's a single word command (like 'hunt', 'work', 'bal')
                if ' ' not in cmd:
                    # Add 'owo ' prefix
                    corrected_cmd = f'owo {cmd}'
                    logger.info(f"✅ Corrected command: '{cmd}' -> '{corrected_cmd}'")
                    
                    # Update the command in all dictionaries
                    idx = self.commands.index(cmd)
                    self.commands[idx] = corrected_cmd
                    
                    # Update daily_usage
                    if cmd in self.daily_usage:
                        self.daily_usage[corrected_cmd] = self.daily_usage.pop(cmd, 0)
                    
                    # Update last_used
                    if cmd in self.last_used:
                        self.last_used[corrected_cmd] = self.last_used.pop(cmd, 0)
                    
                    # Update max_per_day
                    if cmd in self.max_per_day:
                        self.max_per_day[corrected_cmd] = self.max_per_day.pop(cmd, None)
                    
                    # Update commands_config
                    if cmd in self.commands_config:
                        self.commands_config[corrected_cmd] = self.commands_config.pop(cmd)
        
        # Rebuild commands list
        self.commands = list(self.commands_config.keys())
        logger.info(f"✅ Final commands: {self.commands}")

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
            selected = random.choice(fallback_commands)
            logger.info(f"🔄 Fallback command selected: {selected}")
            return selected
        
        selected = random.choices(available_commands, weights=available_weights, k=1)[0]
        logger.info(f"🎯 Command selected: {selected}")
        return selected

    def increment_usage(self, command: str):
        """Increment usage counter for a command"""
        if command in self.daily_usage:
            self.daily_usage[command] += 1
            self.last_used[command] = len(self.daily_usage)
            logger.debug(f"📊 {command} usage: {self.daily_usage[command]}/{self.max_per_day.get(command, '∞')}")

    def reset_daily_counters(self):
        """Reset daily usage counters"""
        self.daily_usage = {cmd: 0 for cmd in self.commands}
        logger.info("🔄 Daily command counters reset")

    def get_command_delay(self) -> int:
        """Get random delay between commands (2-45 minutes)"""
        delay = random.randint(120, 2700)
        logger.debug(f"⏰ Next command in {delay//60} minutes")
        return delay

    def should_batch_commands(self) -> bool:
        """Determine if commands should be batched"""
        should_batch = random.random() < 0.3  # 30% chance
        if should_batch:
            logger.info("📦 Batch mode activated")
        return should_batch
    
    def get_batch_size(self) -> int:
        """Get number of commands to batch"""
        return random.randint(2, 3)
