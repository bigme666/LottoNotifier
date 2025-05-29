#!/usr/bin/env python3
"""
Test script to verify telegram library imports
"""

try:
    print("Testing python-telegram-bot imports...")
    
    # Test basic imports
    import telegram
    print(f"✓ telegram module imported successfully")
    print(f"  telegram version: {telegram.__version__ if hasattr(telegram, '__version__') else 'unknown'}")
    
    # Test specific imports
    from telegram import Update
    print("✓ Update imported successfully")
    
    from telegram.ext import Application, CommandHandler, ContextTypes
    print("✓ telegram.ext imports successful")
    
    try:
        from telegram.constants import ParseMode
        print("✓ ParseMode imported from constants")
    except ImportError:
        from telegram import ParseMode
        print("✓ ParseMode imported from telegram")
    
    print("\n✅ All imports successful! The bot should work.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nTrying to diagnose the issue...")
    
    try:
        import telegram
        print(f"telegram module path: {telegram.__file__}")
        print(f"telegram attributes: {dir(telegram)}")
    except Exception as ex:
        print(f"Failed to import telegram: {ex}")

except Exception as e:
    print(f"❌ Unexpected error: {e}")