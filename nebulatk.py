import tkinter as tk
from tkinter import font as tkfont
from time import sleep
import threading
import math
'''
bounds[y] = [object, left side bound, right side bound]
'''

def _get_max_font_size(root, font, height, width, text):
    width *= 0.9
    height *= 0.9
    
    size1 = 100
    
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)
        
    curr_width = tkfont.Font(root, font=(font[0], size1, font[2]),text=text).measure(text)
    curr_height = tkfont.Font(root, font=(font[0], size1, font[2]),text=text).metrics("linespace")
    
    
        
    while curr_width > width:
        size1 -= 1
        curr_width = tkfont.Font(root, font=(font[0], size1, font[2]),text=text).measure(text)
        
    size = size1

    while curr_height > height:
        size -= 1
        curr_height = tkfont.Font(root, font=(font[0], size, font[2]),text=text).metrics("linespace")
        
    font = tkfont.Font(root, font=(font[0], size, font[2]),text=text)
    print(font.measure(text),font.metrics("linespace"), width, height)
    
    return size

def _get_min_button_size(root, font, text):
    if len(font) < 3:
        font = (font[0], font[1], tkfont.NORMAL)
    
    width = int(math.ceil(tkfont.Font(root, font = font,text=text).measure(text)/0.9))
    height = int(math.ceil(tkfont.Font(root, font = font,text=text).metrics("linespace")/0.9))
    
    return width, height
    
class Button():
    def __init__(self,
                 root = None,
                 width = 0,
                 height = 0,
                 text = "",
                 font = None,
                 fill = "white",
                 border = "black",
                 border_width = 3,
                 command = None):
        
        self.root = root
        self.master = root.canvas
        
        if font == None:
            min_width, min_height = _get_min_button_size(self.master.master, ("Helvetica", 10), text)
        else:
            min_width, min_height = _get_min_button_size(self.master.master, font, text)
            print(min_width,min_height)
        if width == 0:
            width = min_width
        if height == 0:
            height = min_height
            
        self.width = width
        self.height = height
        self.object = None
        self.fill = fill
        self.border = border
        self.border_width = border_width
        self.command = command
        self.text = text
        if font == None:
            font = ("Helvetica", int(width/len(text)))
            font = ("Helvetica", _get_max_font_size(self.master.master, font, self.height, self.width, text))
        self.font = font
        print(font)
        self.x = 0
        self.y = 0
    def clicked(self):
        self.master.itemconfigure(self.object,fill = "light grey")
        print(self.object)
        if self.command != None:
            self.command()

    def release(self):
        self.master.itemconfigure(self.object,fill = "white")

    def place(self, x=0, y=0):
        if self.object == None:
            self.object = self.root.create_rectangle(self.x,
                                                     self.y,
                                                     self.x+self.width,
                                                     self.y+self.height,
                                                     fill = self.fill,
                                                     border_width = self.border_width,
                                                     outline = self.border)
            self.text_object = self.root.create_text(self.x+(self.width/2),self.y+(self.height/2),text=self.text,font=self.font)
        self.master.move(self.object,x-self.x,y-self.y)
        self.master.move(self.text_object,x-self.x,y-self.y)
        for i in range(self.y,self.y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0] == self:
                        self.root.bounds[i].pop(j)
                        break
        for i in range(y,y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0].object < self.object:
                        self.root.bounds[i].insert(j,[self, x, x+self.width])
                        break
            else:
                self.root.bounds[i] = [[self, x, x+self.width]]
        self.x = x
        self.y = y
        return self
    def configure(self, x=0, y=0):
        self.master.move(self.object,x-self.x,y-self.y)
        self.master.move(self.text_object,x-self.x,y-self.y)
        for i in range(self.y,self.y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0] == self:
                        self.root.bounds[i].pop(j)
                        break
        for i in range(y,y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0].object < self.object:
                        self.root.bounds[i].insert(j,[self, x, x+self.width])
                        break
            else:
                self.root.bounds[i] = [[self, x, x+self.width]]
        self.x = x
        self.y = y
        return self



