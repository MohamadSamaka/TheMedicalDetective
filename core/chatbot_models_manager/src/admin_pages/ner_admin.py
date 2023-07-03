from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.forms import FileInput
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db import transaction
from django.db.utils import IntegrityError
from asgiref.sync import async_to_sync
from core.chatbot_models_manager.src.tasks.tasks import set_cancel_flag
from core.core.src.utls.helpers import delete_dir_with_contents_if_canceled
from ..forms.ner import NERInfoForm
from ..widgets.file_download import FileDownloadWidget
from time import sleep



class NERAdmin(admin.ModelAdmin):
    form = NERInfoForm

    def add_view(self, request, form_url='', extra_context=None):
        self.change_form_template = "admin/ner/ner_add.html"
        extra_context = extra_context or {}
        extra_context['form'] = self.get_form(request)
        return super().add_view(request, form_url, extra_context=extra_context)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["training_file"].widget = FileDownloadWidget("training.csv", obj.model_name)
            form.base_fields["training_file"].required = False
            form.base_fields["iterations"].disabled = True
            form.base_fields["neurons_first_layer"].disabled = True
        else:
            form.base_fields["training_file"].required = True
            form.base_fields["iterations"].disabled = False
            form.base_fields["neurons_first_layer"].disabled = False
            form.base_fields["training_file"].widget = FileInput()
        return form

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('validate_ner_form/', self.ner_form_validator, name='ner-form-validator'),
            path('train_ner_model/', self.ner_trainer, name="ner-trainer"),
        ]
        return my_urls + urls
    
    def save_model(self, request, obj, form, change):
        if change:
            old_model_name = form.initial['model_name']
            new_model_name = form.cleaned_data['model_name']
            old_directory_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / old_model_name
            new_directory_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / new_model_name
            
            # Rename the directory
            old_directory_path.rename(new_directory_path)
            
            # Rename the files within the directory
            for file_path in new_directory_path.iterdir():
                if file_path.is_file() and file_path.stem == old_model_name:
                    new_file_path = file_path.with_name(new_model_name + file_path.suffix)
                    file_path.rename(new_file_path)

        super().save_model(request, obj, form, change)
    

        

    
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


    def ner_form_validator(self, request):
        status_code = 200
        if request.method == 'POST':
            form = self.form(request.POST, request.FILES)
            if form.is_valid():
                self.send_form_validation_result(1)
                status_code =  self.process_model(request, form)
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
        return render(request, 'admin/ner/ner_add.html', context, status = status_code)
    


    @transaction.atomic
    def process_model(self, request, form):
        from pathlib import Path
        try:
            iterations = form.cleaned_data['iterations']
            iterations = 300
            model_name = form.cleaned_data['model_name']
            layer1_neurons = form.cleaned_data['neurons_first_layer']
            max_input_len = 100
            # layer2_neurons = form.cleaned_data['neurons_second_layer']
            training_file = form.cleaned_data['training_file']
            print("****got file: ****", training_file)
            # testing_file = form.cleaned_data['testing_file']
            path = Path(settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"ner/{model_name}"))
            path.mkdir(parents=True, exist_ok=False)
            user_id = request.user.id
            self.ner_trainer(user_id, model_name, training_file, layer1_neurons, iterations, max_input_len)
            if delete_dir_with_contents_if_canceled(path, user_id):
                return 200
            # self.store_csv_file(testing_file, model_name, "testing")
            if delete_dir_with_contents_if_canceled(path, user_id):
                return 200
            form.save()
            cache.delete(user_id)
            return 200
        except (IntegrityError) as e:
            delete_dir_with_contents_if_canceled(path, user_id)
    #         return 409
    

    def ner_trainer(self, user_id, model_name, training_file, layer1_nuerons, iterations, max_input_len):
        from core.chatbot_models_manager.src.models.NER import NERModel
        trainer = NERModel.Trainer(training_file, layer1_nuerons, iterations, max_input_len)
        set_cancel_flag.apply_async(args=(user_id, False))
        sleep(1)
        trainer.train_model(user_id)
        if not cache.get(user_id).get('cancel_flag'):
            trainer.save_model(model_name)
            trainer.save_tokenizer(model_name)
    
    
    def cancel_training(self, request):
        if request.method == "POST":
            key = request.user.id
            set_cancel_flag.apply_async(args=(key, True))
            return JsonResponse({'message': 'Training cancellation requested'})
        return HttpResponseNotAllowed(['POST']) 
            
