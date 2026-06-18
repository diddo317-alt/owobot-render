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
        
        # ✅ Your OwO bot name
        self.owo_bot_name = "OwO#8456"
        self.my_bot_name = "wowrender#5034"
        
        self.max_retries = 3
        self.retry_delay = 5
        
        # ✅ Webhook mode - this makes OwO#8456 respond!
        self.use_webhook = True
        logger.info(f"✅ Using Webhook mode - {self.owo_bot_name} will respond!")
        logger.info(f"✅ Bot name: {self.my_bot_name}")
        
        # Set bot presence/status
        self.set_presence()
        self.find_owo_bot()

    def find_owo_bot(self):
        """Find the OwO bot in the channel"""
        try:
            messages = self.get_message_history(50)
            if messages:
                for msg in messages:
                    author = msg.get('author', {})
                    author_name = author.get('username', '')
                    # Check if it's the OwO bot
                    if 'OwO' in author_name or 'owo' in author_name.lower():
                        self.owo_bot_name = author_name
                        logger.info(f"✅ Found {self.owo_bot_name} in channel!")
                        return
                
                logger.info(f"✅ Using known OwO bot: {self.owo_bot_name}")
                
        except Exception as e:
            logger.warning(f"Could not find OwO bot: {e}")

    def set_presence(self, status="online", activity_name="OwO hunting 🐱", activity_type=0):
        """Set bot presence/status"""
        try:
            gateway_url = f"{self.base_url}/gateway/bot"
            response = requests.get(gateway_url, headers=self.headers)
            
            if response.status_code == 200:
                gateway_data = response.json()
                logger.info(f"✅ Gateway connected: {gateway_data.get('url')}")
                logger.info(f"🎯 Bot presence: {status} - {activity_type}: {activity_name}")
                
                # Send status message via webhook
                self.send_status_message()
                
            else:
                logger.warning(f"Could not connect to gateway: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Could not set presence: {e}")

    def send_status_message(self):
        """Send a status message via webhook"""
        try:
            if self.webhook_url:
                payload = {
                    "content": f"🟢 {self.my_bot_name} is online! Ready to talk to {self.owo_bot_name}!",
                    "username": "wowrender",
                    "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"
                }
                
                response = requests.post(self.webhook_url, json=payload)
                
                if response.status_code == 204:
                    logger.info(f"✅ Status message sent - {self.my_bot_name} is online!")
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
        """Send command via webhook - OwO#8456 will respond to this!"""
        try:
            payload = {
                "content": command,
                "username": "wowrender",  # This is your bot's name in chat
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"
            }
            
            response = requests.post(self.webhook_url, json=payload)
            self.last_command_time = time.time()
            
            if response.status_code == 204:  # Webhook success
                logger.info(f"✅ Command sent via webhook: {command}")
                logger.info(f"📤 Sent as: wowrender (user-like)")
                
                # Wait for OwO#8456 to respond
                logger.info(f"⏳ Waiting for {self.owo_bot_name} to respond...")
                time.sleep(5)
                
                # Check if OwO#8456 responded
                owo_response = self.check_owo_response(command)
                
                if owo_response:
                    logger.info(f"🤖 {self.owo_bot_name} responded!")
                    logger.info(f"📝 Response: {owo_response[:200]}")
                    return {
                        "success": True,
                        "owo_responded": True,
                        "owo_response": owo_response,
                        "message": f"✅ {self.owo_bot_name} responded!"
                    }
                else:
                    logger.warning(f"⚠️ No response from {self.owo_bot_name}")
                    logger.info(f"💡 Make sure {self.owo_bot_name} is online!")
                    return {
                        "success": True,
                        "owo_responded": False,
                        "owo_response": None,
                        "message": f"⚠️ {self.owo_bot_name} didn't respond"
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
        """Check if OwO#8456 responded to the command"""
        try:
            # Get recent messages
            url = f"{self.base_url}/channels/{self.channel_id}/messages"
            params = {"limit": 10}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                messages = response.json()
                
                # Look for OwO#8456's response
                for msg in messages:
                    author = msg.get('author', {})
                    author_name = author.get('username', '')
                    
                    # Check if it's OwO#8456
                    if 'OwO' in author_name:
                        content = msg.get('content', '')
                        
                        # Skip our own messages
                        if content and content != command:
                            # This is OwO#8456's response!
                            return content
                        
                        # Check embeds
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
