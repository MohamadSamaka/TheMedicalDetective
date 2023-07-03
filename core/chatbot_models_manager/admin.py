from core.my_admin.admin import my_admin_site
from .src.admin_pages.diagnoser_admin import DiagnoserAdmin
from .src.admin_pages.ner_admin import NERAdmin
from .models import Diagnoser, NER

my_admin_site.register(Diagnoser, DiagnoserAdmin)
my_admin_site.register(NER, NERAdmin)