from django.conf import settings
from django.core.cache import cache
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense, Embedding, Bidirectional, LSTM
from keras.preprocessing.text import Tokenizer as TK
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.stem import WordNetLemmatizer
import numpy as np
import json
import pickle
import re
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pathlib import Path


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


class MissingModelOrTokenizer(Exception):
    def __init__(self, message):
        super().__init__(message)

    def log_error(self):
        error_message = f"MissingModelOrTokenizer exception occurred: {self.args[0]}"

    def __str__(self):
        return f"MissingModelOrTokenizer: {self.args[0]}"

class NERModel:
    iterations = 100
    max_input_len = settings.MAX_SEQUENCE_LENGTH
    n_neurons = 64
    
    tags = ['0', 'B-SYMP', 'I-SYMP']

    def tag_to_id():
        return {tag: i for i, tag in enumerate(NERModel.tags)}

    def get_sentences(train_data):
        return [data[0].lower() for data in train_data]
    
    class Trainer:
        def __init__(self, training_file, dense1_n_neurons, iterations, max_input_len):
            self.initialize_defaults(iterations, max_input_len, dense1_n_neurons)
            self.train_data = self.read_dataset(training_file)
            sentances = NERModel.get_sentences(self.train_data)
            self.tokenizer = NERModel.Tokenizer(sentances)
            self.word_index = self.tokenizer.word_index
            # self.tag_to_idx = NERModel.tag_to_id()
            # self.sequences = self.tokenizer.get_sequences(self.train_data)
            self.annotations = self.soft_text_preprocess(self.train_data, self.word_index) #simply these are the labels
            self.model = NERModel.Model(len(self.word_index), NERModel.dense1_n_neurons, len(NERModel.tags))
            self.x_train = self.get_padded_sequences(sentances, NERModel.max_input_len)
            # self.x_train = pad_sequences(self.get_sequences(), padding='post', maxlen=NERModel.max_input_len)
            self.y_train = self.tokenizer.generate_labels(self.x_train, self.annotations)
            self.y_train = pad_sequences(self.y_train, padding='post', maxlen=NERModel.max_input_len)
            # self.y_train = self.get_padded_sequences(self.y_train, NERModel.max_input_len)

        def initialize_defaults(self, iterations, max_input_len, dense1_n_neurons):
            if iterations:
                NERModel.iterations = iterations
            if max_input_len:
                NERModel.max_input_len = max_input_len
            if dense1_n_neurons:
                NERModel.dense1_n_neurons = dense1_n_neurons

        def train_model(self, user_id):
            self.model.train_model(user_id, self.x_train, self.y_train, NERModel.iterations)

        def soft_text_preprocess(self, train_data, word_to_id):
            sentences = []
            annotations = []
            tag_to_id = NERModel.tag_to_id()
            for sen, annos in train_data:
                tmp = {}
                sen = sen.lower()
                sentences.append(sen)
                for start, end, tag_name in annos:
                    token = sen[start:end]
                    previous_occurrence_count = len(re.findall(fr'\b{token}', sen[:start]))
                    anno_list = tmp.setdefault(word_to_id.get(token, 1), [])
                    if previous_occurrence_count:
                        anno_list.extend([0] * (previous_occurrence_count - len(anno_list)))
                        anno_list.append(tag_to_id[tag_name])
                    else:
                        anno_list.append(tag_to_id[tag_name])
                annotations.append(tmp)
            return annotations

        def read_dataset(self, training_file):
            json_file = json.load(training_file)
            train_data = []
            for annonated_text in json_file:
                entities = []
                for labels in annonated_text['label']:
                    entities.append((labels['start'], labels['end'], labels['labels'][0]))
                train_data.append((annonated_text['text'], entities))
            return train_data
        
        
        def get_padded_sequences(self, sequences, max_input_len, padding="post"):
            return self.tokenizer.get_padded_sequences(sequences, max_input_len, padding)

        def save_tokenizer(self, tokenizer_name):
            self.tokenizer.save_tokenizer(tokenizer_name)

        def save_model(self, model_name):
            self.model.save_model(model_name)
        

    class Tokenizer:
        def __init__(self, text):
            self.tokenizer = TK(oov_token="<OOV>")
            self.tokenizer.fit_on_texts(text)
            self.word_index = self.tokenizer.word_index

        def get_sequences(self, text):
            return self.tokenizer.texts_to_sequences(text)

        def get_padded_sequences(self, text, maxlen, padding="post"):
            # NERModel.max_input_len
            return pad_sequences(self.get_sequences(text), maxlen=maxlen, padding=padding)

        def generate_labels(self, sequences, annotations):
            y_train = []
            for seq, anno in zip(sequences, annotations):
                curr_label = [0] * len(seq)
                curr_index = 0
                while anno:
                    if anno.get(seq[curr_index]):
                        curr_label[curr_index] = anno[seq[curr_index]].pop(0)
                        if not anno[seq[curr_index]]:
                            anno.pop(seq[curr_index])
                    curr_index += 1
                y_train.append(curr_label)
            return np.array(y_train)
        
        def pre_processing(loaded_tokenizer, sent_case):
            processed_case = loaded_tokenizer.texts_to_sequences([sent_case])
            padded_sequence = pad_sequences(processed_case, maxlen=settings.MAX_SEQUENCE_LENGTH, padding='post')
            return padded_sequence
        
        def load_tokenizer(tokenizer_name):
            try:
                tokenizer_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"ner/{tokenizer_name}/{tokenizer_name}.tokenizer")
                with open(tokenizer_path, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, pickle.UnpicklingError):
                return None
            

        def save_tokenizer(self, model_name):
            model_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"ner/{model_name}")
            try:
                with open(model_path / f'{model_name}.tokenizer', 'wb') as f:
                    pickle.dump(self.tokenizer, f)
                return True
            except:
                print('Tokenizer has not been saved')
                return False
                

    class Model:
        def __init__(self, word_len = None, dense1_n_neurons = None, tags_num = None):
            self.initialize_defaults(word_len, dense1_n_neurons, tags_num)

        def initialize_defaults(self, word_len, dense1_n_neurons, tags_num):
            if word_len:
                NERModel.word_len = word_len
            if dense1_n_neurons:
                NERModel.dense1_n_neurons = dense1_n_neurons
            if tags_num:
                NERModel.tags_num = tags_num

        def build_complie_model(self):
            self.model = Sequential([
                Embedding(NERModel.word_len + 1, NERModel.dense1_n_neurons),
                Bidirectional(LSTM(NERModel.dense1_n_neurons, return_sequences=True)),
                Dense(NERModel.tags_num, activation='softmax')
            ])
            self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        def extract_symptoms(sent_case, model, tokenizer):
            # model, tokenizer = NERModel.Model.load_model(model_name), NERModel.Tokenizer.load_tokenizer(tokenizer_name)
            if tokenizer and model:
                # Process the tokenizer and model here
                sequence_to_predict = NERModel.Tokenizer.pre_processing(tokenizer, sent_case)
                prediction = model.predict(sequence_to_predict)
                symptoms = NERModel.Model.post_processing(prediction, sequence_to_predict, tokenizer.index_word)
                return symptoms
            else:
                raise MissingModelOrTokenizer("Failed to load model or tokenizer.")
        
        def post_processing(predicted, sequence_to_predict, indexed_words):
            from nltk.stem import WordNetLemmatizer
            import numpy as np
            lemmetizer = WordNetLemmatizer()
            input_prediction = []
            for i, p in zip(sequence_to_predict, predicted):
                input_prediction.append(list(zip(i[:np.where(i == 0)[0][0]], p.argmax(axis=1))))

            res = []
            for m in input_prediction:
                temp = []
                for word_id, label_id in m:
                    temp.append([indexed_words[word_id], NERModel.tags[label_id]])
                res.append(temp)

            for r in res:
                temp = []
                for i in range(len(r)):
                    r[i][0] = lemmetizer.lemmatize(r[i][0])

            final_res =  [(word, tag) for r in res for word, tag in r if tag != 'OOV' and tag != '0'] #clean up
            raw_symptoms = []
            temp = []

            for item in final_res:
                if item[1] == 'B-SYMP' and temp:
                    raw_symptoms.append('_'.join(temp))
                    temp = []
                temp.append(item[0])
            if temp:
                raw_symptoms.append('_'.join(temp))
                
            return raw_symptoms
    

        def train_model(self, user_id, x_train, y_train, iterations):
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
            self.model.fit(x_train, y_train, epochs=iterations, callbacks=[loss_history_callback])
            self.model_accuracy = accuracy
        
        def load_model(model_name):
            try:
                model_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"ner/{model_name}/{model_name}.model")
                with open(model_path, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, pickle.UnpicklingError):
                return None
            
        def save_model(self, model_name):
            model_info = {
                'iterations': NERModel.iterations ,
                'accuracy': self.model_accuracy,
                'dense1_n_neurons' : NERModel.dense1_n_neurons,
            }
            model_path = settings.PROTECTED_MEDIA_ABSOLUTE_URL / Path(f"ner/{model_name}")
            try:
                with open(model_path / f'{model_name}.model', 'wb') as f:
                    pickle.dump(self.model, f)
                with open(model_path / 'info.json', 'w') as f:
                    json.dump(model_info, f)
                return True
            except:
                print('Model has not been saved')
                return False