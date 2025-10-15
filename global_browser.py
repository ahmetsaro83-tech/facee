#!/usr/bin/env python3
"""
Global Browser Instance - Simple persistent browser management
"""

# Global browser instance
_browser_instance = None
_browser_active = False

def set_browser(sb_instance):
    """Set the global browser instance"""
    global _browser_instance, _browser_active
    _browser_instance = sb_instance
    _browser_active = True

def get_browser():
    """Get the global browser instance"""
    global _browser_instance, _browser_active
    if _browser_active and _browser_instance:
        try:
            # Test if browser is still alive
            _browser_instance.cdp.get_current_url()
            return _browser_instance
        except:
            _browser_active = False
            _browser_instance = None
    return None

def clear_browser():
    """Clear the global browser instance"""
    global _browser_instance, _browser_active
    _browser_instance = None
    _browser_active = False

def is_browser_active():
    """Check if browser is active"""
    return _browser_active and _browser_instance is not None