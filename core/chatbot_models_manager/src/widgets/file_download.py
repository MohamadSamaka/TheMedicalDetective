from django import forms
from django.utils.html import format_html
from django.urls import reverse


class FileDownloadWidget(forms.widgets.FileInput):
    def __init__(self, file, model_name, attrs=None):
        self.file = file
        self.model_name = model_name
        super().__init__(attrs)
    def render(self, name, value, attrs=None, renderer=None):
        from pathlib import Path
        if self.file:
            file_name = str(self.file)
            file_path = f'{self.model_name}/{self.file}'
            file_url = reverse('adminpage-admin:protected-media', kwargs={'file_path': file_path})
            print("protected:", file_url)
            download_link = format_html(f'<a href="{file_url}" download="{file_name}">{file_name}</a>')            
            return download_link
        else:
            return 'File is missing!'