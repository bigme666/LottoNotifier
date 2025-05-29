#!/usr/bin/env python3
import sys
import importlib.util

def test_telegram_imports():
    """Test telegram imports step by step"""
    
    # Test if python-telegram-bot is properly installed
    spec = importlib.util.find_spec("telegram")
    if spec is None:
        print("❌ telegram module not found")
        return False
    
    print(f"✓ telegram module found at: {spec.origin}")
    
    try:
        import telegram
        print(f"✓ telegram imported successfully")
        print(f"✓ telegram location: {telegram.__file__}")
        print(f"✓ telegram attributes: {[attr for attr in dir(telegram) if not attr.startswith('_')][:10]}")
        
        # Test specific imports
        from telegram import Update
        print("✓ Update imported")
        
        from telegram.ext import Application, CommandHandler, ContextTypes
        print("✓ telegram.ext imports successful")
        
        from telegram.constants import ParseMode
        print("✓ ParseMode imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_telegram_imports()
    sys.exit(0 if success else 1)