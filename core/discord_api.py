import requests
import time
import json
import os
from typing import Optional, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class DiscordAPI:
    def __init__(self):
        self.token = os.getenv('DISCORD_TOKEN')
        self.channel_id = os.getenv('CHANNEL_ID')
        self.base_url = "https://discord.com/api/v9"
        self.headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        self.last_command_time = 0
        self.min_command_interval = 2  # Seconds between commands

    def send_command(self, command: str) -> Dict[str, Any]:
        """Send a command to Discord channel"""
        try:
            # Rate limiting
            current_time = time.time()
            if current_time - self.last_command_time < self.min_command_interval:
                time.sleep(self.min_command_interval - (current_time - self.last_command_time))

            url = f"{self.base_url}/channels/{self.channel_id}/messages"
            payload = {"content": command}
            
            response = requests.post(url, headers=self.headers, json=payload)
            self.last_command_time = time.time()
            
            if response.status_code == 200:
                logger.info(f"Command sent: {command}")
                return {"success": True, "response": response.json()}
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return {"success": False, "error": str(e)}

    def get_message_history(self, limit: int = 50) -> Optional[list]:
        """Get recent message history from channel"""
        try:
            url = f"{self.base_url}/channels/{self.channel_id}/messages"
            params = {"limit": limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting message history: {e}")
            return None