import os
from tkinter import *
from PIL import Image, ImageTk
import pygame


def Training_window():
    os.system('TrainingWindow.py')


# home Window
main_window = Tk()
bg = Image.open('images/img.png')
bg_img = bg.resize((800, 500), Image.ANTIALIAS)
bg_re_img = ImageTk.PhotoImage(bg_img)

bg_label = Label(main_window, image=bg_re_img)
bg_label.place(x=0, y=0)

frame = Frame(main_window)
frame.pack()
menuBar = Menu(frame)
home = Menu(menuBar, tearoff=0, activebackground='green', activeforeground='white')
menuBar.add_cascade(label='IE Tool', menu=home)
home.add_command(label='Training', command=lambda: [Training_window()])
home.add_command(label='Industry')
home.add_command(label='Research')
home.add_separator()
home.add_command(label='Exit', command=main_window.quit)



# Create label
vision_label = Label(main_window, text="Vision")
vision_label.config(font=("TimesNewRoman 14 bold"))

Vision = """To assist the business analyst in doing more effective interview elicitation."""

para_label = Label(main_window, text=Vision)
para_label.config()


main_window.geometry('800x500')
main_window.title("Interview Elicitation Tool")
main_window.config(menu=menuBar)
vision_label.pack(pady=20)
para_label.pack(pady=10)
main_window.mainloop()