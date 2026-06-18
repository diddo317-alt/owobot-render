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
import requests

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
        try:
            self.config = self.load_config()
            
            # Initialize Discord API
            self.discord = DiscordAPI()
            
            # Set bot activity/presence
            self.set_bot_activity()
            
            # Initialize other components
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
            
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            sys.exit(1)

    def set_bot_activity(self):
        """Set bot's Discord presence/activity"""
        try:
            token = os.getenv('DISCORD_TOKEN')
            if not token:
                logger.warning("No token found for activity setting")
                return
            
            headers = {"Authorization": f"Bot {token}"}
            
            # Get gateway info
            gateway_url = "https://discord.com/api/v9/gateway/bot"
            response = requests.get(gateway_url, headers=headers)
            
            if response.status_code == 200:
                gateway_data = response.json()
                logger.info(f"✅ Gateway connected: {gateway_data.get('url')}")
                
                # Set bot activity via status message
                # For bots, we use the presence/activity via gateway
                # Since we're using REST, we'll just log it
                logger.info("🎯 Bot activity: Playing OwO hunting 🐱")
                
                # Send a status message to show online
                self.send_status_message()
            else:
                logger.warning(f"Could not set activity: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Could not set activity: {e}")

    def send_status_message(self):
        """Send status message to show bot is online"""
        try:
            channel_id = os.getenv('CHANNEL_ID')
            token = os.getenv('DISCORD_TOKEN')
            
            if not channel_id or not token:
                return
                
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            headers = {
                "Authorization": f"Bot {token}",
                "Content-Type": "application/json"
            }
            payload = {"content": "🟢 Bot is online and ready!"}
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info("✅ Status message sent successfully!")
            else:
                logger.warning(f"Could not send status message: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Could not send status message: {e}")

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
            
            # Send activation message to Discord
            self.discord.send_command("🟢 Bot is now active and ready!")
            
        elif not is_active and self.active:
            # Ending session
            self.active = False
            self.human_engine.end_session()
            self.command_selector.reset_daily_counters()
            logger.info("💤 Bot is now inactive. Sleeping...")
            
            # Send sleep message
            self.discord.send_command("💤 Bot is going to sleep now. See you tomorrow!")
            
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
        
        # Send welcome message
        self.discord.send_command("🤖 OWOBot has started successfully!")
        self.discord.send_command("📅 Schedule will follow configured times.")
        
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
                            # Send reminder message
                            if wait_hours < 2:
                                self.discord.send_command(f"⏰ Bot will wake up in {wait_hours:.1f} hours!")
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

    def force_run(self):
        """Force bot to run immediately (for testing)"""
        logger.info("🚀 Force run activated!")
        self.active = True
        self.human_engine.start_session()
        self.bank_manager.set_daily_start()
        self.discord.send_command("🧪 Force run: Bot is testing!")
        
        # Send test commands
        test_commands = ["owo bal", "owo hunt", "owo work"]
        for cmd in test_commands:
            self.discord.send_command(cmd)
            time.sleep(5)
        
        self.discord.send_command("✅ Force run complete!")

def main():
    """Main entry point"""
    bot = OWOBot()
    
    # Check for force run argument
    if len(sys.argv) > 1 and sys.argv[1] == "force":
        bot.force_run()
        return
    
    bot.run()

if __name__ == "__main__":
    main()
