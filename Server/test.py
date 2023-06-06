from __future__ import division
from __future__ import print_function

import os

import tensorflow as tf
import facenet

import numpy as np
import cv2
import pickle
import socket
import struct
from threading import Thread
import datetime
import pyrebase
from Server_mobie import Server_Mobie


class Server_Python:
    def __init__(self, Host, Port):
        self.dung=0
        self.test =0
        self.Count = 0
        self.firebaseConfig = {
            'apiKey': "AIzaSyDemEX4zM6WQAYVYewOk-0y6EOTrt4Jeq4",
            'authDomain': "pbl5-c253c.firebaseapp.com",
            'databaseURL': "https://pbl5-c253c-default-rtdb.firebaseio.com",
            'projectId': "pbl5-c253c",
            'storageBucket': "pbl5-c253c.appspot.com",
            'messagingSenderId': "769387973080",
            'appId': "1:769387973080:web:14271fb1bc1478688c8aad",
            'measurementId': "G-DXRW3ZD08C"
        }
        self.firebase = pyrebase.initialize_app(self.firebaseConfig)
        self.database = self.firebase.database()
        self.storage = self.firebase.storage()
        self.auth = self.firebase.auth()
        self.email = "baoquocitf@gmail.com"
        self.password = "123258zxc"
        self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
        self.Host = Host
        self.Port = Port
        self.BUFFER_SIZE = 4096
        self.CLASSIFIER_PATH = 'Models/facemodel.pkl'
        self.FACENET_MODEL_PATH = 'Models/20180402-114759.pb'
        self.INPUT_IMAGE_SIZE = 160
        with open(self.CLASSIFIER_PATH, 'rb') as file:
            self.model, self.class_names = pickle.load(file)
        with tf.Graph().as_default():
            # Cai dat GPU neu co
            self.gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.6)
            self.sess = tf.compat.v1.Session(
                config=tf.compat.v1.ConfigProto(gpu_options=self.gpu_options, log_device_placement=False))

            with self.sess.as_default():
                facenet.load_model(self.FACENET_MODEL_PATH)
                self.images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
                self.embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
                self.phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
                self.embedding_size = self.embeddings.get_shape()[1]

    def recv_data(self,pathimg,subpath):

        data = cv2.imread(pathimg)
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
        if best_class_probabilities > 0.85:
            name = self.class_names[best_class_indices[0]]

        else:
            name = "Unknown"
        if name ==  subpath:
            self.dung+=1
        self.test+=1


    def process_images(self,directory_path):
        # Lấy danh sách thư mục con trong thư mục gốc
        subdirectories = [subdir for subdir in os.listdir(directory_path) if
                          os.path.isdir(os.path.join(directory_path, subdir))]

        for subdir in subdirectories:
            subdir_path = os.path.join(directory_path, subdir)


            # Lấy tên thư mục con
            subdir_name = os.path.basename(subdir_path)

            # Lấy danh sách tệp ảnh trong thư mục con
            image_files = [file for file in os.listdir(subdir_path) if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

            for image_file in image_files:
                image_path = os.path.join(subdir_path, image_file)

                # Đọc ảnh

                self.recv_data(image_path,subdir_name)







if __name__ == '__main__':
    main = Server_Python('192.168.9.221', 54321)
    main.process_images('data')
    print(f'Kết quả nhận dạng đúng:{main.dung}')
    print(f'Số lượng test :{main.test}')
    print(f'Phần trăm nhận dạng đúng :{main.dung/main.test}')
