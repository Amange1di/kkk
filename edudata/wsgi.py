import os

from ._backend_path import add_backend_to_path

add_backend_to_path()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edudata.settings")

application = get_wsgi_application()
