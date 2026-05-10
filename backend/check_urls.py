import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver,.onrender.com')
django.setup()

from django.urls import get_resolver

def show_urls(url_pattern, indent=0):
    for pattern in url_pattern.url_patterns:
        print(" " * indent + str(pattern.pattern))
        if hasattr(pattern, 'url_patterns'):
            show_urls(pattern, indent + 2)

from edudata import urls
print("All URLs:")
show_urls(get_resolver())
