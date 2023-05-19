from django.apps import apps
from .models import City
from ..myAdmin.views import my_admin_site

my_admin_site.register(City)





# my_admin_site.register(CustomUserManager)
# my_admin_site.register(CustomUser)

# Register your models here.
# for app_config in apps.get_app_configs():
#     for model in app_config.get_models():
#         if not admin.site.is_registered(model):
#             print("not registered")
#             admin.site.register(model)
#         else:
#             print("already registered")




            
        # if admin.site.is_registered(model):
        #     admin.site.unregister(model)

            

# admin.site.register(CustomUser)
