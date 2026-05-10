import os

from ._backend_path import add_backend_to_path

add_backend_to_path()

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edudata.settings")

application = get_asgi_application()
