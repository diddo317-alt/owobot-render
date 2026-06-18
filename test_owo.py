#!/usr/bin/env python3
"""
Simple OwO Bot Test
Run: python test_owo.py
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def test_command(command):
    """Test a single command"""
    print(f"\n📤 Testing: {command}")
    
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": command}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Sent: {command}")
        
        # Wait for OwO bot
        print("⏳ Waiting for OwO bot...")
        time.sleep(3)
        
        # Check for response
        messages_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
        params = {"limit": 5}
        msgs = requests.get(messages_url, headers=headers, params=params)
        
        if msgs.status_code == 200:
            for msg in msgs.json():
                author = msg.get('author', {}).get('username', '')
                if 'OwO' in author or 'owo' in author.lower():
                    content = msg.get('content', '')
                    if content and content != command:
                        print(f"🤖 OwO replied: {content[:100]}")
                        return True
        
        print("⚠️ No response from OwO bot")
        return False
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

# Test commands
print("🧪 Testing OwO Bot Commands")
print("=" * 40)

commands = [
    "owo help",      # Should respond with help
    "owo bal",       # Check balance
    "owo hunt",      # Hunt
    "owo work",      # Work
]

for cmd in commands:
    test_command(cmd)
    time.sleep(2)

print("\n" + "=" * 40)
print("✅ Test complete!")
