from django.contrib import admin
from django.views.static import serve
from django.http import Http404


def custom_serve(request, path, document_root=None, show_indexes=False):
    excluded_directories = ['protected', 'datasets', 'tokenizers', 'models', ]

    normalized_path = path.lstrip('/')
    for directory in excluded_directories:
        if normalized_path.startswith(directory + '/'):
            # Exclude the directory from being served
            raise Http404('File not found')

    # Call the original serve function to serve the media file
    return serve(request, path, document_root, show_indexes)