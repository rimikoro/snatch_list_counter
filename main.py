import cv2
import ctypes
import numpy as np
import winsound
from tkinter import *
from tkinter import messagebox
from PIL import ImageGrab, ImageTk

class SnatchCounter(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        
        self.master.title("SnatchCounter")
        self.master.geometry("300x200")
        self.master.resizable(False, False)
        self.master.attributes("-toolwindow", 1)
        
        self.temp = cv2.imread("temp/snatch_list.png")
        self.capture_frag = False
        self.snatch_frag = False
        self.count = 0
        self.x = 100
        self.y = 100
        self.threshold = 0.9
        
        self.menuber = Menu(self.master)
        self.master.config(menu=self.menuber)
        self.menuber.add_command(label="キャプチャ枠表示", command=self.capture_window)
        self.menuber.add_command(label="画像を保存", state="disabled", command=self.img_save)
        
        self.create_widget()

    def create_widget(self):
        self.check_button = Button(self.master, text="確認", command=self.preview, state="disabled")
        self.check_button.place(x=210, y=10)
        
        self.canvas = Canvas(self.master, width=180, height=50, bg="red")
        self.canvas.place(x=10, y=10)
        
        label = Label(self.master, text="目標回数 :")
        label.place(x=10, y=74)
        
        self.entry = Entry(self.master, width=10)
        self.entry.place(x=100, y=75)
        
        self.label = Label(self.master, text="スナッチリストを開いた数 : 0回")
        self.label.place(x=10, y=110)
        
        self.counter_button = Button(self.master, text="開始", command=self.snatchcount, state="disabled")
        self.counter_button.place(x=245, y=108)
        
        label = Label(self.master, text="閾値")
        label.place(x=210, y=75)
                
        self.spin = Spinbox(self.master, from_=0.1, to=1.0, increment=0.1, state="readonly",textvariable=DoubleVar(self.master, value=0.9), width=3)
        self.spin.place(x=250,y=78)
        
        self.stop = Button(self.master, text="停止", command=self.stop_counter, state="disabled")
        self.stop.place(x=245, y=155)
    
    def capture_window(self):
        if self.capture_frag:
            self.menuber.entryconfig(1,label="キャプチャ枠表示")
            self.capture_frag = False
            self.capture_frame.destroy()
            return
        self.capture_frag = True
        self.check_button["state"] = "normal"
        self.menuber.entryconfig(1,label="キャプチャ枠非表示")
        self.capture_frame = Toplevel(self.master, bg="snow", bd=0, highlightthickness=0)
        self.capture_frame.title("CapWin")
        self.capture_frame.geometry(f"180x50+{self.x-11}+{self.y-45}")
        self.capture_frame.resizable(False, False)
        self.capture_frame.attributes("-topmost", True)
        self.capture_frame.attributes("-transparentcolor", "snow")
        self.capture_frame.attributes("-toolwindow", 1)
        self.capture_frame.update_idletasks()
    
    def preview(self):
        self.x = self.capture_frame.winfo_rootx()
        self.y = self.capture_frame.winfo_rooty()
        self.w = self.capture_frame.winfo_width()
        self.h = self.capture_frame.winfo_height()
        
        self.menuber.entryconfig(2,state="normal")
        self.counter_button["state"] = "normal"
        
        self.img = ImageGrab.grab(bbox=(self.x, self.y, self.x+self.w, self.y+self.h))
        self.img = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(92, 27, image=self.img)
        self.canvas.update()
    
    def snatchcount(self):
        try:
            max_count = int(self.entry.get())
        except:
            return
        if max_count == 0:
            return
        
        self.threshold = float(self.spin.get())
        self.counter_button["state"] = "disabled"
        self.stop["state"] = "normal"
        
        self.img = ImageGrab.grab(bbox=(self.x, self.y, self.x+self.w, self.y+self.h))
        frame = np.array(self.img)
        self.img = ImageTk.PhotoImage(self.img)
        
        self.canvas.create_image(92, 27, image=self.img)
        self.canvas.update()
        
        result = cv2.matchTemplate(frame, self.temp, cv2.TM_CCORR_NORMED)
        maxVal = cv2.minMaxLoc(result)[1]
        
        if self.threshold < maxVal:
            if not self.snatch_frag:
                self.count += 1
                if max_count - self.count < 3:
                    winsound.Beep(650, 300)
                else:
                    winsound.Beep(580, 300)
                
                self.label["text"] = f"スナッチリストを開いた数 : {self.count}回"
                if self.count == max_count:
                    self.after_cancel(self.id)
                    self.count = 0
                    self.counter_button["state"] = "normal"
                    messagebox.showinfo(title="結果", message="消費が終了しました")
                    self.label["text"] = f"スナッチリストを開いた数 : {self.count}回"
                    self.stop["state"] = "disabled"
                    return
                self.snatch_frag = True
        else:
            self.snatch_frag = False
        self.id = self.after(100, self.snatchcount)
    
    def stop_counter(self):
        self.after_cancel(self.id)
        self.counter_button["state"] = "normal"
        self.count = 0
        self.label["text"] = f"スナッチリストを開いた数 : {self.count}回"
        self.snatch_frag = False
    
    def img_save(self):
        img = ImageGrab.grab(bbox=(self.x, self.y, self.x+self.w, self.y+self.h))
        img.save("temp/output.png")
        
if __name__ == "__main__":
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = Tk()
    app = SnatchCounter(master=root)
    app.mainloop()