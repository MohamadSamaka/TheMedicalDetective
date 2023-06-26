from django.contrib import admin
import django.contrib.admin.options as op
from django.http import JsonResponse
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.conf import settings
from django.urls import reverse, reverse_lazy 
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import path
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.admin.utils import unquote
from django.core.files import File
from .models import * 
from core.my_admin.admin import my_admin_site
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
from django.db.utils import IntegrityError
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class CustomJsonResponse(JsonResponse):
    def __init__(self, redirect_response, additional_data=None, **kwargs):
        data = {
            'redirect_url': redirect_response.url,
            'additional_data': additional_data,
        }
        super().__init__(data, **kwargs)



    # change_fieldsets = (
    #     (None, {
    #         'fields': ('neurons_first_layer', 'neurons_second_layer'),
    #         # 'fields': ('neurons_first_layer', 'neurons_second_layer', 'training_file', 'testing_file'),
    #     }),
    # )
    # change_form_template = "admin/diagnoser/diagnoser_add.html"
    # form = CustomForm

class FileDownloadWidget(forms.widgets.FileInput):
    def __init__(self, file=None, attrs=None):
        self.file = file
        super().__init__(attrs)
    def render(self, name, value, attrs=None, renderer=None):
        from pathlib import Path
        if self.file:
            file_name = str(self.file)
            file_url = f"/admin/media/protected/{file_name}"
            print("protected:", file_url)
            download_link = format_html(f'<a href="{file_url}" download="{file_name}">{file_name}</a>')
            return download_link
        else:
            return 'File is missing!'


class DiagnoserInfoForm(forms.ModelForm):
    neurons_first_layer = forms.IntegerField(
        label="layer 1 # of neurons",
        initial=64,
        min_value= 64,
        
    )
    neurons_second_layer = forms.IntegerField(
        label="layer 2 # of neurons",
        initial=64,
        min_value= 64,
    )
    iterations = forms.IntegerField(
        label="# of iterations",
        initial=100,
        min_value= 100,
    )

    training_file = forms.FileField(
        label="Training file",
        required=True,
    )

    class Meta:
        model = Diagnoser
        fields = '__all__'  # Or specify the fields you want to include




