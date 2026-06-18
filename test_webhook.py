#!/usr/bin/env python3
"""
Test Webhook Connection with Your Webhook URL
Run: python test_webhook.py
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ✅ YOUR WEBHOOK URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1517291484229931088/AYocNg663jfym1NrYzUoW15qeCcWJEBSJDhW395XpBtbepCt2SbNAZw39JCw4itHCIXf"
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def test_webhook():
    """Test sending via webhook"""
    print("🧪 Testing Webhook Connection")
    print("=" * 50)
    
    print(f"✅ Webhook URL: {WEBHOOK_URL[:60]}...")
    
    # Test 1: Send a test message
    print("\n📤 Test 1: Sending test message via webhook...")
    
    payload = {
        "content": "🧪 Test message from webhook! OwO bot should see this!",
        "username": "OwO Tester",
        "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print("✅ Test message sent successfully!")
            print("📤 Check your Discord channel!")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Send an OwO command
    print("\n📤 Test 2: Sending OwO command via webhook...")
    time.sleep(3)
    
    command = "owo cash"
    payload = {
        "content": command,
        "username": "OwO Helper",
        "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print(f"✅ Command sent: {command}")
            print("⏳ Waiting for OwO bot response (5 seconds)...")
            time.sleep(5)
            print("📤 Check Discord for OwO bot response!")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_direct_bot():
    """Test direct bot message (for comparison)"""
    print("\n" + "=" * 50)
    print("📤 Test 3: Sending via bot token (for comparison)...")
    
    if not TOKEN or not CHANNEL_ID:
        print("❌ No token or channel ID found!")
        return
    
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": "🧪 Test from bot token (may not trigger OwO bot)"}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Bot token message sent!")
            print("💡 Compare: Webhook messages appear as user, bot messages appear as bot")
        else:
            print(f"❌ Bot token failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Webhook Test Tool")
    print("Your Webhook URL is configured!")
    print()
    
    test_webhook()
    test_direct_bot()
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("\n💡 IMPORTANT:")
    print("   - Webhook messages appear as a USER (OwO bot will respond)")
    print("   - Bot token messages appear as a BOT (OwO bot may ignore)")
    print("   - Your bot is now using WEBHOOK mode!")
