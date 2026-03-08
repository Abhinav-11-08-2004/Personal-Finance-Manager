"""
main.py - Entry point for the Personal Finance Manager.

Run this file to start the application:
    python main.py
"""

import sys
import os

# Add src/ to the Python path so all modules can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from menu import main_menu


if __name__ == "__main__":
    main_menu()
