import tkinter as tk
from tkinter import messagebox
import cv2
import PIL.Image, PIL.ImageTk
from functools import partial
import threading
import socket
import pickle
import struct
from imutils.video import VideoStream
import imutils
import align.detect_face
import numpy as np
import time
from message import Message
from keras.models import load_model
import random
import f_detector


class CameraGUI:
    def __init__(self, main_gui, pnet, rnet, onet, camera):
        self.count_check = 3
        self.profile_detector = f_detector.detect_face_orientation()
        self.check_face = False
        self.questions = [
            "turn face right",
            "turn face left"]
        self.limit_try = 500
        self.limit_questions = 3
        self.IMG_SIZE = 24
        self.Eye_isopen = False
        self.Eye_isclose = False
        self.model_eye = load_model('eye_status_classifier.h5')
        self.left_eye_cascPath = 'haarcascade_lefteye_2splits.xml'
        self.right_eye_cascPath = 'haarcascade_righteye_2splits.xml'
        self.left_eye_detector = cv2.CascadeClassifier(self.left_eye_cascPath)
        self.right_eye_detector = cv2.CascadeClassifier(self.right_eye_cascPath)
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        self.count = 1
        self.HOST = '192.168.1.11'
        self.PORT = 54321
        self.MINSIZE = 100
        self.THRESHOLD = [0.6, 0.7, 0.7]
        self.FACTOR = 0.709
        self.pnet = pnet
        self.rnet = rnet
        self.onet = onet
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))
        self.main_gui = main_gui
        self.camera = camera
        self.root = tk.Toplevel(self.main_gui)
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.attributes('-fullscreen', False))
        self.label = tk.Label(self.root)
        self.label.place(relx=0.17, rely=0)
        self.label_huong_dan = tk.Label(self.root, text='Vui lòng để khuôn mặt bạn gần camera',
                                        font=('Time New Roman', 20, 'bold'), bg=color_hex)
        self.label_huong_dan.place(relx=0, rely=0.9)
        self.back_button = tk.Button(self.root, text="Back", command=self.on_back_button_click, bg=color_hex)
        self.back_button.place(relx=0.87, rely=0.9)
        self.thread_check_face = threading.Thread(target=self.check_face_oriented)
        self.thread_check_face.daemon = True
        self.thread_check_face.start()
        # self.thread = threading.Thread(target=self.show_frame)
        # self.thread.daemon = True
        # self.thread.start()
        self.thread_rev = threading.Thread(target=self.recv_Server)
        self.thread_rev.daemon = True
        self.thread_rev.start()
        self.root.configure(bg=color_hex)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self):
        print('show')
        frame = self.camera.read()
        frame = imutils.resize(frame, height=250)
        frame = cv2.flip(frame, 1)
        if self.check_face:
            bounding_boxes, _ = align.detect_face.detect_face(frame, self.MINSIZE, self.pnet, self.rnet, self.onet,
                                                              self.THRESHOLD, self.FACTOR)
            faces_found = bounding_boxes.shape[0]
            if faces_found > 1:
                cv2.putText(frame, "Only one face", (0, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            1, (255, 255, 255), thickness=1, lineType=2)
            elif faces_found > 0:
                det = bounding_boxes[:, 0:4]
                bb = np.zeros((faces_found, 4), dtype=np.int32)
                for i in range(faces_found):
                    bb[i][0] = det[i][0]
                    bb[i][1] = det[i][1]
                    bb[i][2] = det[i][2]
                    bb[i][3] = det[i][3]
                    cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)
                    x1, y1, x2, y2 = bb[i][0], bb[i][1], bb[i][2], bb[i][3]
                    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 2:
                        gray = frame[y1:y2, x1:x2]
                        if self.Eye_isopen == False or self.Eye_isclose == False:
                            self.check_Eye(gray)
                        else:
                            try:
                                self.send_Server(frame[y1:y2, x1:x2])
                            except:
                                pass
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)
        self.root.after(1, self.show_frame)

    def send_Server(self, frame):
        try:
            print('senddata')
            data = pickle.dumps(frame)
            self.s.sendall(struct.pack("I", len(data)))
            self.s.sendall(data)
        except:
            pass

    def recv_Server(self):
        try:
            while True:
                data_rev = self.s.recv(1024)
                string = data_rev.decode('utf-8')
                print(string)
                if string != "Unknown":
                    self.root.after(1, lambda: self.show_messagebox(string))
                    break
                else:
                    self.root.after(1, lambda: self.show_messagebox('Unknown'))
                    break
        except:
            pass

    def predict(self, img):
        img = cv2.resize(img, (self.IMG_SIZE, self.IMG_SIZE)).astype('float32')
        img /= 255
        img = img.reshape(1, self.IMG_SIZE, self.IMG_SIZE, 1)
        prediction = self.model_eye.predict(img)
        if prediction < 0.1:
            prediction = 'closed'
        elif prediction > 0.90:
            prediction = 'open'
        else:
            prediction = 'idk'
        return prediction

    def check_Eye(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        left_eye = self.left_eye_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )
        right_eye = self.right_eye_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )
        eyes_detected = {'left': None, 'right': None}

        for (x, y, w, h) in left_eye:
            eyes_detected['left'] = (x, y, w, h)
            tmp = self.predict(gray[y:y + h, x:x + w])
            if tmp == 'closed':
                self.Eye_isclose = True
            elif tmp == 'open':
                self.Eye_isopen = True
            print(tmp)
            break

        for (x, y, w, h) in right_eye:
            eyes_detected['right'] = (x, y, w, h)
            tmp = self.predict(gray[y:y + h, x:x + w])
            if tmp == 'closed':
                self.Eye_isclose = True
            elif tmp == 'open':
                self.Eye_isopen = True
            print(tmp)
            break
        print(eyes_detected)

    def on_closing(self):
        self.s.close()
        self.root.destroy()
        self.main_gui.deiconify()

    def show_messagebox(self, data):
        self.s.close()
        self.root.destroy()
        Message(self.main_gui, data)

    def on_back_button_click(self):
        self.s.close()
        self.root.destroy()
        self.main_gui.deiconify()

    def config_label(self, question):
        self.label_huong_dan.config(text=question)

    def check_face_oriented(self):
        dict_check = {0: False, 1: False, 2: False, 3: False}

        for i_questions in range(0, 4):
            index_question = random.randint(0, 1)
            question_tmp = self.questions[index_question]
            tmp = 0
            self.root.after(1, lambda: self.config_label(f'{i_questions}.'+question_tmp))
            for i_try in range(100):
                frame = self.camera.read()
                img = cv2.flip(frame, 1)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                box_orientation, orientation = self.profile_detector.face_orientation(gray)
                if len(orientation) != 0:
                    check_face  = self.challenge_result(question_tmp,orientation[0])
                    if check_face == 'pass':
                        tmp += 1
                        if tmp == self.count_check:
                            dict_check[i_questions] = True
                            break
                self.root.after(1, lambda: self.Show_img(frame))
            if dict_check[i_questions] == False:
                self.root.after(1, lambda: self.show_messagebox('Fake'))
                break
        if dict_check[0] == True and dict_check[1] == True and dict_check[2] == True and dict_check[3   ] == True :
            self.config_label('Vui lòng để mặt chính giữa')
            self.check_face = True
            self.show_frame()


    def Show_img(self, frame):
        frame = imutils.resize(frame, height=250)
        frame = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

    def challenge_result(self, question, oriented):
        if question == "turn face right":
            if oriented == "right":
                challenge = "pass"
            else:
                challenge = "fail"

        elif question == "turn face left":
            if oriented == "left":
                challenge = "pass"
            else:
                challenge = "fail"
        return challenge
