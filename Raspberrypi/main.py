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
from PIL import Image, ImageTk


class MainGUI:
    def __init__(self):
        img = cv2.imread('PBL5.png')
        img = cv2.resize(img, (480, 320))
        cv2.imwrite('abc.png', img)
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.attributes('-fullscreen', False))

        self.self_Label = tk.Label(self.root, text='Phần mền điểm danh bằng nhận diện khuôn mặt',
                                   font=('Time New Roman', 20, 'bold'))
        self.self_Label.pack()

        with tf.Graph().as_default():
            self.gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=1)
            self.sess = tf.compat.v1.Session(
                config=tf.compat.v1.ConfigProto(gpu_options=self.gpu_options, log_device_placement=False))
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = align.detect_face.create_mtcnn(self.sess, 'align')
        self.camera = VideoStream(src=0).start()
        img = Image.open("PBL5.png")
        background_image = ImageTk.PhotoImage(img)
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)

        # Tạo một đối tượng Label để đặt hình nền
        self.background_label = tk.Label(self.root, image=background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.button = tk.Button(self.root, text="Điểm Danh", command=self.show_Camera_Hide_Main, bg=color_hex,
                                font=('Time New Roman', 10, 'bold'))
        self.button.place(relx=0.3, rely=0.5, anchor=tk.CENTER, width=100, height=50)
        self.root.mainloop()

    def show_Camera_Hide_Main(self):
        self.camera_View = CameraGUI(self.root, self.pnet, self.rnet, self.onet, self.camera)
        self.root.withdraw()


if __name__ == '__main__':
    MainGUI()

