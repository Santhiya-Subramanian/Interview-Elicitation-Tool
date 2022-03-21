from tkinter import *

# Create a GUI window
root = Tk()

# Create a text area box
# for filling or typing the information.
text = Text(root)

# insert given string in text area
text.insert(INSERT, "Hello, everyone!\n")

text.insert(END, "This is 2020.\n")

text.insert(END, "Pandemic has resulted in economic slowdown worldwide")

text.pack(expand=1, fill=BOTH)

# add tag using indices for the
# part of text to be highlighted
text.tag_add("start", "2.8", "1.13")

# configuring a tag called start
text.tag_config("start", background="black", foreground="red")

# start the GUI
root.mainloop()