from tkinter import *
import tkinter.messagebox
from tkinter import ttk

main_window = Tk()

main_window.title("Annotation Tag")
main_window.geometry("500x500")

tags = ['Requirement', 'Mistake', 'Followup', 'Custom']


def tag_window():
    pass


tag_dropdown = ttk.Combobox(main_window, value=tags)
tag_dropdown.current(0)
tag_dropdown.pack(pady=20)

main_window.mainloop()