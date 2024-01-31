from tkinter import *
from tkinter import ttk
import tkinter.colorchooser as cc
import tkinter.filedialog as fd

import src.dartsandkites_svg
import xml.etree.ElementTree as ET
import cairosvg

class App(Tk):
    
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Darts and Kites")

        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.style = {
            "border_thickness": DoubleVar(value=0.001),
            "border_color": StringVar(value="#000000"),
            "dart_color": StringVar(value="#ffaa00"),
            "kite_color": StringVar(value="#0000cc")
        }
        self.dnk = None
        self.img = None

        for F in (StartPage, Editor):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nwes")

        self.showFrame(StartPage)

    def showFrame(self, container):

        frame = self.frames[container]
        frame.tkraise()

    def createImage(self, rec_depth: int):

        self.dnk = src.dartsandkites_svg.DnkInterface(rec_depth, **{attr: val.get() for (attr, val) in self.style.items()})
        self.bytes = self.dnk.getSVGbytes()
        self.imbytes = cairosvg.svg2png(self.bytes)

        self.img = PhotoImage(data=self.imbytes)
        self.frames[Editor].canvas.itemconfig(self.frames[Editor].canvas_img, image=self.img)

        self.showFrame(Editor)        

class StartPage(ttk.Frame):


    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        
        self.scale = ScalePicker(self, controller)
        self.scale.grid(column=0, row=0)
        
        Label(self, text="Border width:").grid(column=0, row=1)
        self.size_var = IntVar(value=2)
        self.border_size = Spinbox(self,from_=0,to=150, textvariable=self.size_var, command=lambda: controller.style["border_thickness"].set(self.size_var.get()*0.0005))
        self.border_size.grid(column=0, row=2)

        self.border_color = ColorPicker(self, "Border color:", controller.style["border_color"])
        self.border_color.grid(column=0, row=3)
        
        self.dartcolor = ColorPicker(self, "Dart color:", controller.style["dart_color"])
        self.dartcolor.grid(column=0, row=4)

        self.kitecolor = ColorPicker(self, "Kite color:", controller.style["kite_color"])
        self.kitecolor.grid(column=0, row=5)

        intro_text = [
            "Welcome to Darts and Kites.",
            "",
            "This rudimentary application lets you generate P2 Penrose tiling ('darts' and",
            "'kites'),allows you to change the individual tile colors afterwards, and lets",
            "you save your creation as a vector (.svg) or raster (.png) image.",
            "",
            "MAIN SCREEN:",
            "On this screen, choose the starting properties of your tiling.",
            "Use the Recursion depth slider to choose how fine the tiling will be.",
            "CAUTION: Higher values (starting form 8) might cause lag while editing on",
            "weaker devices.",
            "",
            "EDITOR:",
            "Left-click a tile to paint it your chosen color (Paint color on the right).",
            "Right-click a tile to pick its color as Paint color.",
            "Use buttons at the bottom of your screen to save your result.",
            "Use the Return button to return here.",
            "",
            "Credit: Bc. Filip Dráber, 2024 for the Computer Arts project"
        ]
        text = Text(self)
        text.grid(column=1, row=0, rowspan=10)
        for line in intro_text:
            text.insert(END, line+"\n")



class Editor(ttk.Frame):
    
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        self.controller = controller

        self.canvas = Canvas(self, width=1200, height=900)
        self.canvas.grid(column=0, row=0, rowspan=4)
        self.canvas_img = self.canvas.create_image(0,0,image=controller.img,anchor=NW)
        self.canvas.bind('<Button-1>', self.paintImage)
        self.canvas.bind('<Button-3>', self.pickColor)

        Label(self, text="Border width:").grid(column=1, row=0, sticky=S)
        self.size_var = IntVar(value=2)
        self.border_size = Spinbox(self,from_=0,to=150, textvariable=self.size_var, command=self.setThickness)
        self.border_size.grid(column=1, row=1,sticky=N)

        self.border_color = ColorPicker(self, "Border color:", controller.style["border_color"], command=self.setBorderColor)
        self.border_color.grid(column=1, row=2)

        self.color_var = StringVar(value="#000000")
        self.picker = ColorPicker(self, "Paint color:", self.color_var)
        self.picker.grid(column=1, row=3, sticky=N)

        self.buttons = Frame(self)
        self.buttons.grid(column=0, row=4)
        self.buttons.grid_rowconfigure(0, weight=1)
        self.buttons.grid_columnconfigure(0, weight=1)

        Button(self.buttons, text="Return", command=lambda: controller.showFrame(StartPage)).grid(column=0, row=0)
        Button(self.buttons, text="Save PNG", command=self.saveAsPNG).grid(column=1, row=0)
        Button(self.buttons, text="Save SVG", command=self.saveAsSVG).grid(column=2, row=0)

    def setThickness(self):
        self.controller.dnk.updateBorder(width=self.size_var.get()*0.0005)
        self.updateImage()

    def setBorderColor(self):
        self.controller.dnk.updateBorder(color=self.controller.style["border_color"].get())
        self.updateImage()

    def paintImage(self, event):
        paint = self.controller.dnk.paint(event.x/1200.0, event.y/900.0, self.color_var.get())
        if paint: self.updateImage()

    def pickColor(self, event):
        color = self.controller.dnk.getColor(event.x/1200.0, event.y/900.0)
        self.picker.setColor(color)

    def updateImage(self):
        self.controller.bytes = self.controller.dnk.getSVGbytes()
        self.controller.imbytes = cairosvg.svg2png(self.controller.bytes)
        self.controller.img = PhotoImage(data=self.controller.imbytes)
        self.canvas.itemconfig(self.canvas_img, image=self.controller.img)

    def paintCanvas(self):
        ...

    def saveAsPNG(self):
        f = fd.asksaveasfile(mode='wb', defaultextension=".png")
        f.write(self.controller.imbytes)
        f.close()

    def saveAsSVG(self):
        f = fd.asksaveasfile(mode='wb', defaultextension=".svg")
        f.write(self.controller.bytes)
        f.close()

class ColorSquare(Canvas):
    
    def __init__(self, parent, color):
        Canvas.__init__(self, parent, width=20, height=20)

        self.rectangle = self.create_rectangle(0,0,20,20, fill=color)

    def changeColor(self, color):
        self.itemconfig(self.rectangle, fill=color)


class ColorPicker(ttk.Frame):

        
        
    def __init__(self, parent, label, color_var, command=lambda: ...):
        ttk.Frame.__init__(self, parent)
        self.color_var = color_var
        self.command = command
        
        Label(self, text=label).grid(column=0,row=0, sticky=W)
        
        self.sq = ColorSquare(self, self.color_var.get())
        self.sq.grid(column=0, row=1)
        
        Button(self, text="Change color", command=self.pickColor).grid(column=1,row=1,sticky=E)
        
    def setColor(self, color):
        self.sq.changeColor(color)
        self.color_var.set(color)
        self.command()
        
    def pickColor(self):
        _, color_code = cc.askcolor(initialcolor=self.color_var.get())
        if not color_code: return
        self.setColor(color_code)

class ScalePicker(ttk.Frame):
     def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        ttk.Label(self, text="Recursion depth").grid(column=0, row=0, sticky=W)
        
        scale_val = IntVar()
        Scale(self, from_=6, to=11, variable=scale_val, orient=HORIZONTAL).grid(column=0, row=1)

        ttk.Button(self, text="Generate", command=lambda: controller.createImage(scale_val.get())).grid(column=0, row=2)

if __name__=="__main__":

    app = App()
    app.mainloop()

    exit()