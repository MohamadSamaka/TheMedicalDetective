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
from core.core.src.utls.helpers import delete_dir_with_contents_if_canceled, delete_dir_with_contents
from ..forms.diagnoser import DiagnoserInfoForm
from ..widgets.file_download import FileDownloadWidget
from pathlib import Path
from time import sleep



class DiagnoserAdmin(admin.ModelAdmin):
    form = DiagnoserInfoForm

    def add_view(self, request, form_url='', extra_context=None):
        self.change_form_template = "admin/diagnoser/diagnoser_add.html"
        extra_context = extra_context or {}
        extra_context['form'] = self.get_form(request)
        print(extra_context)
        return super().add_view(request, form_url, extra_context=extra_context)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.change_form_template = None
        return super().change_view(request, object_id, form_url, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('validate_diagnosis_form/', self.diagnoser_form_validator, name='diagnosis-form-validator'),
            path('train_diagnoser_model/', self.diagnoser_trainer, name="diagnoser-trainer"),
            path('cancel_training/', self.cancel_training, name="cancel-diagnoser-trainer")
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


    def delete_model(self, request, obj):
        path = Path(settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"diagnoser/{obj.model_name}"))
        delete_dir_with_contents(path)
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            path = Path(settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"diagnoser/{obj.model_name}"))
            delete_dir_with_contents(path)
        super().delete_queryset(request, queryset)
    

    @transaction.atomic
    def process_model(self, request, form):
        try:
            iterations = form.cleaned_data['iterations']
            model_name = form.cleaned_data['model_name']
            layer1_neurons = form.cleaned_data['neurons_first_layer']
            layer2_neurons = form.cleaned_data['neurons_second_layer']
            training_file = form.cleaned_data['training_file']
            testing_file = form.cleaned_data['testing_file']
            path = Path(settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"diagnoser/{model_name}"))
            path.mkdir(parents=True, exist_ok=False)
            user_id = request.user.id
            self.diagnoser_trainer(user_id, model_name, training_file, testing_file, iterations, layer1_neurons ,layer2_neurons)
            if delete_dir_with_contents_if_canceled(path, user_id):
                return 200
            self.store_csv_file(training_file, model_name, "training")
            self.store_csv_file(testing_file, model_name, "testing")
            if delete_dir_with_contents_if_canceled(path, user_id):
                return 200
            form.save()
            cache.delete(user_id)
            return 200
        except (IntegrityError) as e:
            delete_dir_with_contents_if_canceled(path, user_id)
            return 409
        
    
    def store_csv_file(self, file, model_name, fname):
        from pathlib import Path
        import pandas as pd
        csv_file = pd.read_csv(file)
        model_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"diagnoser/{model_name}/{fname}.csv")
        csv_file.to_csv(model_path, index=False)
        file.seek(0)

    
    def diagnoser_form_validator(self, request):
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
    

    def diagnoser_trainer(self, user_id, model_name, training_file, testing_file,  iterations, layer1_nuerons, layer2_neurons):
        from core.chatbot_models_manager.src.models.diagnoser import DiagnoserModel
        trainer = DiagnoserModel.Trainer(training_file, testing_file, layer1_nuerons, layer2_neurons, iterations)
        set_cancel_flag.apply_async(args=(user_id, False))
        trainer.train_model(user_id)
        if not cache.get(user_id).get('cancel_flag'):
            trainer.save_model(model_name)
    
    
    def cancel_training(self, request):
        if request.method == "POST":
            key = request.user.id
            set_cancel_flag.apply_async(args=(key, True))
            return JsonResponse({'message': 'Training cancellation requested'})
        return HttpResponseNotAllowed(['POST']) 
             
    
    def get_form(self, request, obj=None, **kwargs):
        print("getting form!")
        form = super().get_form(request, obj, **kwargs)
        if obj:
            print("wtf: ", obj.model_name)

            diagnoser_model_path = Path(f"diagnoser/{obj.model_name}")
            form.base_fields["training_file"].widget = FileDownloadWidget("training.csv", diagnoser_model_path)
            form.base_fields["testing_file"].widget = FileDownloadWidget("testing.csv", diagnoser_model_path)
            # form.base_fields["testing_file"].widget = FileDownloadWidget(file="test.txt")
            # form.base_fields["training_file"].initial = obj.training_file.name
            form.base_fields["training_file"].required = False
            form.base_fields["testing_file"].required = False
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
            form.base_fields["training_file"].widget = FileInput()
            # form.base_fields["testing_file"].widget = forms.FileInput()
        return form
