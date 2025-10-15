#!/usr/bin/env python3
"""
Configuration file for TikTok to Facebook Automation App
Contains file paths, credentials, and other settings
"""

import os

# Application Settings
APP_TITLE = "TikTok to Facebook Otomasyonu"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create directories if they don't exist
for directory in [DOWNLOADS_DIR, LOGS_DIR, DATA_DIR]:
    os.makedirs(directory, exist_ok=True)

# Browser Settings
BROWSER_HEADLESS = False  # Set to True for headless mode
BROWSER_TIMEOUT = 30  # seconds

# TikTok Settings
TIKTOK_DOWNLOAD_TIMEOUT = 60  # seconds

# Facebook Settings
FACEBOOK_LOGIN_TIMEOUT = 30  # seconds
FACEBOOK_UPLOAD_TIMEOUT = 120  # seconds

# Gemini API Settings (to be configured by user)
GEMINI_API_KEY = ""  # User needs to set this
GEMINI_MODEL = "gemini-pro"

# Logging Settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

# UI Settings
STATUS_LOG_MAX_LINES = 1000
BUTTON_STYLES = {
    "primary": """
        QPushButton {
            background-color: #1877f2;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            padding: 10px 20px;
        }
        QPushButton:hover {
            background-color: #166fe5;
        }
        QPushButton:pressed {
            background-color: #1460d1;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """,
    "secondary": """
        QPushButton {
            background-color: #42b883;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #369870;
        }
        QPushButton:pressed {
            background-color: #2d7a5a;
        }
    """
}
