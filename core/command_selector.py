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
        
        # ✅ FORCE FIX: Ensure ALL commands have 'owo ' prefix
        self.force_owo_prefix()

    def force_owo_prefix(self):
        """✅ FORCE all commands to have 'owo ' prefix"""
        corrected_commands = {}
        
        for cmd in self.commands:
            # Check if command already has 'owo ' prefix
            if not cmd.lower().startswith('owo '):
                # Remove any existing prefix and add 'owo '
                # Split by space and take the last part (the actual command)
                parts = cmd.split()
                if parts:
                    # If it's a command with arguments (like 'slot 50')
                    if len(parts) > 1 and parts[0].lower() != 'owo':
                        # Keep arguments, add 'owo ' prefix
                        actual_cmd = ' '.join(parts)
                        corrected_cmd = f'owo {actual_cmd}'
                    elif len(parts) == 1:
                        # Single word command
                        corrected_cmd = f'owo {parts[0]}'
                    else:
                        corrected_cmd = cmd
                else:
                    corrected_cmd = cmd
                
                logger.info(f"✅ Force corrected: '{cmd}' -> '{corrected_cmd}'")
                
                # Update all dictionaries
                idx = self.commands.index(cmd)
                self.commands[idx] = corrected_cmd
                
                if cmd in self.daily_usage:
                    self.daily_usage[corrected_cmd] = self.daily_usage.pop(cmd, 0)
                if cmd in self.last_used:
                    self.last_used[corrected_cmd] = self.last_used.pop(cmd, 0)
                if cmd in self.max_per_day:
                    self.max_per_day[corrected_cmd] = self.max_per_day.pop(cmd, None)
                if cmd in self.commands_config:
                    self.commands_config[corrected_cmd] = self.commands_config.pop(cmd)
            else:
                # Already has 'owo ' prefix, keep it
                corrected_commands[cmd] = self.commands_config[cmd]
        
        # Rebuild commands list
        self.commands = list(self.commands_config.keys())
        
        # Log final commands
        logger.info(f"📋 FINAL COMMANDS: {self.commands}")
        
        # Double-check all commands have 'owo ' prefix
        for cmd in self.commands:
            if not cmd.lower().startswith('owo '):
                logger.error(f"❌ COMMAND WITHOUT PREFIX: {cmd}")
                # Force fix it
                fixed_cmd = f'owo {cmd}'
                logger.info(f"🔧 Emergency fix: {cmd} -> {fixed_cmd}")
                idx = self.commands.index(cmd)
                self.commands[idx] = fixed_cmd

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
