from __future__ import absolute_import
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
class Server_Python:
    def __init__(self, Host, Port):
        self.Count =0
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
        self.storage =self. firebase.storage()
        self.auth =self. firebase.auth()
        self.email = "baoquocitf@gmail.com"
        self.password = "123258zxc"
        self.user = self.auth.sign_in_with_email_and_password(self.email, self.password)
        self.period = {
            1: ['7:00', '7:50'], 2: ['8:00', '8:50'], 3: ['9:00', '9:50'], 4: ['10:00', '10:50'], 5: ['11:00', '11:50'],
            6: ['12:30', '13:20'], 7: ['13:30', '14:20'], 8: ['14:30', '15:20'], 9: ['15:30', '16:20'],
            10: ['16:30', '17:20']
        }
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
        if best_class_probabilities > 0.9:
            name = self.class_names[best_class_indices[0]]
            self.send_data(client_socket, name)
            self.send_fileBase(name,data)
            client_socket.close()
        else:
            name = "Unknown"
            self.send_data(client_socket, name)
            self.send_fileBase(name, data)
            client_socket.close()
        print(name)


    def send_data(self, client_socket, data):
        client_socket.sendall(data.encode())

    def Start(self, client_socket, client_addr):
        while True:
            try:
                self.recv_data(client_socket)
            except:
                pass

    def multi_Client(self):
        print('Server start :')
        while True:
            client_socket, client_addr = self.server_socket.accept()
            thread = Thread(target=self.Start, args=(client_socket, client_addr))
            thread.start()

    def send_fileBase(self, id,frame):
        date_now = datetime.datetime.now()
        dt = date_now.strftime("%d/%m/%Y :%H:%M")
        if id != "Unknown":

            path = f'Student/{id}'
            student = self.database.child(path).get()
            student = student.val()
            print(student['name'])
            self.Count+=1
            name_img  = f'User{self.Count}.png'
            cv2.imwrite(name_img, frame)
            self.storage.child(name_img).put(name_img)
            imageUrl = self.storage.child(name_img).get_url(name_img)
            print(imageUrl)
            data = {"avatar": imageUrl, "name": student['name'], "time": dt}
            self.database.child("Users").child("user" + str(self.Count)).set(data)
            os.remove(name_img)
        else:
            self.Count += 1
            name_img = f'User{self.Count}.png'
            cv2.imwrite(name_img, frame)
            self.storage.child(name_img).put(name_img)
            imageUrl = self.storage.child(name_img).get_url(name_img)
            print(imageUrl)
            data = {"avatar": imageUrl, "name": id, "time": dt}
            self.database.child("Users").child("user" + str(self.Count)).set(data)
            os.remove(name_img)
    def get_Count(self):
        data = self.database.child('Users').get()
        for i in data:
            self.Count +=1

if __name__ == '__main__':
    main = Server_Python('192.168.1.9',54321)
    main.get_Count()
    main.multi_Client()
