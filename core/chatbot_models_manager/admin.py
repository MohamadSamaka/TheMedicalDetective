from core.my_admin.admin import my_admin_site
from .src.admin_pages.diagnoser_admin import DiagnoserAdmin
from .models import Diagnoser

my_admin_site.register(Diagnoser, DiagnoserAdmin)
# my_admin_site.register(NER)