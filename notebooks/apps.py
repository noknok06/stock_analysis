# notebooks/apps.py
from django.apps import AppConfig

class NotebooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notebooks'
    verbose_name = 'ノートブック'