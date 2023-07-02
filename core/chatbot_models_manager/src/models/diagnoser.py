from django.core.cache import cache
from django.conf import settings
import tensorflow as tf
import pandas as pd
import numpy as np
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_progress_update(logs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "train",
        {
            'type': 'progress_update',
            'info': {
                'loss': logs['loss'],
                'accuracy': logs['accuracy'],
            },
        }
    )


class ModelNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

    def log_error(self):
        error_message = f"ModelNotFound exception occurred: {self.args[0]}"

    def __str__(self):
        return f"ModelNotFound: {self.args[0]}"
    
class DiseasesListNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

    def log_error(self):
        error_message = f"DiseasesListNotFound exception occurred: {self.args[0]}"

    def __str__(self):
        return f"DiseasesListNotFound: {self.args[0]}"
    
class SymptomsListNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)

    def log_error(self):
        error_message = f"SymptomsListNotFound exception occurred: {self.args[0]}"

    def __str__(self):
        return f"SymptomsListNotFound: {self.args[0]}"


class DiagnoserModel:
    iterations = 100
    dense1_n_neurons = 64
    dense2_n_neurons = 32

    def pre_proccessing(training_file, testing_file):
        training_data = pd.read_csv(training_file)
        DiagnoserModel.cols = training_data.columns[:-1]
        x = training_data[DiagnoserModel.cols].values
        y = training_data['prognosis'].values
        # map strings to numbers
        DiagnoserModel.unique_labels = list(set(y))
        label_map = {label: i for i, label in enumerate(DiagnoserModel.unique_labels)}
        y = np.array([label_map[label] for label in y])
        # split the data into training and testing sets
        split = int(0.67 * len(x))
        x_train, y_train = x[:split], y[:split]
        x_validate, y_validate= x[split:], y[split:]

        # testing = pd.read_csv(settings.DATASETS_DIR / 'diagnoser'/ testing_data)
        testing_data = pd.read_csv(testing_file)
        x_test = testing_data[DiagnoserModel.cols].values
        y_test = testing_data['prognosis'].values
        y_test = np.array([label_map[label] for label in y_test])
        testing_file.seek(0)  
        training_file.seek(0)  
        
        return (x_train, y_train), (x_validate, y_validate), (x_test, y_test)

    def save_model(self, model_name):
            self.model.save_model(model_name)

    class Trainer:
        def __init__(self, training_file, testing_file, dense1_n_neurons , dense2_n_neurons, iterations):
            self.initialize_defaults(dense1_n_neurons, dense2_n_neurons, iterations)
            self.training_data, self.validation_data, self.testing_data = DiagnoserModel.pre_proccessing(training_file, testing_file)
            DiagnoserModel.input_shape = self.training_data[0].shape[1]
            self.model = DiagnoserModel.Model()

        def initialize_defaults(self, dense1_n_neurons, dense2_n_neurons, iterations):
            if dense1_n_neurons:
                DiagnoserModel.dense1_n_neurons = dense1_n_neurons
            if dense2_n_neurons:
                DiagnoserModel.dense2_n_neurons = dense2_n_neurons
            if iterations:
                DiagnoserModel.iterations = iterations

        def train_model(self, user_id):
            self.model.train_model(user_id, self.training_data, self.validation_data)

        def save_model(self, model_name="default_model"):
             self.model.save_model(model_name)

    
    class Model:
        def __init__(self, dense1_n_neurons = None, dense2_n_neurons = None, iterations = None, input_shape=None):
            self.initialize_defaults(dense1_n_neurons, dense2_n_neurons, iterations, input_shape)

        def initialize_defaults(self, dense1_n_neurons, dense2_n_neurons, iterations, input_shape):
            if dense1_n_neurons:
                DiagnoserModel.dense1_n_neurons = dense1_n_neurons
            if dense2_n_neurons:
                DiagnoserModel.dense2_n_neurons = dense2_n_neurons 
            if iterations:
                DiagnoserModel.iterations = iterations
            if input_shape:
                DiagnoserModel.input_shape = input_shape

            
        def build_complie_model(self):
            self.model = tf.keras.models.Sequential([
                tf.keras.layers.Dense(DiagnoserModel.dense1_n_neurons, activation='relu', input_shape=(DiagnoserModel.input_shape,)),
                tf.keras.layers.Dense(DiagnoserModel.dense2_n_neurons, activation='relu'),
                tf.keras.layers.Dense(len(DiagnoserModel.unique_labels), activation='softmax')
            ])
            self.model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )

        def load_model(model_name="default_model"):
            import pickle
            try:
                model_path = settings.MODELS_DIR / "diagnoser" / model_name
                with open(model_path, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, pickle.UnpicklingError):
                return None
            
        def pre_process(extracted_symptoms):
            pass
            

        def diagnose(extracted_symptoms, pickle):
            import numpy as np
            # pickle = DiagnoserModel.Model.load_model(model_name)
            model = pickle['model']
            id_to_diease = pickle['diseases']
            original_symptoms = pickle['symptoms']

            if not model:
                raise ModelNotFound("Failed to load model")
            if not original_symptoms:
                raise SymptomsListNotFound("Failed to load symptoms")
            if not id_to_diease:
                raise DiseasesListNotFound("Failed to load diseases")


            normalized_symps = DiagnoserModel.Model.normalize_symptoms(extracted_symptoms, original_symptoms)
            encoded_symptoms = DiagnoserModel.Model.onehot_encoded_symptoms(normalized_symps, original_symptoms)
            prediction = model.predict(np.array(encoded_symptoms).reshape((1, len(original_symptoms)))).argmax()
            return id_to_diease[prediction], normalized_symps
        
        def onehot_encoded_symptoms(normalized_symps, original_symptoms):
            encoded_symptoms = [0] * len(original_symptoms)
            for symp in normalized_symps:
                index = original_symptoms[symp]
                encoded_symptoms[index] = 1
            return encoded_symptoms

        def normalize_symptoms(extracted_symps_list, original_symptom_list):
            import jellyfish
            normalized_symps_list = []
            symptoms = list(original_symptom_list.keys())[:-1]


            for ex_symp in extracted_symps_list:
                max_ratio = float('-inf')
                for original_symp in symptoms:
                    ratio = jellyfish.jaro_distance(ex_symp, original_symp)
                    if ratio > max_ratio:
                        max_ratio = ratio
                        closest_normalization = original_symp
                normalized_symps_list.append(closest_normalization)
            return normalized_symps_list

        def train_model(self, user_id, training_data, validation_data):
            from time import sleep
            self.build_complie_model()
            accuracy = None
            
            class LossHistoryCallback(tf.keras.callbacks.Callback):
                def on_epoch_end(self, epoch, logs=None):
                    nonlocal accuracy
                    accuracy = logs['accuracy']
                    send_progress_update(logs)
                    cancel_state = cache.get(user_id).get('cancel_flag')
                    if cancel_state:
                        self.model.stop_training = True  
           
            loss_history_callback = LossHistoryCallback()
            self.model_accuracy = accuracy
            self.model.fit(*training_data, epochs=DiagnoserModel.iterations, validation_data=validation_data, callbacks=[loss_history_callback])

        def save_model(self, model_name):
            import pickle
            import json
            from pathlib import Path
            try:
                model_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(model_name)
                symptoms_map = DiagnoserModel.cols.to_series().reset_index(drop=True).to_dict()
                id_to_symptom = dict(zip(symptoms_map.values(), symptoms_map.keys()))
                disease_to_id = {id: disease for id, disease in enumerate(DiagnoserModel.unique_labels)}
                data_to_pikcle = {
                    'model': self.model,
                    'diseases': disease_to_id,
                    'symptoms': id_to_symptom,
                }
                
                model_info = {
                    'iterations': DiagnoserModel.iterations ,
                    'accuracy': self.model_accuracy,
                    'dense1_n_neurons' : DiagnoserModel.dense1_n_neurons,
                    'dense2_n_neurons' : DiagnoserModel.dense2_n_neurons,
                }
                
                with open(model_path / Path(f'{model_name}.model'), 'wb') as f:
                    pickle.dump(data_to_pikcle, f)
                with open(model_path / Path(f'{model_name}.json'), 'w') as f:
                    json.dump(model_info, f)
                return True
            except Exception as e:
                print('Model has not been saved')
                print(str(e))
                return False