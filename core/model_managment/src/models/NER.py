from django.conf import settings
from keras import Sequential
from keras.layers import Dense, Embedding, Bidirectional, LSTM
from keras.preprocessing.text import Tokenizer as TK
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.stem import WordNetLemmatizer
import numpy as np
import json
import pickle
import re


class MissingModelOrTokenizer(Exception):
    def __init__(self, message):
        super().__init__(message)

    def log_error(self):
        error_message = f"MissingModelOrTokenizer exception occurred: {self.args[0]}"

    def __str__(self):
        return f"MissingModelOrTokenizer: {self.args[0]}"

class NERModel:
    dataset_name = 'default.json'
    iterations = 300
    max_input_len = settings.MAX_SEQUENCE_LENGTH
    n_neurons = 64
    
    tags = ['0', 'B-SYMP', 'I-SYMP']

    def tag_to_id():
        return {tag: i for i, tag in enumerate(NERModel.tags)}

    def get_sentences(train_data):
        return [data[0].lower() for data in train_data]
    
    class Trainer:
        def __init__(self, dataset_name=None, iterations=None, max_input_len=None, n_neurons=None):
            self.initialize_defaults(dataset_name, iterations, max_input_len, n_neurons)
            self.train_data = self.read_dataset()
            sentances = NERModel.get_sentences(self.train_data)
            self.tokenizer = NERModel.Tokenizer(sentances)
            self.word_index = self.tokenizer.word_index
            # self.tag_to_idx = NERModel.tag_to_id()
            # self.sequences = self.tokenizer.get_sequences(self.train_data)
            self.annotations = self.soft_text_preprocess(self.train_data, self.word_index) #simply these are the labels
            self.model = NERModel.Model(len(self.word_index), NERModel.n_neurons, len(NERModel.tags))
            self.x_train = self.get_padded_sequences(sentances, NERModel.max_input_len)
            # self.x_train = pad_sequences(self.get_sequences(), padding='post', maxlen=NERModel.max_input_len)
            self.y_train = self.tokenizer.generate_labels(self.x_train, self.annotations)
            self.y_train = pad_sequences(self.y_train, padding='post', maxlen=NERModel.max_input_len)
            # self.y_train = self.get_padded_sequences(self.y_train, NERModel.max_input_len)

        def initialize_defaults(self, dataset_name, iterations, max_input_len, n_neurons):
            if dataset_name:
                NERModel.dataset_name = dataset_name
            if iterations:
                NERModel.iterations = iterations
            if max_input_len:
                NERModel.max_input_len = max_input_len
            if n_neurons:
                NERModel.n_neurons = n_neurons

        def train_model(self):
            self.model.train_model(self.x_train, self.y_train, NERModel.iterations)

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

        def read_dataset(self):
            with open(settings.DATASETS_DIR / 'NER' / NERModel.dataset_name, 'r') as f:
                json_file = json.load(f)
                # json_file = [json_file[3]]
                train_data = []
                for annonated_text in json_file:
                    entities = []
                    for labels in annonated_text['label']:
                        entities.append((labels['start'], labels['end'],labels['labels'][0]))
                    train_data.append((annonated_text['text'], entities))
            return train_data
        
        
        def get_padded_sequences(self, sequences, max_input_len, padding="post"):
            return self.tokenizer.get_padded_sequences(sequences, max_input_len, padding)

        def save_tokenizer(self, tokenizer_name="default_tokenizer"):
            self.tokenizer.save_tokenizer(tokenizer_name)

        def save_model(self, model_name="default_model"):
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
        
        def load_tokenizer(tokenizer_name="default_tokenizer"):
            try:
                tokenizer_path = settings.MEDIA_ROOT / "tokenizers" / tokenizer_name
                with open(tokenizer_path, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, pickle.UnpicklingError):
                return None
            

        def save_tokenizer(self, file_name="default_tokenizer"):
            try:
                with open(settings.TOKENIZERS_DIR / file_name, 'wb') as f:
                    pickle.dump(self.tokenizer, f)
                return True
            except:
                print('Tokenizer has not been saved')
                return False
                

    class Model:
        def __init__(self, word_len = None, n_neurons = None, tags_num = None):
            self.initialize_defaults(word_len, n_neurons, tags_num)

        def initialize_defaults(self, word_len, n_neurons, tags_num):
            if word_len:
                NERModel.word_len = word_len
            if n_neurons:
                NERModel.n_neurons = n_neurons
            if tags_num:
                NERModel.tags_num = tags_num

        def build_complie_model(self):
            self.model = Sequential([
                Embedding(NERModel.word_len + 1, NERModel.n_neurons),
                Bidirectional(LSTM(NERModel.n_neurons, return_sequences=True)),
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
    

        def train_model(self, x_train, y_train, iterations):
            self.build_complie_model()
            self.model.fit(x_train, y_train, epochs=iterations)
            return self.model
        
        def load_model(model_name="default_model"):
            try:
                model_path = settings.MODELS_DIR / "NER" / model_name
                with open(model_path, "rb") as f:
                    return pickle.load(f)
            except (FileNotFoundError, pickle.UnpicklingError):
                return None

            
        def save_model(self, model_name):
            try:
                with open(settings.MODELS_DIR / 'NER' / model_name, 'wb') as f:
                    pickle.dump(self.model, f)
                return True
            except:
                print('Model has not been saved')
                return False