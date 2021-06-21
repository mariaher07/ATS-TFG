# -*- coding: utf-8 -*-
"""model_gpu_news.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16I3-Kk2WMXjeu1ibYvqL6CaxZCLIztxY

#0. Imports
"""

'''from google.colab import drive
drive.mount('/content/drive')'''

data_path = ####
output_path = #####

import tensorflow as tf

#check GPU
import tensorflow as tf
device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  print('GPU device not found: continue with CPU')
else:
  print('Found GPU at: {}'.format(device_name))


#check versions
print('tf version: ', tf.__version__)
print('tf.keras version:', tf.keras.__version__)

import numpy as np
import pandas as pd 

from sklearn.model_selection import train_test_split


from tensorflow.keras.preprocessing.text import Tokenizer 
from tensorflow.keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping

from attention import AttentionLayer

"""#1. Load dataset"""

print("Num of GPUs available: ", len(tf.test.gpu_device_name()))
print("\n")

df = pd.read_csv(output_path+ "arxiv_preprocessed.csv", encoding='latin-1')
print(df.shape)

"""#2. Tokenization"""

max_headlines_length = 15
max_text_length = 55

#train and test split
x_tr, x_test, y_tr, y_test=train_test_split(np.array(df['text']), np.array(df['headlines']), test_size=0.15, random_state=0, shuffle=True)

#train and val split
x_tr, x_val, y_tr, y_val=train_test_split(x_tr, y_tr , test_size=0.15, random_state=0, shuffle=True)

#prepare a tokenizer for reviews on training data
x_tokenizer = Tokenizer() 
x_tokenizer.fit_on_texts(list(x_tr))

total_words=0

for key,value in x_tokenizer.word_counts.items():
    total_words=total_words+1
    
# Tokenizer
x_tokenizer = Tokenizer(num_words=total_words) 
x_tokenizer.fit_on_texts(list(x_tr))

#convert to integer sequences
x_tr_seq    =   x_tokenizer.texts_to_sequences(x_tr) 
x_val_seq   =   x_tokenizer.texts_to_sequences(x_val)
x_test_seq   =   x_tokenizer.texts_to_sequences(x_test)

#padding zero 
x_tr    =   pad_sequences(x_tr_seq,  maxlen=max_text_length, padding='post')
x_val   =   pad_sequences(x_val_seq, maxlen=max_text_length, padding='post')
x_test =  pad_sequences(x_test_seq, maxlen=max_text_length, padding='post')

#size of vocabulary 
x_voc   =  len(x_tokenizer.word_index )+ 1

x_voc

#prepare a tokenizer for titles on training data
y_tokenizer = Tokenizer()   
y_tokenizer.fit_on_texts(list(y_tr))

total_words=0

for key,value in y_tokenizer.word_counts.items():
    total_words=total_words+1

#prepare a tokenizer for titles on training data
y_tokenizer = Tokenizer(num_words=total_words) 
y_tokenizer.fit_on_texts(list(y_tr))

#convert to integer sequences
y_tr_seq    =   y_tokenizer.texts_to_sequences(y_tr) 
y_val_seq   =   y_tokenizer.texts_to_sequences(y_val) 
y_test_seq =   y_tokenizer.texts_to_sequences(y_test)

#padding zero 
y_tr    =   pad_sequences(y_tr_seq, maxlen=max_headlines_length, padding='post')
y_val   =   pad_sequences(y_val_seq, maxlen=max_headlines_length, padding='post')
y_test   =   pad_sequences(y_test_seq, maxlen=max_headlines_length, padding='post')


#size of vocabulary
y_voc  =   len(y_tokenizer.word_index )+1

#delete sequences that only have padding values (0s)
ind=[]
for i in range(len(y_tr)):
    cnt=0
    for j in y_tr[i]:
        if j!=0:
            cnt=cnt+1
    if(cnt==2):
        ind.append(i)

y_tr=np.delete(y_tr,ind, axis=0)
x_tr=np.delete(x_tr,ind, axis=0)

ind=[]
for i in range(len(y_val)):
    cnt=0
    for j in y_val[i]:
        if j!=0:
            cnt=cnt+1
    if(cnt==2):
        ind.append(i)

y_val=np.delete(y_val,ind, axis=0)
x_val=np.delete(x_val,ind, axis=0)

"""#3. Model"""

print("Num of GPUs available: ", len(tf.test.gpu_device_name()))

import tensorflow.keras.backend as K 
K.clear_session()
print("\n")
print("Creating model...")

latent_dim = 200
embedding_dim= 100 

# Set up the Encoder
encoder_inputs = Input(shape=(max_text_length,))

#embedding layer
enc_emb =  Embedding(x_voc, embedding_dim, trainable=True)(encoder_inputs)

#encoder lstm1 layer
encoder_lstm1 = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4)
encoder_output1, state_h1, state_c1 = encoder_lstm1(enc_emb)

#encoder lstm2 layer
encoder_lstm2 = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.4)
encoder_output2, state_h2, state_c2 = encoder_lstm2(encoder_output1)

#encoder lstm3 layer
encoder_lstm3=LSTM(latent_dim, return_state=True, return_sequences=True, dropout=0.4, recurrent_dropout=0.4)
encoder_outputs, state_h, state_c= encoder_lstm3(encoder_output2)

# Set up the decoder
decoder_inputs = Input(shape=(None,))

#embedding layer
dec_emb_layer = Embedding(y_voc, embedding_dim, trainable=True)
dec_emb = dec_emb_layer(decoder_inputs)

decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True, dropout=0.4, recurrent_dropout=0.2)
decoder_outputs, decoder_fwd_state, decoder_back_state = decoder_lstm(dec_emb, initial_state=[state_h, state_c])

# Attention layer
attention_layer = AttentionLayer (name='attention_layer')
attention_outputs, attention_states = attention_layer([encoder_outputs, decoder_outputs])

# Concat attention 
decoder_concat_input = Concatenate(axis=-1, name='concat_layer')([decoder_outputs, attention_outputs])

# softmax layer
decoder_dense =  TimeDistributed(Dense(y_voc, activation='softmax'))
decoder_outputs = decoder_dense(decoder_concat_input)

# Define the model 
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.summary()

model.compile(optimizer='rmsprop', loss='sparse_categorical_crossentropy')
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1,patience=2)
history=model.fit([x_tr,y_tr[:,:-1]], y_tr.reshape(y_tr.shape[0],y_tr.shape[1], 1)[:,1:], epochs=50, callbacks=[es], batch_size=128, validation_data=([x_val,y_val[:,:-1]], y_val.reshape(y_val.shape[0], y_val.shape[1], 1)[:,1:]))

print("\nModel trained... \n")

"""#4. Inference"""

# beam search algorithm
# beam width parameter k: k most likely sequences
def beam_search_algorithm(data, k):
  #initialize 0 sequences
	output = [[list(), 0.0]]
  #iterate over lines
	for line in data:
		all_candidates = list()
		# add candidates and score
		for i in range(len(output)):
			seq, score = output[i]
			for j in range(len(line)):
				candidate = [seq + [j], score - log(line[j])]
				all_candidates.append(candidate)
		# order candidates by score
		ordered_candidates = sorted(all_candidates, key=lambda tup:tup[1])
		# select k best options
		output = ordered_candidates[:k]
	return output

reverse_target_word_index=y_tokenizer.index_word
reverse_source_word_index=x_tokenizer.index_word
target_word_index=y_tokenizer.word_index

# Feature vector
encoder_model = Model (inputs = encoder_inputs, outputs = [encoder_outputs, state_h, state_c])

# Decoder setup
decoder_state_input_h = Input(shape=(latent_dim,))
decoder_state_input_c = Input(shape=(latent_dim,))
decoder_hidden_state_input = Input(shape=(max_text_length,latent_dim))

# embeddings
dec_emb_inference= dec_emb_layer(decoder_inputs) 

# set initial state to the states from the previous time step 
decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb_inference, initial_state=[decoder_state_input_h, decoder_state_input_c])

#attention 
attention_out_inference, attention_states_inference = attention_layer([decoder_hidden_state_input, decoder_outputs2])
decoder_inference_concat = Concatenate(axis=-1, name='concat')([decoder_outputs2, attention_out_inference])

# softmax layer 
decoder_outputs2 = decoder_dense(decoder_inference_concat) 

# Final decoder model
decoder_model = Model([decoder_inputs] + [decoder_hidden_state_input, decoder_state_input_h, decoder_state_input_c],
    [decoder_outputs2] + [state_h2, state_c2])

# Decode feature vector using the Decoder Model
# Outputs a the decoded sentence

def decode_sequence(input_sequence):
    encoder_output, encoder_h, encoder_c = encoder_model.predict(input_sequence)
    
    # target sequence full of 0's
    target_sequence = np.zeros((1,1))
    
    # first word of the sequence: "sostok"
    target_sequence[0, 0] = target_word_index['sostok']

    stop_condition = False
    decoded_sentence = ''
    # look while stop_condition is not activated 
    while not stop_condition:
      
        output_tokens, h, c = decoder_model.predict([target_sequence] + [encoder_output, encoder_h, encoder_c])

        # Sample one token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_token = reverse_target_word_index[sampled_token_index]
        
        # if token different to "eostok"
        if(sampled_token!='eostok'):
            decoded_sentence += ' '+sampled_token

        # finish the sentence when max length is reached or the word found is 'eostok'
        if (sampled_token == 'eostok'  or len(decoded_sentence.split()) >= (max_headlines_length-1)):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_sequence = np.zeros((1,1))
        target_sequence[0, 0] = sampled_token_index

        # Update internal states
        encoder_h, encoder_c = h, c

    return decoded_sentence

#two different functions to convert integer to text sequences
#because headline sequences will have "sostok" and "eostok" tokens
#that long texts won't


#conversion of headline integer sequences to text sequences
def textsequence_headline(input_sequence):
    output_sequence = ''
    for i in input_sequence:
        if((i!=0 and i!=target_word_index['sostok']) and i!=target_word_index['eostok']):
            output_sequence = output_sequence +  reverse_target_word_index[i]+' '
    return output_sequence

#conversion of article integer sequences to text sequences
def textsequence_article(input_sequence):
    output_sequence = ''
    for i in input_sequence:
        if(i!=0):
            output_sequence = output_sequence+reverse_source_word_index[i]+' '
    return output_sequence

"""Calculate predictions for text subset"""

test_dataset_evaluation = pd.DataFrame(columns=["real_title", "predicted_title"]) 
print(test_dataset_evaluation)
for i in range(0,len(x_test)):
    test_dataset_evaluation.at [i,"real_title"]= textsequence_headline(y_test[i])
    test_dataset_evaluation.at [i,"predicted_title"]= decode_sequence(x_test[i].reshape(1,max_text_length))

test_dataset_evaluation

"""Save predictions to csv

"""

test_dataset_evaluation.head()
test_dataset_evaluation.to_csv(output_path+'news_predictions.csv',index=False)