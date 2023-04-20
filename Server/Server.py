from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import facenet

import numpy as np
import cv2
import pickle
import socket
import struct
from threading import Thread


class Server_Python:
    def __init__(self, Host, Port):
        self.Host = Host
        self.Port = Port
        self.BUFFER_SIZE = 4096
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))
        self.server_socket.listen()
        self.CLASSIFIER_PATH = 'Models/facemodel.pkl'
        self.FACENET_MODEL_PATH = 'Models/20180402-114759.pb'
        self.INPUT_IMAGE_SIZE = 160
        with open(self.CLASSIFIER_PATH, 'rb') as file:
            self.model, self.class_names = pickle.load(file)
        print("Custom Classifier, Successfully loaded")
        with tf.Graph().as_default():
            # Cai dat GPU neu co
            self.gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.6)
            self.sess = tf.compat.v1.Session(
                config=tf.compat.v1.ConfigProto(gpu_options=self.gpu_options, log_device_placement=False))

            with self.sess.as_default():
                # Load model MTCNN phat hien khuon mat
                print('Loading feature extraction model')
                facenet.load_model(self.FACENET_MODEL_PATH)
                self.images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
                self.embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
                self.phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
                self.embedding_size = self.embeddings.get_shape()[1]

    def recv_data(self, client_socket):
        data_len = struct.unpack("I", client_socket.recv(struct.calcsize("I")))[0]
        received_data = b""
        while len(received_data) < data_len:
            recv_data = client_socket.recv(data_len - len(received_data))
            if not recv_data:
                break
            received_data += recv_data
        data = pickle.loads(received_data)
        scaled = cv2.resize(data, (self.INPUT_IMAGE_SIZE, self.INPUT_IMAGE_SIZE),
                            interpolation=cv2.INTER_CUBIC)
        scaled = facenet.prewhiten(scaled)
        scaled_reshape = scaled.reshape(-1, self.INPUT_IMAGE_SIZE, self.INPUT_IMAGE_SIZE, 3)
        feed_dict = {self.images_placeholder: scaled_reshape, self.phase_train_placeholder: False}
        emb_array = self.sess.run(self.embeddings, feed_dict=feed_dict)
        predictions = self.model.predict_proba(emb_array)
        best_class_indices = np.argmax(predictions, axis=1)
        best_class_probabilities = predictions[
            np.arange(len(best_class_indices)), best_class_indices]
        best_name = self.class_names[best_class_indices[0]]
        if best_class_probabilities > 0.8:
            name = self.class_names[best_class_indices[0]]
        else:
            name = "Unknown"
        print(name)

    def Start(self, client_socket, client_addr):
        while True:
            try:
                self.recv_data(client_socket)
            except:
                pass

    def multi_Client(self):
        while True:
            client_socket, client_addr = self.server_socket.accept()
            thread = Thread(target=self.Start, args=(client_socket, client_addr))
            thread.start()
    def send_fileBase(self,id):
        pass


if __name__ == '__main__':
    Server_Python('192.168.1.9', 12345).multi_Client()
