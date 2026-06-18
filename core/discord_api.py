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
        # ✅ YOUR WEBHOOK URL
        self.webhook_url = "https://discord.com/api/webhooks/1517291484229931088/AYocNg663jfym1NrYzUoW15qeCcWJEBSJDhW395XpBtbepCt2SbNAZw39JCw4itHCIXf"
        self.base_url = "https://discord.com/api/v9"
        self.headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json"
        }
        self.last_command_time = 0
        self.min_command_interval = 10  # 10 seconds between commands
        self.owo_bot_name = None
        self.max_retries = 3
        self.retry_delay = 5
        
        # ✅ Always use webhook mode
        self.use_webhook = True
        logger.info("✅ Using Webhook mode (messages appear as user - OwO bot will respond!)")
        
        # Set bot presence/status on initialization
        self.set_presence()
        self.find_owo_bot()

    def find_owo_bot(self):
        """Find the OwO bot in the channel"""
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
            if self.webhook_url:
                payload = {
                    "content": "🟢 Bot is online and ready! (Webhook Mode)",
                    "username": "OwO Helper",
                    "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"
                }
                
                response = requests.post(self.webhook_url, json=payload)
                
                if response.status_code == 204:
                    logger.info("✅ Status message sent - bot is online!")
                else:
                    logger.warning(f"Could not send status message: {response.status_code}")
                    
        except Exception as e:
            logger.warning(f"Could not send status message: {e}")

    def send_command(self, command: str) -> Dict[str, Any]:
        """Send a command using webhook (appears as user-like message)"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_command_time
            
            if time_since_last < self.min_command_interval:
                wait_time = self.min_command_interval - time_since_last
                logger.info(f"⏰ Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)

            # ✅ SEND VIA WEBHOOK
            return self.send_via_webhook(command)
                
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return {"success": False, "error": str(e)}

    def send_via_webhook(self, command: str) -> Dict[str, Any]:
        """Send command via webhook (appears as user-like message)"""
        try:
            payload = {
                "content": command,
                "username": "OwO Helper",  # Custom name that appears in Discord
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"  # Custom avatar
            }
            
            response = requests.post(self.webhook_url, json=payload)
            self.last_command_time = time.time()
            
            if response.status_code == 204:  # Webhook success (no content returned)
                logger.info(f"✅ Command sent via webhook: {command}")
                
                # Wait for OwO bot to respond
                logger.info("⏳ Waiting for OwO bot response (5 seconds)...")
                time.sleep(5)
                
                # Check if OwO bot responded
                owo_response = self.check_owo_response(command)
                
                if owo_response:
                    logger.info(f"🤖 OwO bot responded!")
                    logger.info(f"📝 Response: {owo_response[:200]}")
                    return {
                        "success": True,
                        "owo_responded": True,
                        "owo_response": owo_response
                    }
                else:
                    logger.warning("⚠️ No OwO bot response detected")
                    logger.info("💡 Make sure OwO bot is online in the server!")
                    return {
                        "success": True,
                        "owo_responded": False,
                        "owo_response": None
                    }
                    
            elif response.status_code == 429:
                # Rate limited
                try:
                    retry_after = response.json().get('retry_after', 10)
                except:
                    retry_after = 10
                
                logger.warning(f"⏰ Rate limited! Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                
                # Retry
                return self.send_via_webhook(command)
                
            else:
                logger.error(f"Webhook error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {"success": False, "error": f"Webhook error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {"success": False, "error": str(e)}

    def check_owo_response(self, command: str) -> Optional[str]:
        """Check if OwO bot responded to the command"""
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
                        if content and len(content) > 0:
                            # Make sure it's not our own message
                            if content != command:
                                # OwO bot responses typically contain specific keywords
                                keywords = ['coins', 'found', 'earned', 'balance', 'slot', 'hunt', 'work', 'you', 'have']
                                if any(keyword in content.lower() for keyword in keywords):
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

    def wait_for_owo_response(self, timeout: int = 10) -> Optional[str]:
        """Wait for OwO bot to respond"""
        try:
            start_time = time.time()
            last_messages = self.get_message_history(5)
            
            while time.time() - start_time < timeout:
                time.sleep(2)
                current_messages = self.get_message_history(5)
                
                if current_messages:
                    # Check for new messages from OwO bot
                    for msg in current_messages:
                        author = msg.get('author', {})
                        author_name = author.get('username', '').lower()
                        
                        if 'owo' in author_name:
                            # Check if this message wasn't in the last check
                            if msg not in last_messages:
                                content = msg.get('content', '')
                                if content:
                                    return content
                    
                    last_messages = current_messages
            
            return None
            
        except Exception as e:
            logger.error(f"Error waiting for OwO response: {e}")
            return None

    def is_owo_bot_online(self) -> bool:
        """Check if OwO bot is online in the server"""
        try:
            messages = self.get_message_history(10)
            if messages:
                for msg in messages:
                    author = msg.get('author', {})
                    author_name = author.get('username', '').lower()
                    if 'owo' in author_name:
                        return True
            
            # Alternative: Check if OwO bot has sent any message recently
            owo_messages = self.get_owo_bot_messages(1)
            return len(owo_messages) > 0
            
        except Exception as e:
            logger.error(f"Error checking OwO bot status: {e}")
            return False

    def get_owo_bot_messages(self, limit: int = 5) -> List[Dict]:
        """Get recent OwO bot messages"""
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
