import tkinter as tk
import RPi.GPIO as GPIO
class Message:
    def __init__(self,main_gui,data):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(17, GPIO.OUT)
        self.main_gui = main_gui
        self.root = tk.Toplevel(self.main_gui)
        self.root.attributes('-fullscreen', True)
        self.root.after(20000,self.on_closing)
        if data != 'Unknown':
            self.data_True(data)
        else :
            self.data_False()
            
        self.button = tk.Button(self.root, text="OK", command=self.on_closing,bg=color_hex)
        self.button.pack(expand=True)
        self.root.configure(bg=color_hex)
        self.root.mainloop()
    def error_Message(self):
        while True:
            GPIO.output(17, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(17, GPIO.LOW)
            time.sleep(1)
    def data_True(self,data):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        data = 'Sinh viên '+data+'điểm danh thành công'
        self.label_huong_dan = tk.Label(self.root,text = data,
                                        font=('Time New Roman',20,'bold'),bg=color_hex)
        self.label_huong_dan.pack(pady = 10)
    def data_False(self):
        r, g, b = 0, 91, 187
        color_hex = '#%02x%02x%02x' % (r, g, b)
        data = 'Bạn không thuộc sinh viên lơp này'
        self.label_huong_dan = tk.Label(self.root,text = data,
                                        font=('Time New Roman',20,'bold'),bg=color_hex)
        self.label_huong_dan.pack(pady = 10)
    def on_closing(self):
        self.root.destroy()
        self.main_gui.deiconify()