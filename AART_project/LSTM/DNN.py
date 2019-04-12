from __future__ import print_function
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from IPython.display import display, HTML

from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn import preprocessing

import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Reshape
from keras.layers import Conv2D, MaxPooling2D
from keras.utils import np_utils

# Set some standard parameters upfront
pd.options.display.float_format = '{:.1f}'.format
sns.set() # Default seaborn look and feel
plt.style.use('ggplot')
print('keras version ', keras.__version__)
# shooting => 投籃, layup => 上籃, dribble => 運球
LABELS = ['shooting',
          'layup',
          'dribble']
# The number of steps within one time segment
# FPS20 * 3 second = 60 => 60 value for one step
TIME_PERIODS = 60
# The steps to take from one segment to the next; if this value is equal to
# TIME_PERIODS, then there is no overlap between the segments
STEP_DISTANCE = 20


def read_data(file_path):
    column_names = ['user_id', 'type', 'photo number',
                    'nose_x', 'nose_y',
                    'neck_x', 'neck_y',
                    'shoulderR_x', 'shoulderR_y',
                    'elbowR_x', 'elbowR_y',
                    'handR_x', 'handR_y',
                    'shoulderL_x', 'shoulderL_y',
                    'elbowL_x', 'elbowL_y',
                    'handL_x', 'handL_y',
                    'ass_x', 'ass_y',
                    'legR_x', 'legR_y',
                    'kneeR_x', 'kneeR_y',
                    'feetR_x', 'feetR_y',
                    'legL_x', 'legL_y',
                    'kneeL_x', 'kneeL_y',
                    'feetL_x', 'feetL_y',
                    'eyeR_x', 'eyeR_y',
                    'eyeL_x', 'eyeL_y',
                    'earR_x', 'earR_y',
                    'earL_x', 'earL_y',
                    'footBoardR1_x', 'footBoardR1_y',
                    'footBoardR2_x', 'footBoardR2_y',
                    'footBoardR3_x', 'footBoardR3_y',
                    'footBoardL1_x', 'footBoardL1_y',
                    'footBoardL2_x', 'footBoardL2_y',
                    'footBoardL3_x', 'footBoardL3_y']
    df = pd.read_csv(file_path,
                     header=None,
                     names=column_names)
    # Last column has a ";" character which must be removed ...
    df['footBoardL3_y'].replace(regex=True, inplace=True, to_replace=r';', value=r'')
    # ... and then this column must be transformed to float explicitly
    # df['footBoardL3_y'] = df['footBoardL3_y'].apply(convert_to_float)
    # This is very important otherwise the model will not fit and loss
    # will show up as NAN
    df.dropna(axis=0, how='any', inplace=True)
    return df


def convert_to_float(x):
    try:
        return np.float(x)
    except BaseException:
        return np.nan


def show_basic_dataframe_info(dataframe):
    # Shape and how many rows and columns
    print('Number of columns in the dataframe: %i' % (dataframe.shape[1]))
    print('Number of rows in the dataframe: %i\n' % (dataframe.shape[0]))


# Load data set containing all the data from csv
df = read_data('/home/louisme/PycharmProjects/LSTM/LSTMDataset.txt')
show_basic_dataframe_info(df)
df.head(20)

# Show how many training examples exist for each of the six activities
df['type'].value_counts().plot(kind='bar', title='Training Examples by Activity Type')
# plt.show()
# Better understand how the recordings are spread across the different
# users who participated in the study
df['user_id'].value_counts().plot(kind='bar', title='Training Examples by User')
# plt.show()

# Define column name of the label vector
LABEL = 'TypeEncoded'
# Transform the labels from String to Integer via LabelEncoder
le = preprocessing.LabelEncoder()
# Add a new column to the existing DataFrame with the encoded values
df[LABEL] = le.fit_transform(df['type'].values.ravel())

df_train = read_data('/home/louisme/PycharmProjects/LSTM/LSTMDataset_train.txt')
df_train[LABEL] = le.fit_transform(df_train['type'].values.ravel())
df_test = read_data('/home/louisme/PycharmProjects/LSTM/LSTMDataset_test.txt')
df_test[LABEL] = le.fit_transform(df_test['type'].values.ravel())


