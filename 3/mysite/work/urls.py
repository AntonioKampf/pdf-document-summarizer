from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('project_print/', project_view, name='project_view'),
    path('upload/', upload_file, name='upload_file'),
    path('delete/<int:file_id>/', delete_file, name='delete_file'),
    path('download_file/<int:file_id>/', download_file, name='download_file'),
    path('help_text/', help_text, name='help_text'),
    path('output_summarazy/<int:file_id>/', output_summarazy, name='output_summarazy'),
    path('print_summarazy/<int:file_id>/', print_summarazy, name='print_summarazy'),
    path('output_summarazy_txt/<int:file_id>/', output_summarazy_txt, name='output_summarazy_txt')
]
