#!/usr/bin/env python3
"""
BiScheduler Application Runner with URL Prefix Support
"""

import os
import sys
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.app import create_app

# Create the main app
app = create_app('development')

# Create a simple app for the root
def simple_app(environ, start_response):
    status = '404 Not Found'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'Not Found']

# Use dispatcher middleware to handle /bischeduler prefix
application = DispatcherMiddleware(simple_app, {
    '/bischeduler': app
})

if __name__ == '__main__':
    # Run with URL prefix support
    run_simple('0.0.0.0', 5005, application,
               use_reloader=True,
               use_debugger=True,
               threaded=True)