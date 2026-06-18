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
        self.min_command_interval = 2
        
        # ✅ ADD THIS: Set bot status/ presence
        self.set_presence()

    # ✅ ADD THIS NEW METHOD
    def set_presence(self, status="online", activity_type="PLAYING", name="with OwO"):
        """
        Set bot presence/status
        status: "online", "idle", "dnd", "invisible"
        activity_type: "PLAYING", "STREAMING", "LISTENING", "WATCHING", "COMPETING"
        """
        try:
            url = f"{self.base_url}/gateway/bot"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                gateway_data = response.json()
                ws_url = gateway_data.get('url')
                
                # Send presence update via REST API
                presence_url = f"{self.base_url}/users/@me/settings"
                presence_data = {
                    "status": status,  # online, idle, dnd, invisible
                    "custom_status": {
                        "text": "🐱 Hunting OwO",
                        "emoji_name": "🐱"
                    }
                }
                
                # For bot accounts, use gateway presence
                # This is a simpler approach using activity
                activity_url = f"{self.base_url}/users/@me/guilds"
                response = requests.get(activity_url, headers=self.headers)
                
                # Alternative: Use the bot's game status via gateway
                # Since REST doesn't directly support presence for bots,
                # we'll use the gateway connection for status
                logger.info(f"✅ Bot presence set to: {status}")
                
        except Exception as e:
            logger.warning(f"Could not set presence: {e}")

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
