from django.conf import settings
import tensorflow as tf
import pandas as pd
import numpy as np
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_progress_update(logs, num):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "train",
        {
            # 'type': 'send_progress_update',
            'type': 'progress_update',
            'info': {
                'loss': logs['loss'],
                'accuracy': logs['accuracy'],
                'val_loss': logs['val_loss'],
                'num': num
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
    training_data_fname = "default_training.csv"
    testing_data_fname = "default_testing.csv"
    iterations = 100
    dense1_n_neurons = 64
    dense2_n_neurons = 32

    def pre_proccessing(training_data, testing_data):
        # encode training labels
        training = pd.read_csv(settings.DATASETS_DIR / 'diagnoser'/ training_data)
        DiagnoserModel.cols = training.columns[:-1]
        x = training[DiagnoserModel.cols].values
        y = training['prognosis'].values
        # map strings to numbers
        DiagnoserModel.unique_labels = list(set(y))
        label_map = {label: i for i, label in enumerate(DiagnoserModel.unique_labels)}
        y = np.array([label_map[label] for label in y])
        # split the data into training and testing sets
        split = int(0.67 * len(x))
        x_train, y_train = x[:split], y[:split]
        x_validate, y_validate= x[split:], y[split:]

        testing = pd.read_csv(settings.DATASETS_DIR / 'diagnoser'/ testing_data)
        x_test = testing[DiagnoserModel.cols].values
        y_test = testing['prognosis'].values
        y_test = np.array([label_map[label] for label in y_test])
        
        return (x_train, y_train), (x_validate, y_validate), (x_test, y_test)

    def save_model(self, model_name="default_model"):
            self.model.save_model(model_name)

    class Trainer:
        def __init__(self, training_data_fname = None, testing_data_fname = None, dense1_n_neurons = None , dense2_n_neurons = None, iterations = None):
            self.initialize_defaults(training_data_fname, testing_data_fname, dense1_n_neurons, dense2_n_neurons, iterations)
            self.training_data, self.validation_data, self.testing_data = DiagnoserModel.pre_proccessing(DiagnoserModel.training_data_fname, DiagnoserModel.testing_data_fname)
            DiagnoserModel.input_shape = self.training_data[0].shape[1]
            self.model = DiagnoserModel.Model()

        def initialize_defaults(self, training_data_fname, testing_data_fname, dense1_n_neurons, dense2_n_neurons, iterations):
            if training_data_fname:
                DiagnoserModel.training_data_fname = training_data_fname
            if testing_data_fname:
                DiagnoserModel.testing_data_fname = testing_data_fname
            if dense1_n_neurons:
                DiagnoserModel.dense1_n_neurons = dense1_n_neurons
            if dense2_n_neurons:
                DiagnoserModel.dense2_n_neurons = dense2_n_neurons
            if iterations:
                DiagnoserModel.iterations = iterations

        def train_model(self):
            # from channels.layers import get_channel_layer
            # progress = 0
            # for i in range(10):
            #     progress += 10

            #     # Send progress update to all connected consumers
            #     channel_layer = get_channel_layer()
            #     await channel_layer.group_send(
            #         "train",
            #         {
            #             'type': 'send_progress_update',
            #             'progress': progress,
            #         }
            #     )
            self.model.train_model(self.training_data, self.validation_data)
            # self.model.train_model()

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
            # for symp in extracted_symptoms:
            #     normalized_symps = DiagnoserModel.Model.normalize_symptoms(symp, symptoms)
            #     index = symptoms[normalized_symps]
            #     encoded_symptoms[index] = 1
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

        def train_model(self, training_data, validation_data):
            import threading
            import asyncio

            self.build_complie_model()
            class LossHistoryCallback(tf.keras.callbacks.Callback):
                def __init__(self):
                    self.num = 0
                def on_epoch_end(self, epoch, logs=None):
                    # thread = threading.Thread(target=self.run_async, args=(logs,))
                    # thread.start()
                    self.num+=1
                    send_progress_update(logs, self.num)

                # def run_async(self, logs):
                #     loop = asyncio.new_event_loop()
                #     asyncio.set_event_loop(loop)
                #     loop.run_until_complete(send_progress_update(logs))
                    
            loss_history_callback = LossHistoryCallback()
            self.model.fit(*training_data, epochs=DiagnoserModel.iterations, validation_data=validation_data, callbacks=[loss_history_callback])
            return self.model
        
        # async def test(self):
        #     from channels.layers import get_channel_layer
        #     progress = 0
        #     for i in range(10):
        #         progress += 10
        #         channel_layer = get_channel_layer()
        #         await channel_layer.group_send(
        #             "train",
        #             {
        #                 'type': 'send_progress_update',
        #                 'progress': progress,
        #             }
        #         )

        def save_model(self, model_name):
            import pickle
            try:
                symptoms_map = DiagnoserModel.cols.to_series().reset_index(drop=True).to_dict()
                id_to_symptom = dict(zip(symptoms_map.values(), symptoms_map.keys()))
                disease_to_id = {id: disease for id, disease in enumerate(DiagnoserModel.unique_labels)}
                data = {
                    'model': self.model,
                    'diseases': disease_to_id,
                    'symptoms': id_to_symptom,
                }
                with open(settings.MODELS_DIR / 'diagnoser' / model_name, 'wb') as f:
                    pickle.dump(data, f)
                    # pickle.dump(self.model, f)
                return True
            except Exception as e:
                print('Model has not been saved')
                print(str(e))
                return False