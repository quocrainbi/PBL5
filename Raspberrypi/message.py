import threading
import tkinter as tk
# import RPi.GPIO as GPIO


class Message:
    def __init__(self, main_gui, data):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setwarnings(False)
        # GPIO.setup(26, GPIO.OUT)
        # GPIO.setup(5, GPIO.OUT)
        # GPIO.setup(6, GPIO.OUT)
        self.main_gui = main_gui
        self.root = tk.Toplevel(self.main_gui)
        self.root.attributes('-fullscreen', True)
        self.root.after(20000, self.on_closing)
        print(data)
        if data == 'Fake':
            self.data_Fake()
        elif data == 'Unknown':
            self.data_False()
        else:
            self.data_True(data)
        self.button = tk.Button(self.root, text="OK", command=self.on_closing, bg=color_hex)
        self.button.pack(expand=True)
        self.root.configure(bg=color_hex)
        self.root.mainloop()

    # def error_Message(self):
    #     count = 0
    #     while count <= 5:
    #         GPIO.output(5, GPIO.HIGH)
    #         time.sleep(1)
    #         GPIO.output(5, GPIO.LOW)
    #         time.sleep(1)
    #         count += 1
    #
    # def fake_Message(self):
    #     count = 0
    #     while count <= 5:3
    #         GPIO.output(26, GPIO.HIGH)
    #         GPIO.output(5, GPIO.HIGH)
    #         time.sleep(1)
    #         GPIO.output(26, GPIO.LOW)
    #         GPIO.output(5, GPIO.LOW)
    #         time.sleep(1)
    #         count += 1
    # def true_Message(self):
    #     GPIO.output(6, GPIO.HIGH)
    #     time.sleep(5)
    #     GPIO.output(6, GPIO.LOW)


    def data_True(self, data):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        data = 'Sinh viên ' + data + '\nđiểm danh thành công'
        self.label_huong_dan = tk.Label(self.root, text=data,
                                        font=('Time New Roman', 20, 'bold'), bg=color_hex)
        self.label_huong_dan.place(relx=0, rely=0)
        # threading_Warning = threading.Thread(target=self.true_Message())
        # threading_Warning.start()

    def data_False(self):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        data = 'Bạn không thuộc \nsinh viên lớp này'
        self.label_huong_dan = tk.Label(self.root, text=data,
                                        font=('Time New Roman', 20, 'bold'), bg=color_hex)
        self.label_huong_dan.place(relx=0, rely=0)
        # threading_Warning = threading.Thread(target=self.error_Message)
        # threading_Warning.start()

    def data_Fake(self):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        data = 'Chúng tôi phát hiện bạn \n đang cố gắng giả mạo ai đó'
        self.label_huong_dan = tk.Label(self.root, text=data,
                                        font=('Time New Roman', 20, 'bold'), bg=color_hex)
        self.label_huong_dan.place(relx=0, rely=0)
        # threading_Warning = threading.Thread(target=self.fake_Message)
        # threading_Warning.start()

    def on_closing(self):
        # GPIO.output(26, GPIO.LOW)
        self.root.destroy()
        self.main_gui.deiconify()
