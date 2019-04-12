import tensorflow as tf
import  numpy as np
import PIL.Image as Image
from skimage import io, transform

def recognize(txt_path, pb_file_path):
    saver = tf.train.import_meta_graph('./checkpoint-2019-04-12-2001/har.ckpt.meta')
    # try:
    with tf.Session() as sess:
        saver = tf.train.import_meta_graph('./checkpoint-2019-04-12-2001/har.ckpt.meta')
        saver.restore(sess, tf.train.latest_checkpoint('./checkpoint-2019-04-12-2001'))
        print(sess.run('w1:0'))
    # except Exception:
    #     print('Load model error')
    #     exit(1)


recognize("LSTMDatasetUse.txt", "/home/louisme/PycharmProjects/LSTM/save-2019-04-12-2001/frozen_har.pb")
