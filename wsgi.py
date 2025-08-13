#!/usr/bin/env python3
"""
WSGI configuration for PythonAnywhere deployment.

This file is used by PythonAnywhere to serve your Flask application.
"""

import sys
import os

# Add your project directory to the Python path
path = '/home/yourusername/svg-to-animated-lottie'
if path not in sys.path:
    sys.path.insert(0, path)

# Import your Flask app
from app import app as application

if __name__ == "__main__":
    application.run()
