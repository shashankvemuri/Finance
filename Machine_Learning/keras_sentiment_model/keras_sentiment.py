import re
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
import sys
import os
from sklearn.metrics import auc
import matplotlib.pyplot as plt
from keras.preprocessing import sequence
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Lambda
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import GRU
from keras.preprocessing.text import Tokenizer
from keras import backend as K
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_curve

np.random.seed(10)

data = pd.read_csv('/Users/shashank/Documents/GitHub/Code/Finance/keras_sentiment_model/input/Combined_News_DJIA.csv')
data['Date'] = pd.to_datetime(data.Date)
train_split = 0.8
total_count = data.shape[0]
train_cut = int(total_count* train_split)
train = data.loc[: train_cut-1, :]
test = data.loc[train_cut :, :]
y_train = np.array(train["Label"])
y_test = np.array(test["Label"])

train.head()

trainheadlines = []
for row in range(0,len(train.index)):
    trainheadlines.append(' '.join(str(x) for x in train.iloc[row,2:27]))

testheadlines = []
for row in range(0,len(test.index)):
    testheadlines.append(' '.join(str(x) for x in test.iloc[row,2:27]))

def read_glove_vecs(glove_file):
    with open(glove_file, 'r', encoding='utf-8') as f:
        words = set()
        word_to_vec_map = {}
        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            words.add(curr_word)
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)
        
        i = 1
        words_to_index = {}
        index_to_words = {}
        for w in sorted(words):
            words_to_index[w] = i
            index_to_words[i] = w
            i = i + 1
    return words_to_index, index_to_words, word_to_vec_map

def convert_to_one_hot(Y, C):
    Y = np.eye(C)[Y.reshape(-1)]
    return Y

word_to_index, index_to_word, word_to_vec_map = read_glove_vecs('/Users/shashank/Documents/GitHub/Code/Finance/keras_sentiment_model/input/glove.6B.50d.txt')
word_to_vec_map['dog'].shape

def sentences_to_indices(X, word_to_index, max_len):
    """
    Converts an array of sentences (strings) into an array of indices corresponding to words in the sentences.
    The output shape should be such that it can be given to `Embedding()`. 
    
    Arguments:
    X -- array of sentences (strings), of shape (m, 1)
    word_to_index -- a dictionary containing the each word mapped to its index
    max_len -- maximum number of words in a sentence. You can assume every sentence in X is no longer than this. 
    
    Returns:
    X_indices -- array of indices corresponding to words in the sentences from X, of shape (m, max_len)
    """
    
    m = X.shape[0]                                   # number of training examples
    
    # Initialize X_indices as a numpy matrix of zeros and the correct shape
    X_indices = np.zeros((m, max_len), dtype=int)
    
    for i in range(m):                               # loop over training examples
        
        # Convert the ith training sentence in lower case and split is into words. You should get a list of words.
        sentence_words = [w.lower() for w in X[i].split()]
        
        # Initialize j to 0
        j = 0
        
        # Loop over the words of sentence_words
        for w in sentence_words:
            # Set the (i,j)th entry of X_indices to the index of the correct word.
            if w in word_to_index:
                X_indices[i, j] = word_to_index[w]
                # Increment j to j + 1
                j += 1
                if j >= max_len:
                    break
            
    return X_indices

strip_special_chars = re.compile("[^A-Za-z ]+")

def cleanSentences(string):
    # remove b"
    string = string.lower().replace("b\"", " ")
    # remove b\'
    string = string.lower().replace("b\'", "")
    return re.sub(strip_special_chars, "", string.lower())


a = ['b"Georgia \'downs']
np.array(list(map(lambda x:cleanSentences(x), a)))

X_train = np.array(list(map(lambda x:cleanSentences(x), trainheadlines)))
X_test = np.array(list(map(lambda x:cleanSentences(x), testheadlines)))

X_train[0]

X_train_lengths = list(map(lambda x: len(x.split()), X_train))
df = pd.DataFrame({'counts': X_train_lengths})
df.counts.plot.hist(bins = 40)

X1 = np.array(['germany to meet with france'])
X1_indices = sentences_to_indices(X1,word_to_index, max_len = 9)
print("X1 =", X1)
print("X1_indices =", X1_indices)

def pretrained_embedding_layer(word_to_vec_map, word_to_index):
    """
    Creates a Keras Embedding() layer and loads in pre-trained GloVe 50-dimensional vectors.
    
    Arguments:
    word_to_vec_map -- dictionary mapping words to their GloVe vector representation.
    word_to_index -- dictionary mapping from words to their indices in the vocabulary (400,001 words)

    Returns:
    embedding_layer -- pretrained layer Keras instance
    """
    
    vocab_len = len(word_to_index) + 1                  # adding 1 to fit Keras embedding (requirement)
    emb_dim = word_to_vec_map["cucumber"].shape[0]      # define dimensionality of your GloVe word vectors (= 50)
    
    # Initialize the embedding matrix as a numpy array of zeros of shape (vocab_len, dimensions of word vectors = emb_dim)
    emb_matrix = np.zeros((vocab_len, emb_dim))
    
    # Set each row "index" of the embedding matrix to be the word vector representation of the "index"th word of the vocabulary
    for word, index in word_to_index.items():
        emb_matrix[index, :] = word_to_vec_map[word]

    # Define Keras embedding layer with the correct output/input sizes, make it trainable. Use Embedding(...). Make sure to set trainable=False. 
    embedding_layer = Embedding(vocab_len, emb_dim, trainable=False)
    # Build the embedding layer, it is requi before setting the weights of the embedding layer. Do not modify the "None".
    embedding_layer.build((None,))
    
    # Set the weights of the embedding layer to the embedding matrix. Your layer is now pretrained.
    embedding_layer.set_weights([emb_matrix])
    
    return embedding_layer

embedding_layer = pretrained_embedding_layer(word_to_vec_map, word_to_index)
embedding_layer.get_weights()[0][word_to_index['cat']]

print('Build model...')
model = Sequential()
model.add(pretrained_embedding_layer(word_to_vec_map, word_to_index))
model.add(GRU(128, dropout=0.2, return_sequences=True)) 
model.add(GRU(128, dropout=0.2))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.summary()

maxlen = 500
batch_size = 32
X_train_indices = sentences_to_indices(X_train, word_to_index, maxlen)
X_test_indices = sentences_to_indices(X_test, word_to_index, maxlen)

# nb_classes = 2
# Y_train = np_utils.to_categorical(y_train, nb_classes)
# Y_test = np_utils.to_categorical(y_test, nb_classes)
Y_train = y_train.reshape((-1,1))
Y_test = y_test.reshape((-1,1))

print('Train...')
history = model.fit(X_train_indices, Y_train, batch_size=batch_size, epochs=10,
          validation_data=(X_test_indices, Y_test))

model.save("./model.h5")
score, acc = model.evaluate(X_test_indices, Y_test,
                            batch_size=batch_size)
print('Test score:', score)
print('Test accuracy:', acc)

y_pred_keras = model.predict(X_test_indices).ravel()
fpr_keras, tpr_keras, thresholds_keras = roc_curve(y_test, y_pred_keras)

auc_keras = auc(fpr_keras, tpr_keras)

plt.figure(1)
plt.plot([0, 1], [0, 1], 'k--')
plt.plot(fpr_keras, tpr_keras, label='Keras (area = {:.3f})'.format(auc_keras))
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('ROC curve')
plt.legend(loc='best')
plt.show()
