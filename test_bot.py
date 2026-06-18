#!/usr/bin/env python3
"""
Complete Bot Test Script
Run: python test_bot.py
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Test 1: Check environment variables
print("=" * 50)
print("🔍 TEST 1: Environment Variables")
print("=" * 50)

token = os.getenv('DISCORD_TOKEN')
channel = os.getenv('CHANNEL_ID')

print(f"✅ Token present: {'Yes' if token else 'No'}")
print(f"✅ Channel ID: {channel}")
print(f"✅ Token length: {len(token) if token else 0}")

# Test 2: Test Discord API
print("\n" + "=" * 50)
print("🔍 TEST 2: Discord API Connection")
print("=" * 50)

from core.discord_api import DiscordAPI

api = DiscordAPI()
result = api.send_command("🧪 Test message from test script!")
print(f"✅ Result: {result}")

# Test 3: Test Bot Initialization
print("\n" + "=" * 50)
print("🔍 TEST 3: Bot Initialization")
print("=" * 50)

try:
    from main import OWOBot
    bot = OWOBot()
    print("✅ Bot initialized successfully!")
    print(f"✅ Bot active: {bot.active}")
except Exception as e:
    print(f"❌ Bot initialization failed: {e}")

# Test 4: Test Schedule
print("\n" + "=" * 50)
print("🔍 TEST 4: Schedule Manager")
print("=" * 50)

from core.schedule_manager import ScheduleManager
import json

with open('config.json', 'r') as f:
    config = json.load(f)

schedule = ScheduleManager(config)
start, end = schedule.get_today_schedule()

if start and end:
    print(f"✅ Schedule found!")
    print(f"   Start: {start.strftime('%H:%M')}")
    print(f"   End: {end.strftime('%H:%M')}")
    print(f"   Active: {schedule.is_active()}")
else:
    print("❌ No schedule found")

print("\n✅ ALL TESTS COMPLETE!")
