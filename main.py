#!/usr/bin/env python3
import os
import sys
import json
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import signal
import threading

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.discord_api import DiscordAPI
from core.command_selector import CommandSelector
from core.schedule_manager import ScheduleManager
from core.bank_manager import BankManager
from core.human_engine import HumanEngine
from utils.logger import get_logger
from utils.stats_tracker import StatsTracker

logger = get_logger(__name__)

class OWOBot:
    def __init__(self):
        """Initialize the OWOBot"""
        self.config = self.load_config()
        self.discord = DiscordAPI()
        self.command_selector = CommandSelector(self.config)
        self.schedule_manager = ScheduleManager(self.config)
        self.bank_manager = BankManager(self.config)
        self.human_engine = HumanEngine(self.config)
        self.stats_tracker = StatsTracker()
        self.running = True
        self.active = False
        self.session_start = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info("🤖 OWOBot initialized successfully!")

    def load_config(self) -> dict:
        """Load configuration from file"""
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.error("config.json not found!")
            sys.exit(1)

    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Cleanup resources before exit"""
        logger.info("Cleaning up...")
        self.bank_manager.save_state()
        self.stats_tracker.save_stats()
        logger.info("💾 State saved successfully!")

    def check_schedule(self) -> bool:
        """Check if bot should be active based on schedule"""
        is_active = self.schedule_manager.is_active()
        
        if is_active and not self.active:
            # Starting new session
            self.active = True
            self.session_start = datetime.now()
            self.human_engine.start_session()
            self.bank_manager.set_daily_start()
            logger.info("🚀 Bot is now active!")
            
            # Send schedule preview
            preview = self.schedule_manager.get_weekly_preview()
            logger.info(preview)
            
        elif not is_active and self.active:
            # Ending session
            self.active = False
            self.human_engine.end_session()
            self.command_selector.reset_daily_counters()
            logger.info("💤 Bot is now inactive. Sleeping...")
            
            # Calculate next active time
            next_time = self.schedule_manager.get_next_active_time()
            if next_time:
                wait_seconds = (next_time - datetime.now()).total_seconds()
                wait_hours = wait_seconds / 3600
                logger.info(f"Next active session in {wait_hours:.2f} hours")
        
        return is_active

    def execute_commands(self):
        """Execute bot commands"""
        if not self.active:
            return

        # Check if we should execute a command
        if not self.human_engine.should_execute_command():
            # Skip this cycle
            return

        # Update human engine state
        self.human_engine.update_active_duration()

        # Select command
        command = self.command_selector.select_command()
        
        # Handle gambling commands with bankroll management
        if 'slot' in command:
            if not self.bank_manager.can_gamble():
                return
                
            # Add bet amount to command
            bet_amount = self.bank_manager.get_bet_amount()
            command = f"owo slot {bet_amount}"
            logger.info(f"🎰 Gambling with {bet_amount} coins")

        # Send command
        result = self.discord.send_command(command)
        
        # Update tracking
        success = result.get('success', False)
        self.stats_tracker.track_command(command, success)
        self.command_selector.increment_usage(command)
        
        if 'slot' in command:
            # For gambling, we would need to parse response to determine win/loss
            # This is a placeholder - you'd need to implement response parsing
            if success:
                # Simulate win/loss tracking (you'd parse actual response)
                won = random.random() > 0.45  # ~55% win rate
                self.bank_manager.record_gamble(won, bet_amount if bet_amount else 0)

        # Get delay before next command
        delay = self.human_engine.get_command_delay()
        
        # Check if we should batch commands
        if self.human_engine.get_batch_size() > 1:
            # Execute batch of commands with short delays
            time.sleep(random.randint(5, 15))
            # ... implement batching logic

        # Schedule next execution
        return delay

    def run(self):
        """Main bot loop"""
        logger.info("🏃 OWOBot is starting main loop...")
        logger.info("📋 Command configuration loaded:")
        
        # Log command weights
        for cmd, data in self.config['commands'].items():
            max_per_day = data.get('max_per_day', '∞')
            logger.info(f"  {cmd}: weight={data['weight']}, max/day={max_per_day}")
        
        logger.info("📅 Schedule configuration loaded.")
        
        while self.running:
            try:
                # Check if we're in active window
                is_active = self.check_schedule()
                
                if is_active:
                    # Execute commands
                    delay = self.execute_commands()
                    
                    # If no delay was returned, use default
                    if delay is None:
                        delay = random.randint(60, 300)  # 1-5 minutes
                else:
                    # Inactive - check every 15 minutes
                    delay = 900  # 15 minutes
                    
                    # Log status periodically
                    if not hasattr(self, '_last_status_log'):
                        self._last_status_log = datetime.now()
                    
                    if (datetime.now() - self._last_status_log).seconds > 3600:
                        next_time = self.schedule_manager.get_next_active_time()
                        if next_time:
                            wait_hours = (next_time - datetime.now()).total_seconds() / 3600
                            logger.info(f"💤 Bot is sleeping. Next active in {wait_hours:.2f} hours")
                        self._last_status_log = datetime.now()
                
                # Sleep before next iteration
                time.sleep(delay)
                
            except KeyboardInterrupt:
                self.signal_handler(0, 0)
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                # Wait before retrying
                time.sleep(random.randint(30, 120))
                continue

def main():
    """Main entry point"""
    bot = OWOBot()
    bot.run()

if __name__ == "__main__":
    main()