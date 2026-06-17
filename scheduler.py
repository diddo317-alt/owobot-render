#!/usr/bin/env python3
import os
import sys
import json
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.schedule_manager import ScheduleManager
from utils.logger import get_logger

logger = get_logger(__name__)

class BotScheduler:
    def __init__(self):
        self.config = self.load_config()
        self.schedule_manager = ScheduleManager(self.config)
        self.scheduler = BlockingScheduler()
        self.setup_jobs()

    def load_config(self) -> dict:
        """Load configuration from file"""
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.error("config.json not found!")
            sys.exit(1)

    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Main bot job - runs every 5 minutes during active hours
        self.scheduler.add_job(
            self.check_and_run,
            'interval',
            minutes=5,
            id='main_bot_job',
            next_run_time=datetime.now()
        )
        
        # Daily reset at midnight
        self.scheduler.add_job(
            self.daily_reset,
            CronTrigger(hour=0, minute=0),
            id='daily_reset_job'
        )
        
        logger.info("✅ Scheduler jobs configured")

    def check_and_run(self):
        """Check schedule and run bot if active"""
        try:
            if self.schedule_manager.is_active():
                logger.info("🔄 Running bot check...")
                # Import and run main bot
                from main import OWOBot
                bot = OWOBot()
                # Run one cycle
                bot.check_schedule()
                bot.execute_commands()
            else:
                # Log schedule status
                next_time = self.schedule_manager.get_next_active_time()
                if next_time:
                    wait_hours = (next_time - datetime.now()).total_seconds() / 3600
                    logger.info(f"💤 Scheduled sleep. Next active in {wait_hours:.2f} hours")
        except Exception as e:
            logger.error(f"❌ Error in scheduled task: {e}")

    def daily_reset(self):
        """Reset daily counters"""
        logger.info("🔄 Daily reset running...")
        try:
            # Clean up state
            state_file = 'state.json'
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                # Reset daily counters
                state['daily_commands'] = {}
                state['daily_start_balance'] = state.get('current_balance', 0)
                with open(state_file, 'w') as f:
                    json.dump(state, f, indent=2)
            logger.info("✅ Daily reset complete")
        except Exception as e:
            logger.error(f"❌ Error during daily reset: {e}")

    def run(self):
        """Start the scheduler"""
        logger.info("🚀 Starting scheduler...")
        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")

def main():
    scheduler = BotScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()