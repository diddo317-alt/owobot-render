import requests
import time
import json
import os
from typing import Optional, Dict, Any, List
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
        self.min_command_interval = 5  # ✅ INCREASED to avoid rate limits
        self.owo_bot_name = None  # Will store OwO bot's name
        
        # Set bot presence/status on initialization
        self.set_presence()
        # ✅ Find OwO bot in the channel
        self.find_owo_bot()

    def find_owo_bot(self):
        """✅ ADD THIS: Find the OwO bot in the channel"""
        try:
            # Get recent messages to find OwO bot
            messages = self.get_message_history(50)
            if messages:
                for msg in messages:
                    author = msg.get('author', {})
                    author_name = author.get('username', '').lower()
                    # Check if it's the OwO bot
                    if 'owo' in author_name or 'owobot' in author_name:
                        self.owo_bot_name = author.get('username')
                        logger.info(f"✅ Found OwO bot: {self.owo_bot_name}")
                        return
                
                # If not found, use default
                self.owo_bot_name = "OwO"
                logger.info("ℹ️ Using default OwO bot name: OwO")
                
        except Exception as e:
            logger.warning(f"Could not find OwO bot: {e}")
            self.owo_bot_name = "OwO"

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
        """✅ FIXED: Send a command and check for OwO bot response"""
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
                logger.info(f"✅ Command sent: {command}")
                message_data = response.json()
                
                # ✅ ADD THIS: Wait for OwO bot to respond
                logger.info("⏳ Waiting for OwO bot response...")
                time.sleep(3)  # Give OwO bot time to respond
                
                # ✅ ADD THIS: Check if OwO bot responded
                owo_response = self.check_owo_response(command)
                
                if owo_response:
                    logger.info(f"🤖 OwO bot responded!")
                    logger.info(f"📝 Response: {owo_response[:200]}")
                else:
                    logger.warning("⚠️ No OwO bot response detected")
                    logger.info("💡 Make sure OwO bot is online in the server!")
                    logger.info("💡 Also check if the bot has 'Read Message History' permission")
                
                return {
                    "success": True, 
                    "response": message_data,
                    "owo_responded": owo_response is not None,
                    "owo_response": owo_response
                }
                
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

    def check_owo_response(self, command: str) -> Optional[str]:
        """✅ ADD THIS: Check if OwO bot responded to the command"""
        try:
            # Get recent messages
            url = f"{self.base_url}/channels/{self.channel_id}/messages"
            params = {"limit": 10}  # Get last 10 messages
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                messages = response.json()
                
                # Look for OwO bot's response
                for msg in messages:
                    author = msg.get('author', {})
                    author_name = author.get('username', '').lower()
                    
                    # Check if it's the OwO bot
                    if 'owo' in author_name or 'owobot' in author_name:
                        # Get the message content
                        content = msg.get('content', '')
                        
                        # Check if it's a response to our command
                        # OwO bot responses typically contain the command or a reaction
                        if content and len(content) > 0:
                            # Make sure it's not our own message
                            if content != command:
                                # Additional check: OwO bot responses often have specific formatting
                                # Example: "You found a Deer! (+150 coins)"
                                if 'owo' not in content.lower() or 'hunt' in content.lower() or 'work' in content.lower():
                                    return content
                        
                        # Also check for embeds (OwO bot often uses embeds)
                        embeds = msg.get('embeds', [])
                        if embeds:
                            embed_desc = embeds[0].get('description', '')
                            if embed_desc:
                                return embed_desc
                
                return None
                
            else:
                logger.warning(f"Could not get messages: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error checking OwO response: {e}")
            return None

    def get_owo_bot_messages(self, limit: int = 5) -> List[Dict]:
        """✅ ADD THIS: Get recent OwO bot messages"""
        try:
            messages = self.get_message_history(limit * 2)  # Get extra to filter
            if not messages:
                return []
            
            owo_messages = []
            for msg in messages:
                author = msg.get('author', {})
                author_name = author.get('username', '').lower()
                if 'owo' in author_name:
                    owo_messages.append(msg)
                    
                    if len(owo_messages) >= limit:
                        break
            
            return owo_messages
            
        except Exception as e:
            logger.error(f"Error getting OwO messages: {e}")
            return []

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
