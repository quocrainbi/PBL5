import socket
import time

import tensorflow as tf
import align.detect_face
import cv2
import numpy as np
from threading import Thread
import pickle
import facenet
import pyrebase
import requests
import datetime
import os
class Server_Mobie:
    def __init__(self, Host, Port):
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
        self.INPUT_IMAGE_SIZE = 160
        self.Host = Host
        self.Port = Port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.Host, self.Port))
        self.server_socket.listen()
        self.MINSIZE = 100
        self.THRESHOLD = [0.6, 0.7, 0.7]
        self.FACTOR = 0.709
        self.CLASSIFIER_PATH = 'Models/facemodel.pkl'
        self.FACENET_MODEL_PATH = 'Models/20180402-114759.pb'
        with open(self.CLASSIFIER_PATH, 'rb') as file:
            self.model, self.class_names = pickle.load(file)
        with tf.Graph().as_default():
            self.gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=1)
            self.sess = tf.compat.v1.Session(
                config=tf.compat.v1.ConfigProto(gpu_options=self.gpu_options, log_device_placement=False))
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = align.detect_face.create_mtcnn(self.sess, 'align')
                facenet.load_model(self.FACENET_MODEL_PATH)
                self.images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
                self.embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
                self.phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
                self.embedding_size = self.embeddings.get_shape()[1]

    def recv_data(self, client_socket):
        count =0
        count_face =0
        data = b''
        while True:
            packet = client_socket.recv(4096)
            if not packet:
                break
            data += packet
        print(data)
        if data != b'':
            path='CheckNow'
            checknow = self.database.child(path).get()
            checknow = checknow.val()
            url = checknow['url']
            print(url)
            self.download_image_from_url(url)
            frame = cv2.imread('tmp.jpg')
            bounding_boxes, _ = align.detect_face.detect_face(frame, self.MINSIZE, self.pnet, self.rnet, self.onet,
                                                          self.THRESHOLD, self.FACTOR)
            faces_found = bounding_boxes.shape[0]
            print(faces_found)

            if faces_found > 0:
                det = bounding_boxes[:, 0:4]
                bb = np.zeros((faces_found, 4), dtype=np.int32)
                for i in range(faces_found):
                    bb[i][0] = det[i][0]
                    bb[i][1] = det[i][1]
                    bb[i][2] = det[i][2]
                    bb[i][3] = det[i][3]
                    #cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)
                    cropped = frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :]
                    scaled = cv2.resize(cropped, (self.INPUT_IMAGE_SIZE, self.INPUT_IMAGE_SIZE),
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
                        #self.send_data(client_socket, name)
                        self.send_fileBase(name,cropped)
                        count += 1
                    else:
                        name = "Unknown"
                        #self.send_data(client_socket, name)
                        #   self.send_fileBase(name, data)
                    print(name)

        if count >0 and  faces_found!=0:
            self.send_end()
        client_socket.close()

    def send_end(self):
        self.database.child('check').set(True)
    def download_image_from_url(self,url):
        response = requests.get(url)
        with open('tmp.jpg','wb') as file:
            file.write(response.content)
    def Start(self, client_socket, client_addr):
        self.recv_data(client_socket)

    def multi_Client(self):
        print('Server mobie start :')
        while True:
            client_socket, client_addr = self.server_socket.accept()
            print(client_socket)
            print(client_addr)
            thread = Thread(target=self.Start, args=(client_socket, client_addr))
            thread.start()

    def send_fileBase(self, id, frame):
        date_now = datetime.datetime.now()
        dt = date_now.strftime("%d/%m/%Y :%H:%M")
        if id != "Unknown":

            path = f'Student/{id}'
            student = self.database.child(path).get()
            student = student.val()
            self.Count = self.get_Count()
            name_img = f'User{self.Count+1}.jpg'
            print(name_img)
            cv2.imwrite(name_img, frame)
            self.storage.child(name_img).put(name_img)
            imageUrl = self.storage.child(name_img).get_url(name_img)
            print(imageUrl)
            data = {"avatar": imageUrl, "id":int(id),"name": student['name'], "time": dt}
            self.database.child("Users").child("user" + str(self.Count+1)).set(data)
            self.database.child("UserCheck").child("usercheck" + str(self.Count + 1)).set(data)
            os.remove(name_img)
        else:
            self.Count = self.get_Count()
            name_img = f'User{self.Count+1}.jpg'
            cv2.imwrite(name_img, frame)
            self.storage.child(name_img).put(name_img)
            imageUrl = self.storage.child(name_img).get_url(name_img)
            print(imageUrl)
            data = {"avatar": imageUrl, "id":id,"name": id, "time": dt}
            self.database.child("Users").child("user" + str(self.Count+1)).set(data)
            os.remove(name_img)
    def get_Count(self):
        self.Count = 0
        data = self.database.child('Users').get()
        for i in data:
            self.Count += 1
        tmp = self.Count
        return tmp


