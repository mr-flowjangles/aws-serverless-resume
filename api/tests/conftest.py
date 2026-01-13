"""
Pytest configuration for testing shared handlers.
"""
import sys
import os

# Add the parent directory to Python path so we can import shared
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
