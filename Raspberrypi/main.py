from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
from imutils.video import VideoStream
import imutils
import numpy as np
import cv2
import tkinter as tk
from camera_gui import CameraGUI
import align.detect_face

class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.attributes('-fullscreen', False))

        
        self.self_Label = tk.Label(self.root,text = 'Phần mền điểm danh bằng nhận diện khuôn mặt',
                                font=('Time New Roman',20,'bold'))
        self.self_Label.pack()
        self.button = tk.Button(self.root, text="Show Camera", command=self.show_Camera_Hide_Main)
        self.button.pack(expand=True)
        with tf.Graph().as_default():
            self.gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=1)
            self.sess = tf.compat.v1.Session(
                config=tf.compat.v1.ConfigProto(gpu_options=self.gpu_options, log_device_placement=False))
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = align.detect_face.create_mtcnn(self.sess, 'align')
        self.camera = VideoStream(src=0).start()    
        self.root.mainloop()

    def show_Camera_Hide_Main(self):
        self.camera_View = CameraGUI(self.root,self.pnet,self.rnet,self.onet,self.camera)
        self.root.withdraw()
        
        
if __name__ == '__main__':
    MainGUI()
