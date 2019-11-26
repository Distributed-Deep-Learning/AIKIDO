"""KungFu experiment_0

KungFu requires users to make the following changes:
1. KungFu provides distributed optimizers that can wrap the original optimizer.
The distributed optimizer defines how local gradients and model weights are synchronized.
2. (Optional) In a distributed training setting, the training dataset is often partitioned.
3. (Optional) Scaling the learning rate of your local optimizer
"""

from __future__ import absolute_import, division, print_function

import logging
import os
from datetime import datetime

# kungfu imports
import kungfu as kf
import numpy as np
# tensorflow imports
import tensorflow as tf
from kungfu import current_cluster_size, current_rank
from kungfu.tensorflow.initializer import BroadcastGlobalVariablesCallback
from kungfu.tensorflow.ops import broadcast
from kungfu.tensorflow.optimizers import (PairAveragingOptimizer,
                                          SynchronousAveragingOptimizer,
                                          SynchronousSGDOptimizer)
# tf.keras imports
from tensorflow.keras import Model
from tensorflow.keras.layers import (Activation, AveragePooling2D,
                                     BatchNormalization, Conv2D, Dense,
                                     Dropout, Flatten, Input, MaxPooling2D)
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import preprocess_data
# local imports
from model_definition import Conv4_model

# Model and dataset params
save_dir = os.path.join(os.getcwd(), 'saved_models')
num_classes = 10
learning_rate = 0.01
batch_size = 32
epochs = 1


def build_optimizer(name, n_shards=1):
    # Scale learning rate according to the level of data parallelism
    optimizer = tf.keras.optimizers.SGD(learning_rate=(learning_rate *
                                                       n_shards))

    # KUNGFU: Wrap the TensorFlow optimizer with KungFu distributed optimizers.
    if name == 'sync-sgd':
        return SynchronousSGDOptimizer(optimizer, use_locking=True)
    elif name == 'async-sgd':
        return PairAveragingOptimizer(optimizer)
    elif name == 'sma':
        return SynchronousAveragingOptimizer(optimizer)
    else:
        raise RuntimeError('unknown optimizer: %s' % name)


def build_model(optimizer, x_train, num_classes):
    model = Conv4_model(x_train, num_classes)
    # Compile model using kungfu optimizer
    model.compile(loss='categorical_crossentropy',
                  optimizer=optimizer,
                  metrics=['accuracy'])
    return model


def train_model(model, model_name, x_train, x_test, y_train, y_test):
    # Pre-process dataset
    x_test = x_test.astype('float32')
    x_test /= 255

    # Convert class vectors to binary class matrices.
    y_test = tf.keras.utils.to_categorical(y_test, num_classes)

    # Train model
    print("training set size:", x_train.shape, y_train.shape)

    # calculate the offset for the data of the KungFu node
    n_shards = current_cluster_size()
    shard_id = current_rank()
    train_data_size = len(x_train)

    shard_size = train_data_size // n_shards
    data_batch_size = train_data_size // n_shards
    offset = data_batch_size * shard_id

    # extract the data for learning of the KungFu node
    print("sharding info for current worker : ",
          current_rank(), offset, offset + shard_size)
    x_node = x_train[offset:offset + shard_size]
    y_node = y_train[offset:offset + shard_size]

    callbacks = [BroadcastGlobalVariablesCallback()]

    # Save model and weights only on the rank 0 worker
    # TODO: Saving model has a bug
    # if current_rank() == 0:
    #     if not os.path.isdir(save_dir):
    #         os.makedirs(save_dir)
    #     model_path = os.path.join(
    #         save_dir, model_name, 'checkpoint-{epoch}.h5')

    #     callbacks.append(tf.keras.callbacks.ModelCheckpoint(model_path))

    # Log to tensorboard for now
    if current_rank() == 0:
        logdir = "tensorboard_logs/{}/scalars/".format(
            model_name) + datetime.now().strftime("%Y%m%d-%H%M%S")
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
        callbacks.append(tensorboard_callback)

    model.fit(x_node, y_node,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_test, y_test),
              shuffle=True,
              verbose=2,
              callbacks=callbacks)


def evaluate_trained_cifar10_model(model_name, x_test, y_test):
    model_file = os.path.join("./saved_models/", model_name)
    model = load_model(model_file)
    x_test = x_test.astype('float32')
    x_test /= 255
    y_test = keras.utils.to_categorical(y_test, num_classes)
    scores = model.evaluate(x_test, y_test, verbose=1)
    return scores


def f_data(x_train, y_train):
    x_train = x_train.astype('float32')
    x_train /= 255
    y_train = tf.keras.utils.to_categorical(y_train, num_classes)
    return x_train, y_train


if __name__ == "__main__":
    logging.basicConfig(filename="tf2_Conv4_CIFAR10_exp_0.log",
                        level=logging.DEBUG,
                        format="%(asctime)s:%(levelname)s:%(message)s")
    print("n shards here: ", current_cluster_size())
    # Load data
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    class_names = ["airplane", "automobile", "bird", "cat",
                   "deer", "dog", "frog", "horse", "ship", "truck"]
    # Pre process data
    x_train, y_train = preprocess_data.process(f_data, x_train, y_train)

    optimizer = build_optimizer('sync-sgd', n_shards=current_cluster_size())
    model = build_model(optimizer, x_train, num_classes)
    train_model(model, "Conv4_CIFAR10_exp_0", x_train, x_test, y_train, y_test)
