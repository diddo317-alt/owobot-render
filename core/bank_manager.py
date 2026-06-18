import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class BankManager:
    def __init__(self, config: Dict):
        self.config = config['bankroll']
        self.state_file = 'state.json'
        self.bank_state = self.load_state()
        self.daily_start_balance = self.bank_state.get('daily_start_balance', 0)
        self.current_balance = self.bank_state.get('current_balance', 0)
        self.last_gamble_time = None
        self.consecutive_losses = 0
        self.winning_streak = 0
        
        # Initialize current balance if not set
        if self.current_balance == 0:
            self.current_balance = 1000  # Starting balance
            self.save_state()

    def load_state(self) -> Dict:
        """Load bank state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_state(self):
        """Save bank state to file"""
        self.bank_state.update({
            'daily_start_balance': self.daily_start_balance,
            'current_balance': self.current_balance,
            'last_gamble_time': self.last_gamble_time.isoformat() if self.last_gamble_time else None,
            'consecutive_losses': self.consecutive_losses,
            'winning_streak': self.winning_streak
        })
        with open(self.state_file, 'w') as f:
            json.dump(self.bank_state, f, indent=2)

    def update_balance(self, new_balance: int):
        """Update current balance"""
        self.current_balance = new_balance
        if self.current_balance > self.daily_start_balance:
            self.winning_streak += 1
            self.consecutive_losses = 0
        self.save_state()

    def set_daily_start(self):
        """Set daily starting balance"""
        self.daily_start_balance = self.current_balance
        self.consecutive_losses = 0
        self.winning_streak = 0
        self.save_state()
        logger.info(f"📊 Daily start balance: {self.daily_start_balance}")

    def can_gamble(self) -> bool:
        """Check if gambling is allowed based on bankroll management"""
        # Check stop-loss
        if self.daily_start_balance > 0:
            loss_percent = ((self.daily_start_balance - self.current_balance) / 
                          self.daily_start_balance) * 100
            if loss_percent >= self.config['stop_loss_percent']:
                logger.info(f"⛔ Stop-loss triggered: {loss_percent:.1f}% loss")
                return False

        # Check win lock-in
        if self.winning_streak >= 3:
            if self.current_balance > self.daily_start_balance * 1.2:
                lock_duration = self.config['win_lock_duration']
                logger.info(f"🔒 Win lock-in active for {lock_duration} hours")
                return False

        # Check loss recovery wait time
        if self.consecutive_losses > 0 and self.last_gamble_time:
            wait_minutes = random.randint(
                self.config['loss_recovery_wait_min'],
                self.config['loss_recovery_wait_max']
            )
            time_since = (datetime.now() - self.last_gamble_time).total_seconds() / 60
            if time_since < wait_minutes:
                logger.info(f"⏰ Loss recovery wait: {wait_minutes - time_since:.0f} minutes remaining")
                return False

        return True

    def get_bet_amount(self) -> int:
        """Calculate bet amount based on current balance"""
        max_bet = int(self.current_balance * (self.config['max_bet_percent'] / 100))
        bet_options = [25, 50, 75, 100]
        
        # Filter options based on balance
        available_bets = [b for b in bet_options if b <= max_bet]
        if not available_bets:
            return min(25, max_bet)
            
        return random.choice(available_bets)

    def record_gamble(self, won: bool, amount: int):
        """Record gamble result"""
        self.last_gamble_time = datetime.now()
        if won:
            self.winning_streak += 1
            self.consecutive_losses = 0
            logger.info(f"🎉 Won {amount} coins! Streak: {self.winning_streak}")
        else:
            self.consecutive_losses += 1
            self.winning_streak = 0
            logger.info(f"😢 Lost {amount} coins. Losses: {self.consecutive_losses}")
        self.save_state()