def create_segments_and_labels(df, time_steps, step, label_name):
    nfeatures = 50
    # Number of steps to advance in each iteration (for me, it should always
    # be equal to the time_steps in order to have no overlap between segments)
    # step = time_steps
    segments = []
    labels = []
    for i in range(0, len(df) - time_steps, step):
        nose_x = df['nose_x'].values[i: i + time_steps]
        nose_y = df['nose_y'].values[i: i + time_steps]
        neck_x = df['neck_x'].values[i: i + time_steps]
        neck_y = df['neck_y'].values[i: i + time_steps]
        shoulderr_x = df['shoulderR_x'].values[i: i + time_steps]
        shoulderr_y = df['shoulderR_y'].values[i: i + time_steps]
        elbowr_x = df['elbowR_x'].values[i: i + time_steps]
        elbowr_y = df['elbowR_y'].values[i: i + time_steps]
        handr_x = df['handR_x'].values[i: i + time_steps]
        handr_y = df['handR_y'].values[i: i + time_steps]
        shoulderl_x = df['shoulderL_x'].values[i: i + time_steps]
        shoulderl_y = df['shoulderL_y'].values[i: i + time_steps]
        elbowl_x = df['elbowL_x'].values[i: i + time_steps]
        elbowl_y = df['elbowL_y'].values[i: i + time_steps]
        handl_x = df['handL_x'].values[i: i + time_steps]
        handl_y = df['handL_y'].values[i: i + time_steps]
        ass_x = df['ass_x'].values[i: i + time_steps]
        ass_y = df['ass_y'].values[i: i + time_steps]
        legr_x = df['legR_x'].values[i: i + time_steps]
        legr_y = df['legR_y'].values[i: i + time_steps]
        kneer_x = df['kneeR_x'].values[i: i + time_steps]
        kneer_y = df['kneeR_y'].values[i: i + time_steps]
        feetr_x = df['feetR_x'].values[i: i + time_steps]
        feetr_y = df['feetR_y'].values[i: i + time_steps]
        legl_x = df['legL_x'].values[i: i + time_steps]
        legl_y = df['legL_y'].values[i: i + time_steps]
        kneel_x = df['kneeL_x'].values[i: i + time_steps]
        kneel_y = df['kneeL_y'].values[i: i + time_steps]
        feetl_x = df['feetL_x'].values[i: i + time_steps]
        feetl_y = df['feetL_y'].values[i: i + time_steps]
        eyer_x = df['eyeR_x'].values[i: i + time_steps]
        eyer_y = df['eyeR_y'].values[i: i + time_steps]
        eyel_x = df['eyeL_x'].values[i: i + time_steps]
        eyel_y = df['eyeL_y'].values[i: i + time_steps]
        earr_x = df['earR_x'].values[i: i + time_steps]
        earr_y = df['earR_y'].values[i: i + time_steps]
        earl_x = df['earL_x'].values[i: i + time_steps]
        earl_y = df['earL_y'].values[i: i + time_steps]
        footboardr1_x = df['footBoardR1_x'].values[i: i + time_steps]
        footboardr1_y = df['footBoardR1_y'].values[i: i + time_steps]
        footboardr2_x = df['footBoardR2_x'].values[i: i + time_steps]
        footboardr2_y = df['footBoardR2_y'].values[i: i + time_steps]
        footboardr3_x = df['footBoardR3_x'].values[i: i + time_steps]
        footboardr3_y = df['footBoardR3_y'].values[i: i + time_steps]
        footboardl1_x = df['footBoardL1_x'].values[i: i + time_steps]
        footboardl1_y = df['footBoardL1_y'].values[i: i + time_steps]
        footboardl2_x = df['footBoardL2_x'].values[i: i + time_steps]
        footboardl2_y = df['footBoardL2_y'].values[i: i + time_steps]
        footboardl3_x = df['footBoardL3_x'].values[i: i + time_steps]
        footboardl3_y = df['footBoardL3_y'].values[i: i + time_steps]

        # Retrieve the most often used label in this segment
        label = stats.mode(df[label_name][i: i + time_steps])[0][0]
        segments.append([nose_x, nose_y, neck_x, neck_y, shoulderr_x, shoulderr_y, elbowr_x, elbowr_y,
                         handr_x, handr_y, shoulderl_x, shoulderl_y, elbowl_x, elbowl_y, handl_x, handl_y,
                         ass_x, ass_y, legr_x, legr_y, kneer_x, kneer_y, feetr_x, feetr_y, legl_x, legl_y,
                         kneel_x, kneel_y, feetl_x, feetl_y, eyer_x, eyer_y, eyel_x, eyel_y, earr_x, earr_y,
                         earl_x, earl_y, footboardr1_x, footboardr1_y, footboardr2_x, footboardr2_y,
                         footboardr3_x, footboardr3_y, footboardl1_x, footboardl1_y, footboardl2_x, footboardl2_y,
                         footboardl3_x, footboardl3_y])
        labels.append(label)
    # Bring the segments into a better shape
    reshaped_segments = np.asarray(segments, dtype=np.float32).reshape(-1, time_steps, nfeatures)
    labels = np.asarray(labels)

    return reshaped_segments, labels