class Frame():
    def __init__(self,
                 root = None,
                 width = 0,
                 height = 0,
                 fill = None,
                 border = "black",
                 border_width = 1):
        
        global bounds
        self.root = root
        self.master = root.canvas
        self.width = width
        self.height = height
        self.object = None
        self.fill = fill
        self.border = border
        self.border_width = border_width
        

    def place(self, x=0, y=0):
        self.x = x
        self.y = y
        if self.object == None:
            self.object = self.root.create_rectangle(self.x,
                                                     self.y,
                                                     self.x+self.width,
                                                     self.y+self.height,
                                                     fill = self.fill,
                                                     border_width = self.border_width,
                                                     outline = self.border)
        self.master.move(self.object,x-self.x,y-self.y)
        for i in range(self.y,self.y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0] == self:
                        self.root.bounds[i].pop(j)
                        break
        for i in range(y,y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0].object < self.object:
                        self.root.bounds[i].insert(j,[self, x, x+self.width])
                        break
            else:
                self.root.bounds[i] = [[self, x, x+self.width]]
        return self
    def clicked(self):
        pass
    def release(self):
        pass
    
    def configure(self, x=0, y=0):
        self.master.move(self.object,x-self.x,y-self.y)
        for i in range(self.y,self.y+self.height):
            if i in bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0] == self:
                        self.root.bounds[i].pop(j)
                        break
        for i in range(y,y+self.height):
            if i in self.root.bounds:
                for j in range(0,len(self.root.bounds[i])):
                    if self.root.bounds[i][j][0].object < self.object:
                        self.root.bounds[i].insert(j,[self, x, x+self.width])
                        break
            else:
                self.root.bounds[i] = [[self, x, x+self.width]]
        self.x = x
        self.y = y
        return self


        
'''
def add_btn(x,y,height,width,message):
    global canvas
    btn = canvas.create_rectangle(x, y, x+width, y+height, fill = "green")
    for i in range(y,y+height):
        if i in bounds:
            bounds[i].insert(0,[btn, x, x+width, lambda: print(message)])
        else:
            bounds[i] = [[btn, x, x+width, lambda: print(message)]]
  '''
'''
add_btn(10,10,10,10,"1")
add_btn(50,10,60,70,"2")
add_btn(100,100,150,150,"3")
add_btn(15,15,15,15,"4")
'''

class _window_internal(threading.Thread):
    def __init__(self):
        super().__init__()
        self.bounds = {}
        self.root = None
        self.canvas = None
        self.down = None
        
        

    def click(self, event):
        x = int(event.x)
        y = int(event.y)
        if y in self.bounds:
            for i in self.bounds[y]:
                if x <= i[2] and x >= i[1]:
                    i[0].clicked()
                    self.down = i[0]
                    break

    def click_up(self, event):
        if self.down:
            self.down.release()
            self.down = None
    def create_rectangle(self,x,y,widt,height=0,fill=0,border_width=0,outline=0):
        return self.canvas.create_rectangle(x, y, widt, height,
                                                     fill = fill,
                                                     width = border_width,
                                                     outline = outline)
    def create_text(self,x,y,text,font):
        return self.canvas.create_text(x,y,text=text,font=font)
    def move(self, _object, x, y):
        self.canvas.move(_object, x, y)
        
    def run(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width = 500, height = 500, borderwidth = 0, highlightthickness = 0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<ButtonRelease-1>", self.click_up)
        self.root.mainloop()

def Window():
    canvas = _window_internal()
    canvas.start()
        
    while canvas.root == None:
        sleep(0.1)
    return canvas


def __main__():
    canvas = Window()
    Button(canvas,10,10,text="hahah").place()
    Button(canvas,text="hahah").place(50,10)
    Button(canvas,text="hihih", font = ("Helvetica",36)).place(100,100)
    btn_4 = Button(canvas,15,15,text="hahah").place(15,15)
    btn_4.place(50,60)

    Frame(canvas,30,30, border = "green").place(160,80)

if __name__ == "__main__":
    __main__()

#canvas.root.mainloop()
