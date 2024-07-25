import json
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, GlobalAveragePooling1D, Dropout
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping

# Load intents.json file
with open('intents.json', encoding='utf-8') as file:
    data = json.load(file)

# Extract data from intents.json
training_sentences = []
training_labels = []
labels = []
responses = {}

for intent in data['intents']:
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(intent['tag'])
    responses[intent['tag']] = intent['responses']
    if intent['tag'] not in labels:
        labels.append(intent['tag'])

num_classes = len(labels)

# Encode labels
lbl_encoder = LabelEncoder()
lbl_encoder.fit(training_labels)
training_labels = lbl_encoder.transform(training_labels)

# Text preprocessing
vocab_size = 10000
embedding_dim = 128
oov_token = "<OOV>"
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index
sequences = tokenizer.texts_to_sequences(training_sentences)
padded_sequences = pad_sequences(sequences, truncating='post')

# Model
model = Sequential()
model.add(Embedding(vocab_size, embedding_dim, input_length=padded_sequences.shape[1]))
model.add(GlobalAveragePooling1D())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# Train the model
epochs = 500
early_stop = EarlyStopping(monitor='val_loss', patience=10)
model.fit(padded_sequences, np.array(training_labels), epochs=epochs, callbacks=[early_stop])

# Save the trained model in Keras format
model.save('chatbot_model.keras')

# Save the fitted tokenizer
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Save the fitted label encoder
with open('label_encoder.pickle', 'wb') as enc:
    pickle.dump(lbl_encoder, enc, protocol=pickle.HIGHEST_PROTOCOL)

# Save the responses
with open('responses.pickle', 'wb') as resp:
    pickle.dump(responses, resp, protocol=pickle.HIGHEST_PROTOCOL)

print("Model and necessary files saved successfully.")
