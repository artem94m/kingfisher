from django.core.files.storage import default_storage
from django.core.files.base import File

def handle_upload(request):
    files = request.FILES
    for f in files.values():
        path = default_storage.save('upload/', File(f))