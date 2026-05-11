import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edudata.settings')
django.setup()

from django.urls import path, include
from edudata import urls as main_urls

print("Все URL endpoints бекенда:\n")

def show_urls(url_patterns, prefix=''):
    for pattern in url_patterns:
        pattern_str = str(pattern.pattern)
        full_pattern = prefix + pattern_str
        if hasattr(pattern, 'url_patterns'):
            show_urls(pattern.url_patterns, full_pattern)
        else:
            view = pattern.callback
            if hasattr(view, 'cls'):
                # ViewSet
                view_name = view.cls.__name__
                if hasattr(view, 'actions'):
                    actions = ', '.join(view.actions.keys())
                    print(f"  {full_pattern:<40} -> {view_name} ({actions})")
                else:
                    print(f"  {full_pattern:<40} -> {view_name}")
            else:
                # Функция или класс
                view_name = getattr(view, '__name__', str(view))
                print(f"  {full_pattern:<40} -> {view_name}")

show_urls(main_urls.urlpatterns)
