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
        
        # Set bot presence/status on initialization
        self.set_presence()

    def set_presence(self, status="online", activity_name="OwO hunting 🐱", activity_type=0):
        """
        Set bot presence/status
        status: "online", "idle", "dnd", "invisible"
        activity_type: 0=Playing, 1=Streaming, 2=Listening, 3=Watching, 5=Competing
        activity_name: Name of the activity
        """
        try:
            # Get gateway information
            gateway_url = f"{self.base_url}/gateway/bot"
            response = requests.get(gateway_url, headers=self.headers)
            
            if response.status_code == 200:
                gateway_data = response.json()
                logger.info(f"✅ Gateway connected: {gateway_data.get('url')}")
                
                # For bot accounts, we use the gateway connection
                # Since we can't directly set presence via REST for bots,
                # we log the status and send a heartbeat message
                logger.info(f"🎯 Bot presence: {status} - {activity_type}: {activity_name}")
                
                # Send a simple status message to show bot is online
                self.send_status_message()
                
            else:
                logger.warning(f"Could not connect to gateway: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Could not set presence: {e}")

    def send_status_message(self):
        """Send a status message to show bot is online"""
        try:
            if self.channel_id:
                url = f"{self.base_url}/channels/{self.channel_id}/messages"
                payload = {"content": "🟢 Bot is online and ready!"}
                
                response = requests.post(url, headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    logger.info("✅ Status message sent - bot is online!")
                else:
                    logger.warning(f"Could not send status message: {response.status_code}")
                    
        except Exception as e:
            logger.warning(f"Could not send status message: {e}")

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
            elif response.status_code == 401:
                logger.error("❌ Invalid token! Check DISCORD_TOKEN")
                return {"success": False, "error": "Invalid token"}
            elif response.status_code == 403:
                logger.error("❌ No permission! Check bot permissions")
                return {"success": False, "error": "No permission"}
            elif response.status_code == 404:
                logger.error("❌ Channel not found! Check CHANNEL_ID")
                return {"success": False, "error": "Channel not found"}
            elif response.status_code == 429:
                logger.warning("⏰ Rate limited! Waiting...")
                time.sleep(5)
                # Retry once after rate limit
                response = requests.post(url, headers=self.headers, json=payload)
                if response.status_code == 200:
                    return {"success": True, "response": response.json()}
                else:
                    return {"success": False, "error": response.text}
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

    def get_bot_info(self) -> Optional[Dict]:
        """Get bot information"""
        try:
            url = f"{self.base_url}/users/@me"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting bot info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            return None
