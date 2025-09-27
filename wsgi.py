#!/usr/bin/env python3
"""
BiScheduler WSGI Application
"""
import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.app import create_app

# Create application
application = create_app('development')

# Add URL routing support for /bischeduler prefix
class PrefixMiddleware:
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        # Remove the prefix from PATH_INFO if present
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
        elif environ['PATH_INFO'] == self.prefix:
            environ['PATH_INFO'] = '/'
            environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)

# Apply prefix middleware
application = PrefixMiddleware(application, '/bischeduler')

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5005, application, use_reloader=True, use_debugger=True)