#!/usr/bin/python3
"""
WSGI configuration for AkriOnline project on GoDaddy cPanel.

This file is used by cPanel's Python app hosting to serve the Django application.
Place this file in your domain's root directory (public_html).
"""

import sys
import os

# Add your project directory to the Python path
# Adjust this path based on where you upload your Django project
project_path = os.path.dirname(__file__)
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Set the Django settings module for production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akrionline.production_settings')

# Import Django's WSGI application
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except ImportError:
    # Fallback for debugging
    import traceback
    traceback.print_exc()
    
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [b'Django import error. Check your Python path and dependencies.']

# For debugging purposes (remove in production)
# Uncomment the following lines if you need to debug import issues
"""
def application(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    
    debug_info = f'''
    Python Path: {sys.path}
    Environment: {dict(environ)}
    Current Directory: {os.getcwd()}
    Project Path: {project_path}
    '''
    
    return [debug_info.encode('utf-8')]
"""
