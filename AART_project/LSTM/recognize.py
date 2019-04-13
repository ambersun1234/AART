import tensorflow as tf
import pandas as pd
import numpy as np


def recognize(txt_path, pb_file_path):
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
    df = pd.read_csv(txt_path, header=None, names=columns)
    df['feetL_y'].replace(regex=True, inplace=True, to_replace=r';', value=r'')

    time_steps = 60
    # 50 data for one input
    n_features = 24
    # step is for overlapping
    step = 20
    segments = []
    for i in range(0, len(df) - time_steps):
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

        segments.append([neck_x, neck_y, shoulderr_x, shoulderr_y, elbowr_x, elbowr_y,
                         handr_x, handr_y, shoulderl_x, shoulderl_y, elbowl_x, elbowl_y, handl_x, handl_y,
                         ass_x, ass_y, kneer_x, kneer_y, feetr_x, feetr_y,
                         kneel_x, kneel_y, feetl_x, feetl_y])

    reshaped_segments = np.asarray(segments, dtype=np.float32).reshape(-1, time_steps, n_features)
    with tf.Graph().as_default():
        graph0 = tf.GraphDef()
        with open(pb_file_path, mode='rb') as f:
            graph0.ParseFromString(f.read())
            tf.import_graph_def(graph0, name='')
        with tf.Session() as sess:
            init = tf.global_variables_initializer()
            sess.run(init)
            input = sess.graph.get_tensor_by_name('input:0')
            # sess.graph.
            print('sumTensor is : ', input)
            print(sess.run('y_', feed_dict={input: reshaped_segments}))


recognize("LSTMDatasetUse.txt", "./save-2019-04-12-2001/frozen_har.pb")