x_train, y_train = create_segments_and_labels(df_train, TIME_PERIODS, STEP_DISTANCE, LABEL)
print('x_train shape: ', x_train.shape)
print(x_train.shape[0], 'training samples')
print('y_train shape: ', y_train.shape)
print(y_train)

# Set input & output dimensions
num_time_periods, num_sensors = x_train.shape[1], x_train.shape[2]
num_classes = le.classes_.size
print(list(le.classes_))

# keras can only support a one dimension data, reshape to 60*30=3000
input_shape = (num_time_periods * num_sensors)
x_train = x_train.reshape(x_train.shape[0], input_shape)
print('x_train shape：', x_train.shape)
print('input_shape：', input_shape)
# convert to keras accept datatype
x_train = x_train.astype('float32')
y_train = y_train.astype('float32')
y_train_hot = np_utils.to_categorical(y_train, num_classes)
print('New y_train shape: ', y_train_hot.shape)

model_m = Sequential()
# Remark: since coreml cannot accept vector shapes of complex shape like
# [80,3] this workaround is used in order to reshape the vector internally
# prior feeding it into the network
model_m.add(Reshape((TIME_PERIODS, 50), input_shape=(input_shape,)))
model_m.add(Dense(100, activation='relu'))
model_m.add(Dense(100, activation='relu'))
model_m.add(Dense(100, activation='relu'))
model_m.add(Flatten())
model_m.add(Dense(num_classes, activation='softmax'))
print(model_m.summary())

callbacks_list = [
    keras.callbacks.ModelCheckpoint(
        filepath='best_model.{epoch:02d}-{val_loss:.2f}.h5',
        monitor='val_loss', save_best_only=True),
    keras.callbacks.EarlyStopping(monitor='acc', patience=1)
]

model_m.compile(loss='categorical_crossentropy',
                optimizer='adam', metrics=['accuracy'])

# Hyper-parameters
BATCH_SIZE = 400
EPOCHS = 50

# Enable validation to use ModelCheckpoint and EarlyStopping callbacks.
history = model_m.fit(x_train,
                      y_train_hot,
                      batch_size=BATCH_SIZE,
                      epochs=EPOCHS,
                      callbacks=callbacks_list,
                      validation_split=0.2,
                      verbose=1)

plt.figure(figsize=(6, 4))
plt.plot(history.history['acc'], 'r', label='Accuracy of training data')
plt.plot(history.history['val_acc'], 'b', label='Accuracy of validation data')
plt.plot(history.history['loss'], 'r--', label='Loss of training data')
plt.plot(history.history['val_loss'], 'b--', label='Loss of validation data')
plt.title('Model Accuracy and Loss')
plt.ylabel('Accuracy and Loss')
plt.xlabel('Training Epoch')
plt.ylim(0)
plt.legend()
plt.show()

# Print confusion matrix for training data
y_pred_train = model_m.predict(x_train)
# Take the class with the highest probability from the train predictions
max_y_pred_train = np.argmax(y_pred_train, axis=1)
print(classification_report(y_train, max_y_pred_train))
