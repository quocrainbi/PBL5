import tkinter as tk
from tkinter import  messagebox
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
class CameraGUI:
    def __init__(self, main_gui,pnet,rnet,onet,camera):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        self.count = 1
        self.HOST = '10.10.28.109'
        self.PORT = 12345
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
        self.label.pack(pady = 100)
        self.label_huong_dan = tk.Label(self.root,text = 'Vui lòng để khuôn mặt bạn gần camera',
                                        font=('Time New Roman',20,'bold'),bg=color_hex)
        self.label_huong_dan.pack(pady = 10)
        self.back_button = tk.Button(self.root, text="Back", command=self.on_back_button_click,bg=color_hex)
        self.back_button.pack()
        self.thread = threading.Thread(target=self.show_frame)
        self.thread.daemon = True
        self.thread.start()
        self.thread_rev = threading.Thread(target=self.recv_Server)
        self.thread_rev.daemon = True
        self.thread_rev.start()
        
        self.root.configure(bg=color_hex)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def show_frame(self):
        frame = self.camera.read()
        frame = imutils.resize(frame, width=600)
        frame = cv2.flip(frame, 1)
        bounding_boxes, _ = align.detect_face.detect_face(frame, self.MINSIZE, self.pnet, self.rnet, self.onet, self.THRESHOLD, self.FACTOR)
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
                if x1 > 0 and y1>0 and x2>0 and y2>2 :
                    self.send_Server(frame[y1:y2, x1:x2])

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)
        self.root.after(1, self.show_frame)
        
    def send_Server(self,frame):
        data = pickle.dumps(frame)
        self.s.sendall(struct.pack("I", len(data)))
        self.s.sendall(data)
        
    def recv_Server(self):
        dict = {}
        dict["Unknown"]=1
        while True:
            data_rev = self.s.recv(1024)
            string = data_rev.decode('utf-8')
            print(string)
            if string != "Unknown":
                self.root.after(3000, lambda : self.show_messagebox(string))
                break
            elif  dict["Unknown"]==10:
                self.root.after(3000, lambda : self.show_messagebox('Unknown'))
                break
            dict["Unknown"] += 1
                
                
        
    def on_closing(self):
        self.s.close()
        self.root.destroy()
        self.main_gui.deiconify()
    def show_messagebox(self,data):
        self.root.destroy()
        message = Message(self.main_gui,data)
    def on_back_button_click(self):
        self.s.close()
        self.root.destroy()
        self.main_gui.deiconify()
