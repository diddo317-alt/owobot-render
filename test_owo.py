#!/usr/bin/env python3
"""
Test OwO#8456 Response
Run: python test_owo.py
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.discord_api import DiscordAPI

def test_owo_commands():
    """Test if OwO#8456 responds to commands"""
    print("🧪 Testing OwO#8456 Response")
    print("=" * 50)
    print("🤖 Your bot: wowrender#5034")
    print("🎯 Target: OwO#8456")
    print("=" * 50)
    
    api = DiscordAPI()
    
    # Test commands that OwO#8456 responds to
    commands = [
        "owo bal",      # Check balance
        "owo hunt",     # Hunt
        "owo work",     # Work
    ]
    
    for cmd in commands:
        print(f"\n📤 Testing: {cmd}")
        result = api.send_command(cmd)
        
        if result.get('success'):
            print(f"✅ Command sent successfully!")
            if result.get('owo_responded'):
                print(f"✅ OwO#8456 responded!")
                print(f"📝 Response: {result.get('owo_response', '')[:100]}")
            else:
                print(f"⚠️ OwO#8456 didn't respond yet")
                print(f"   💡 Make sure OwO#8456 is online")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        time.sleep(3)
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")

if __name__ == "__main__":
    test_owo_commands()
