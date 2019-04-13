import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy import stats
import tensorflow as tf
import seaborn as sns
from pylab import rcParams
from sklearn import metrics
from sklearn.model_selection import train_test_split


sns.set(style='whitegrid', palette='muted', font_scale=1.5)

rcParams['figure.figsize'] = 14, 8

RANDOM_SEED = 42
columns = ['user_id', 'activity', 'photo number',
           'neck_x', 'neck_y',
           'shoulderR_x', 'shoulderR_y',
           'elbowR_x', 'elbowR_y',
           'handR_x', 'handR_y',
           'shoulderL_x', 'shoulderL_y',
           'elbowL_x', 'elbowL_y',
           'handL_x', 'handL_y',
           'ass_x', 'ass_y',
           'kneeR_x', 'kneeR_y',
           'feetR_x', 'feetR_y',
           'kneeL_x', 'kneeL_y',
           'feetL_x', 'feetL_y']
df = pd.read_csv('/home/louisme/PycharmProjects/LSTM/LSTMDataset.txt', header=None, names=columns)
df['feetL_y'].replace(regex=True, inplace=True, to_replace=r';', value=r'')
df.head()
# 30FPS * 2sec = 60
time_steps = 60
# 50 data for one input
N_FEATURES = 24
# step is for overlapping
step = 20
segments = []
labels = []
for i in range(0, len(df) - time_steps, step):
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
    kneer_x = df['kneeR_x'].values[i: i + time_steps]
    kneer_y = df['kneeR_y'].values[i: i + time_steps]
    feetr_x = df['feetR_x'].values[i: i + time_steps]
    feetr_y = df['feetR_y'].values[i: i + time_steps]
    kneel_x = df['kneeL_x'].values[i: i + time_steps]
    kneel_y = df['kneeL_y'].values[i: i + time_steps]
    feetl_x = df['feetL_x'].values[i: i + time_steps]
    feetl_y = df['feetL_y'].values[i: i + time_steps]

    label = stats.mode(df['activity'][i: i + time_steps])[0][0]
    segments.append([neck_x, neck_y, shoulderr_x, shoulderr_y, elbowr_x, elbowr_y,
                     handr_x, handr_y, shoulderl_x, shoulderl_y, elbowl_x, elbowl_y, handl_x, handl_y,
                     ass_x, ass_y, kneer_x, kneer_y, feetr_x, feetr_y,
                     kneel_x, kneel_y, feetl_x, feetl_y])
    labels.append(label)
# print(np.array(segments).shape)
reshaped_segments = np.asarray(segments, dtype=np.float32).reshape(-1, time_steps, N_FEATURES)
labels = np.asarray(pd.get_dummies(labels), dtype=np.float32)
# print(reshaped_segments.shape)
X_train, X_test, y_train, y_test = train_test_split(reshaped_segments, labels, test_size=0.2, random_state=RANDOM_SEED)

# Building the model
# Number of class
N_CLASSES = 3
# for a matrix size
N_HIDDEN_UNITS = 64


def create_lstm_model(inputs):
    W = {
        'hidden': tf.Variable(tf.random_normal([N_FEATURES, N_HIDDEN_UNITS])),
        'output': tf.Variable(tf.random_normal([N_HIDDEN_UNITS, N_CLASSES]))
    }
    biases = {
        'hidden': tf.Variable(tf.random_normal([N_HIDDEN_UNITS], mean=1.0)),
        'output': tf.Variable(tf.random_normal([N_CLASSES]))
    }

    X = tf.transpose(inputs, [1, 0, 2])
    X = tf.reshape(X, [-1, N_FEATURES])
    hidden = tf.nn.relu(tf.matmul(X, W['hidden']) + biases['hidden'])
    hidden = tf.split(hidden, time_steps, 0)

    # Stack 2 LSTM layers
    lstm_layers = [tf.contrib.rnn.BasicLSTMCell(N_HIDDEN_UNITS, forget_bias=1.0) for _ in range(2)]
    lstm_layers = tf.contrib.rnn.MultiRNNCell(lstm_layers)

    outputs, _ = tf.contrib.rnn.static_rnn(lstm_layers, hidden, dtype=tf.float32)

    # Get output for the last time step
    lstm_last_output = outputs[-1]

    return tf.matmul(lstm_last_output, W['output']) + biases['output']


