#!/usr/bin/env python3
"""
Slow OwO Bot Test (With Proper Delays)
Run: python test_owo_slow.py
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def test_command(command, wait_before=0):
    """Test a single command with delay"""
    if wait_before > 0:
        print(f"⏰ Waiting {wait_before} seconds before next command...")
        time.sleep(wait_before)
    
    print(f"\n📤 Testing: {command}")
    
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": command}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✅ Sent: {command}")
            
            # Wait for OwO bot
            print("⏳ Waiting for OwO bot (5 seconds)...")
            time.sleep(5)
            
            # Check for response
            messages_url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
            params = {"limit": 5}
            msgs = requests.get(messages_url, headers=headers, params=params)
            
            if msgs.status_code == 200:
                found_response = False
                for msg in msgs.json():
                    author = msg.get('author', {}).get('username', '')
                    if 'OwO' in author or 'owo' in author.lower():
                        content = msg.get('content', '')
                        if content and content != command:
                            print(f"🤖 OwO replied: {content[:100]}")
                            found_response = True
                            break
                
                if not found_response:
                    print("⚠️ No response from OwO bot yet")
                    print("   (It might be processing or rate limited)")
                return True
            else:
                print(f"❌ Failed to get messages: {msgs.status_code}")
                return False
                
        elif response.status_code == 429:
            retry_after = response.json().get('retry_after', 10)
            print(f"⏰ Rate limited! Waiting {retry_after} seconds...")
            time.sleep(retry_after)
            # Retry
            return test_command(command, 0)
            
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Test commands with delays
print("🧪 Testing OwO Bot Commands (Slow Mode)")
print("=" * 50)
print("⚠️  WAITING 15 SECONDS BEFORE FIRST COMMAND...")
time.sleep(15)

commands = [
    "owo help",
    "owo bal",
    "owo hunt",
    "owo work",
]

for i, cmd in enumerate(commands):
    # Wait between commands (increasing wait time)
    wait_time = 15 + (i * 5)  # 15s, 20s, 25s, 30s
    success = test_command(cmd, wait_time)
    
    if not success:
        print(f"❌ Command failed: {cmd}")
        break

print("\n" + "=" * 50)
print("✅ Test complete!")