class DiagnoserAdmin(admin.ModelAdmin):
    form = DiagnoserInfoForm

    def change_view(self, request, object_id, form_url='', extra_context=None):
        print("change view!")
        self.change_form_template = 'admin/diagnoser/diagnoser_change.html'
        # extra_context = extra_context or {}
        # print(extra_context)
        # extra_context['errors'] = None
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        self.change_form_template = "admin/diagnoser/diagnoser_add.html"
        extra_context = extra_context or {}
        extra_context['form'] = self.get_form(request)
        return super().add_view(request, form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('validate_diagnosis_form/', self.diagnoser_form_validator, name='diagnosis-form-validator'),
            path('train_diagnoser_model/', self.diagnoser_trainer, name="diagnoser-trainer")
        ]
        return my_urls + urls
    

    @transaction.atomic
    def process_model(self, form):
        try:
            print("trying to save model...")
            form.save()
            print(form)
            print("model saved successflly\nstart starining...")
            itrations = form.cleaned_data['iterations']
            layer1_neurons = form.cleaned_data['neurons_first_layer']
            layer2_neurons = form.cleaned_data['neurons_second_layer']
            self.diagnoser_trainer(itrations, layer1_neurons ,layer2_neurons)
        except IntegrityError as e:
            print("error accured")
            return 409

    
    def diagnoser_form_validator(self, request):
        from time import sleep
        status_code = 200
        if request.method == 'POST':
            form = self.form(request.POST, request.FILES)
            if form.is_valid():
                self.send_form_validation_result(1)
                status_code =  self.process_model(form)
            else:
                print("form is invalid")
                status_code = 400
        else:
            form = self.form()
            status_code = 405 #method is not allowed

        context = {
            'form': form,
        }
        sleep(1)
        return render(request, 'admin/diagnoser/diagnoser_add.html', context, status = status_code)
    
    def send_form_validation_result(self, validity):
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "train",
            {
                'type': 'form_validiation_result',
                'info': {
                    'validity': validity
                },
            }
    ) 
    

    def diagnoser_trainer(self, iterations, layer1_nuerons, layer2_neurons):
        import tempfile
        import threading
        from core.chatbot_models_manager.src.models.diagnoser import DiagnoserModel
        trainer = DiagnoserModel.Trainer(dense1_n_neurons=layer1_nuerons, dense2_n_neurons = layer2_neurons, iterations=iterations)
        trainer.train_model()
        # return HttpResponse("Training Done")

    # # @method_decorator(staff_member_required)
    # # def custom_add_view(self, request):
    # #     if request.method == 'POST':
    # #         pass
    # #         # Perform form submission
    # #         form_class = self.get_form(request)
    # #         form = form_class(request.POST)
    # #         if form.is_valid():
    # #             # Process the form data (e.g., save to database)
    # #             # form.save()
    # #             return JsonResponse({'success': True})
    # #         else:
    # #             print("invalid!")
    # #             error_html = render_to_string('admin/diagnoser/diagnoser_add.html', {'errors': form.errors})
    # #             return JsonResponse({'success': False, 'error_html': error_html})
    # #     else:
    # #         # Render the custom add form
    # #         context = self.admin_site.each_context(request)
    # #         return TemplateResponse(request, self.change_form_template, context)
    # #     return JsonResponse({'success': True})
        
    # def save_model(self, request, obj, form, change):
    #     print("*****inside model!!****")
    #     from pathlib import Path
    #     # print(form.cleaned_data)
    #     # print(form.cleaned_data["training_file"])
    #     # print(dir(form.cleaned_data["training_file"]))
    #     cleaned = form.cleaned_data
    #     model_name = cleaned["model_name"]
    #     try:
    #         Path(settings.PROTECTED_MEDIA_ABSOLUTE_URL/  Path(model_name)).mkdir(parents=True, exist_ok=False)
    #     except FileExistsError as e:
    #         print("error")
    #         messages.set_level(request, messages.ERROR)
    #         self.message_user(request, "File name already exist!", level=messages.ERROR)
    #         return e
    #     # super().save_model(request, obj, form, change)

    # def render_change_form(self, request, context, *args, **kwargs):
    #     print("**************!!!!!!!***********")
    #     # Custom logic before rendering the change form
    #     # Call the parent class's render_change_form method
    #     response = super().render_change_form(request, context, *args, **kwargs)
    #     print("resposne from render_change_form", response)
    #     # print(response.rendered_content)
    #     # print(dir(response))
    #     return response
        
    
    def get_form(self, request, obj=None, **kwargs):
        print("getting form!")
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["training_file"].widget = FileDownloadWidget(file="test.txt")
            # form.base_fields["testing_file"].widget = FileDownloadWidget(file="test.txt")
            # form.base_fields["training_file"].initial = obj.training_file.name
            form.base_fields["training_file"].required = False
            # form.base_fields["testing_file"].required = False
            form.base_fields["iterations"].disabled = True
            form.base_fields["neurons_first_layer"].disabled = True
            form.base_fields["neurons_second_layer"].disabled = True   
        else:
            form.base_fields["training_file"].required = True
            form.base_fields["iterations"].disabled = False
            # form.base_fields["testing_file"].required = True
            form.base_fields["neurons_first_layer"].disabled = False
            form.base_fields["neurons_second_layer"].disabled = False
            form.base_fields["training_file"].widget = forms.FileInput()
            # form.base_fields["testing_file"].widget = forms.FileInput()
        return form
    
    
    # def response_add(self, request, obj, post_url_continue=None):
    #     print("response_add")
    #     from django.http import HttpRequest, HttpResponse
    #     from django.template.loader import render_to_string

    #     # print("response_add!!!!")
    #     storage = messages.get_messages(request)
    #     # return HttpResponse("Success!")
    #     response = super().response_add(request, obj, post_url_continue)
    #     test = render(request, 'client/pages/home.html')
    #     # self.render_change_form()
    #     # print(dir(test))
    #     # print("content", test.content)
    #     print(response)
    #     # HttpResponseRedirect('/admin/chatbot_models_manager/diagnoser/')
    #     # print(response._content_type_for_repr)
    #     # json_response = JsonResponse({
    #     #     'page': response
    #     # })
    #     # print("content: ", response.content.decode('utf-8'))
    #     # print(dir(response))
    #     # print("response before:", response)
        
    #     # print(dir(response.serialize()))
    #     # json_response = CustomJsonResponse(response, additional_data={
    #     #     'hello':'world'
    #     # })

    #     # print("content1:", response.render().content.decode('utf-8'))
    #     # rendered_page = response.content.decode('utf-8')
    #     # print("renderd_page:", response.rendered_content)
    #     # print("previous status_code: ", response.status_code)
    #     # response.status_code = 200
    #     # print("content1:", response.render().content.decode('utf-8'))
    #     # print("response after:", response)
    #     # print("previous status_code: ", response.status_code)
    #     # rendered_page = response.content.decode('utf-8')
    #     # print("status before", response.status_code)
    #     # response.status_code = 400
    #     # print("status after", response.status_code)
    #     # print("response is: ", dir(response))
    #     # return JsonResponse(data, status=200)

    #     # error_message_exists = any(message.level == messages.ERROR for message in storage)
    #     # if error_message_exists:
    #     #     return HttpResponseRedirect(reverse('adminpage-admin:booking_booking_changelist'))
    #     return response  # Replace with the desired URL
        
    # #     # Custom logic to display success message after adding a model
    # #     self.message_user(request, "Object saved successfully.", level=messages.SUCCESS)
    # #     return super().response_add(request, obj, post_url_continue)
    
    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     print("change view!")
    #     self.change_form_template = 'admin/diagnoser/diagnoser_change.html'
    #     # extra_context = extra_context or {}
    #     # print(extra_context)
    #     # extra_context['errors'] = None
    #     return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        print("cahnge_vew_something!")
        extra_context = extra_context or {}
        form = self.get_form(request)(request.POST or None, request.FILES or None)
        print(dir(form))
        print(form.errors)
        # form.fields['model_name'].initial ="hello mf"
        # form.base_fields['model_name'].initial ="hello mf"
        # extra_context['form'] = form
        # print(form)
        # extra_context['form'] = form
        # extra_context['errors'] = form.errors.values()
        # form.errors.values()
        form = self.form

        context = {
            'form': form,
        }
        response = super().changeform_view(request, object_id, form_url, extra_context=extra_context)
        print("response: ", response)
        return response


    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     extra_context = extra_context or {}
    #     # extra_context['app_label'] = 'asdasd'
    #     app_label  = "chatbot_models_manager" 
    #     print("changing view")
    #     # print(request.method)
    #     if request.method == 'POST':
    #         form = self.get_form(request)(request.POST)
    #         if form.is_valid():
    #             print("form is valid!")
    #     #         # Process the form data (e.g., save to database)
    #     #         # form.save()
    #     #         return JsonResponse({'success': True})
    #         else:
    #             print("hello world")
    #             has_editable_inline_admin_formsets = False
    #             to_field = request.POST.get(op.TO_FIELD_VAR, request.GET.get(op.TO_FIELD_VAR))
    #     #         # Return the form errors
    #             # context = {'request': request}  # Include the 'request' object in the context
    #             # return render(request, 'admin/diagnoser/diagnoser_add.html')
    #             context = {
    #                 **self.admin_site.each_context(request),
    #                 "opts": self.opts,
    #                 "add": object_id is None,
    #                 "change": not (object_id is None),
    #                 "is_popup": op.IS_POPUP_VAR,
    #                 "save_as": self.save_as,
    #                 "has_add_permission": self.has_add_permission(request),
    #                 "has_delete_permission": self.has_delete_permission(request),
    #                 "has_change_permission": self.has_change_permission(request),
    #                 "has_view_permission": self.has_view_permission(request),
    #                 "has_editable_inline_admin_formsets": True
    #             }
    #             # context.update(self.get_model_perms(request))
    #             error_html = render_to_string('client/pages/diagnoser_add.html', context)
    #             # print(error_html)
    #             return HttpResponse(error_html)
    #             # return  error_html
    #             # error_html = render(request, 'admin/diagnoser/diagnoser_add.html')
    #     #         return JsonResponse({'success': False, 'error_html': error_html})
    #     # else:
    #     #     print("returned normal")
    #     #     # Render the default admin add page
    #     return super().changeform_view(request, object_id, form_url, extra_context)


    # def add_view(self, request, form_url='', extra_context=None):
    #     self.change_form_template = 'admin/diagnoser/diagnoser_add.html'
    #     extra_context = extra_context or {}
    #     # form = self.get_form(request)
    #     # extra_context['form'] = form
    #     # context = {
    #     #     'form': form,
    #     # }
    #     print("*********add view**********")
    #     print(extra_context)
    #     return super().add_view(request, form_url, extra_context=extra_context)
    

    # # def change_view(self, request, object_id=None, form_url='', extra_context=None):
    # #     extra_context = extra_context or {}
    # #     extra_context['save_button_text'] = _('Custom Save Button Text')
    # #     return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    # #     extra_context = extra_context or {}
    # #     extra_context['save_button_text'] = _('Custom Save Button Text')
    # #     return super().changeform_view(request, object_id, form_url, extra_context=extra_context)


    # # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    # #     extra_context = extra_context or {}
    # #     extra_context['save_button_text'] = _('Custom Save Button Text')
    # #     return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    # # def change_view(self, request, object_id, form_url='', extra_context=None):
    # #     print("****contenxt is wokring!!****")
    # #     extra_context = extra_context or {}
    # #     extra_context['save_button_text'] = _('Custom Save Button Text')
    # #     return super().change_view(request, object_id, form_url, extra_context=extra_context)




my_admin_site.register(Diagnoser, DiagnoserAdmin)
my_admin_site.register(NER)