tf.reset_default_graph()

X = tf.placeholder(tf.float32, [None, time_steps, N_FEATURES], name="input")
Y = tf.placeholder(tf.float32, [None, N_CLASSES])
pred_Y = create_lstm_model(X)

pred_softmax = tf.nn.softmax(pred_Y, name="y_")
L2_LOSS = 0.0015

l2 = L2_LOSS * sum(tf.nn.l2_loss(tf_var) for tf_var in tf.trainable_variables())

loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred_Y, labels=Y)) + l2

LEARNING_RATE = 0.0025

optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE).minimize(loss)

correct_pred = tf.equal(tf.argmax(pred_softmax, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, dtype=tf.float32))

N_EPOCHS = 5000
BATCH_SIZE = 20
saver = tf.train.Saver()

history = dict(train_loss=[],
               train_acc=[],
               test_loss=[],
               test_acc=[])

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

train_count = len(X_train)

for i in range(1, N_EPOCHS + 1):
    for start, end in zip(range(0, train_count, BATCH_SIZE),
                          range(BATCH_SIZE, train_count + 1, BATCH_SIZE)):
        sess.run(optimizer, feed_dict={X: X_train[start:end],
                                       Y: y_train[start:end]})

    _, acc_train, loss_train = sess.run([pred_softmax, accuracy, loss], feed_dict={
        X: X_train, Y: y_train})

    _, acc_test, loss_test = sess.run([pred_softmax, accuracy, loss], feed_dict={
        X: X_test, Y: y_test})

    history['train_loss'].append(loss_train)
    history['train_acc'].append(acc_train)
    history['test_loss'].append(loss_test)
    history['test_acc'].append(acc_test)

    if i != 1 and i % 10 != 0:
        continue

    print('epoch: {} test accuracy: {} loss: {}'.format(i, acc_test, loss_test))

predictions, acc_final, loss_final = sess.run([pred_softmax, accuracy, loss], feed_dict={X: X_test, Y: y_test})

print()
print('final results: accuracy: {} loss: {}'.format(acc_final, loss_final))
# Store weights or model to disk
pickle.dump(predictions, open("predictions.p", "wb"))
pickle.dump(history, open("history.p", "wb"))
tf.train.write_graph(sess.graph_def, '.', './checkpoint/har.pbtxt')
saver.save(sess, save_path="./checkpoint/har.ckpt")
sess.close()

plt.figure(figsize=(12, 8))
plt.plot(np.array(history['train_loss']), "r--", label="Train loss")
plt.plot(np.array(history['train_acc']), "g--", label="Train accuracy")
plt.plot(np.array(history['test_loss']), "r-", label="Test loss")
plt.plot(np.array(history['test_acc']), "g-", label="Test accuracy")
plt.title("Training session's progress over iterations")
plt.legend(loc='upper right', shadow=True)
plt.ylabel('Training Progress (Loss or Accuracy values)')
plt.xlabel('Training Epoch')
plt.ylim(0)
plt.show()

LABELS = ['shooting', 'layup', 'dribble']
max_test = np.argmax(y_test, axis=1)
max_predictions = np.argmax(predictions, axis=1)
confusion_matrix = metrics.confusion_matrix(max_test, max_predictions)
plt.figure(figsize=(16, 14))
sns.heatmap(confusion_matrix, xticklabels=LABELS, yticklabels=LABELS, annot=True, fmt="d");
plt.title("Confusion matrix")
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show();