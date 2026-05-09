#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)
    
    # Now run the actual manage.py
    from django.core.management import execute_from_command_line
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
    execute_from_command_line(sys.argv)