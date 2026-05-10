from ._backend_path import add_backend_to_path

add_backend_to_path()

from backend.edudata.urls import *  # noqa: F401,F403
