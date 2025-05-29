#!/usr/bin/env python3
"""
Test script to check telegram imports and available modules.
"""

def test_telegram_imports():
    """Test different ways to import telegram modules."""
    
    try:
        import telegram
        print("✓ telegram module imported successfully")
        print(f"telegram module file: {telegram.__file__}")
        print(f"telegram module dir: {dir(telegram)}")
    except ImportError as e:
        print(f"✗ Failed to import telegram: {e}")
    
    try:
        from telegram import Update
        print("✓ Update imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Update: {e}")
    
    try:
        from telegram.ext import Application, CommandHandler
        print("✓ Application and CommandHandler imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Application/CommandHandler: {e}")
    
    try:
        import telegram.ext
        print(f"✓ telegram.ext available: {dir(telegram.ext)}")
    except ImportError as e:
        print(f"✗ Failed to import telegram.ext: {e}")

if __name__ == "__main__":
    test_telegram_imports()