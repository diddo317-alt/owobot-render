#!/usr/bin/env python3
"""
Test OwO Bot Response
Run: python test_owo_response.py
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.discord_api import DiscordAPI

def test_owo_response():
    """Test if OwO bot responds to commands"""
    print("🧪 Testing OwO Bot Response")
    print("=" * 50)
    
    api = DiscordAPI()
    
    # Test commands
    test_commands = [
        "owo bal",
        "owo hunt",
        "owo work",
    ]
    
    for cmd in test_commands:
        print(f"\n📤 Testing: {cmd}")
        result = api.send_command(cmd)
        
        if result.get('success'):
            print(f"✅ Command sent successfully")
            if result.get('owo_responded'):
                print(f"🤖 OwO bot responded: {result.get('owo_response', '')[:100]}")
            else:
                print(f"⚠️ No OwO bot response detected")
                print(f"   💡 Make sure OwO bot is online in the server")
                print(f"   💡 Check if bot has 'Read Message History' permission")
        else:
            print(f"❌ Failed to send command: {result.get('error')}")
        
        time.sleep(3)  # Wait between tests
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")

if __name__ == "__main__":
    test_owo_response()
