import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
import pygame
from playsound import playsound
import os
from PIL import Image, ImageTk
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk
from pydub import AudioSegment
import tempfile
import speech_recognition as sr
from tkinter import colorchooser
import tkinter.messagebox as mb

main_window = Tk()
pw = PanedWindow(main_window, orient=HORIZONTAL)


def UploadAction():
    global path
    audios = filedialog.askopenfilenames()
    for audio in audios:
        path = os.path.split(audio)
        audio = path[1]
        audio_box.insert(END, audio)

        path = f'{path[0]}/'


def removeAudio():
    audio_box.delete(ANCHOR)
    pygame.mixer.music.stop()


def play_audio():
    global stopped
    stopped = False
    audio = audio_box.get(ACTIVE)
    audio_name = audio
    audio = f'{path}{audio}'
    print(audio)

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play(loops=0)
    audio_Label.config(text=audio_name)
    # call audio length function
    audio_Time()


global stopped
stopped = False


def stop_audio():
    status_bar.config(text='')
    slider.config(value=0)
    pygame.mixer.music.stop()
    audio_box.selection_clear(ACTIVE)

    status_bar.config(text='')
    audio_Label.config(text='')

    global stopped
    stopped = True


# create Global Pause Variable
global paused
paused = False


def pause_audio(is_paused):
    global paused
    paused = is_paused

    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True


global count
count = 0


def play_pause():
    global count
    count = count + 1
    if count == 1:
        play_audio()
    else:
        pause_audio(paused)


def audio_Time():
    current_time = pygame.mixer.music.get_pos() / 1000
    # slider_label.config(text=f'Slider: {int(slider.get())} and Song Pos: {int(current_time)}')
    formatted_time = time.strftime('%M:%S', time.gmtime(current_time))

    audio = audio_box.get(ACTIVE)
    audio = f'{path}{audio}'
    # loading the song to Mutagen
    load_audio_to_mutagen = MP3(audio)
    global audio_total_length
    audio_total_length = load_audio_to_mutagen.info.length
    formatted_audio_length = time.strftime('%M:%S', time.gmtime(audio_total_length))

    current_time += 1

    if int(slider.get()) == int(audio_total_length):
        status_bar.config(text=f'Time Elapsed: {formatted_audio_length}')

    elif paused:
        pass

    elif int(slider.get()) == int(current_time):
        slider_position = int(audio_total_length)
        slider.config(to=slider_position, value=int(current_time))

    else:
        slider_position = int(audio_total_length)
        slider.config(to=slider_position, value=int(slider.get()))
        formatted_time = time.strftime('%M:%S', time.gmtime(int(slider.get())))
        status_bar.config(text=f'Time Elapsed: {formatted_time} / {formatted_audio_length}')

        slider_time = int(slider.get()) + 1
        slider.config(value=slider_time)

    # status_bar.config(text=f'Time Elapsed: {formatted_time} / {formatted_audio_length}')
    # slider.config(value=current_time)

    status_bar.after(1000, audio_Time)


def slide(x):
    # slider_label.config(text=f'{int(slider.get())} of {int(audio_total_length)}')
    audio = audio_box.get(ACTIVE)
    audio = f'{path}{audio}'

    pygame.mixer.music.load(audio)
    pygame.mixer.music.play(loops=0, start=int(slider.get()))


def transcribe_action():
    audio_file = audio_box.curselection()
    input_file_name = audio_box.get(audio_file)
    print(f'{path}{input_file_name}')
    input_file_path = f'{path}{input_file_name}'

    load_audio_to_mutagen = MP3(input_file_path)
    audio_total_length = load_audio_to_mutagen.info.length
    length = float(audio_total_length) * 1000
    print(float(length))

    temp = tempfile.TemporaryFile()
    path_output = os.path.split(temp.name)
    global output_file
    output_file = f'{path_output[1]}.wav'
    print(output_file)
    temp.close()

    sound = AudioSegment.from_mp3(input_file_path)
    sound.export(output_file, format='wav')

    print(audio_total_length)
    if not os.path.isdir("splitaudio"):
        os.mkdir("splitaudio")

    audio = AudioSegment.from_file(output_file)
    lengthaudio = len(audio)
    print("Length of Audio File", lengthaudio)

    start = 0
    # # In Milliseconds, this will cut 10 Sec of audio
    threshold = 60000
    end = 0
    counter = 0

    file = open("recognized.txt", "r+")
    file.truncate(0)
    file.close()

    text_box.delete("1.0", "end")

    while start < len(audio):

        end += threshold

        chunk = audio[start:end]

        filename = f'splitaudio/chunk{counter}.wav'

        chunk.export(filename, format="wav")
        r = sr.Recognizer()

        fh = open("recognized.txt", "a+")

        with sr.AudioFile(filename) as source:
            audio_text = r.record(source)

            try:
                transcribed_text = r.recognize_google(audio_text)
                fh.write(transcribed_text + " ")
            except:
                print('something went wrong')

        fh.close()
        counter += 1

        start += threshold

        fh = open("recognized.txt", "r+")
        text_box.insert('end', fh.read())
        fh.close()

    os.remove(output_file)


global highlightCount
highlightCount = 0


def highlight():
    global highlightCount
    my_color = colorchooser.askcolor()[1]
    highlightCount += 1
    try:
        text_box.tag_add(highlightCount, "sel.first", "sel.last")
        text_box.tag_configure(highlightCount, foreground="Black", background=my_color)
    except tkinter.TclError:
        pass


def clear_highlight():
    text_box.tag_remove(highlightCount, "sel.first", "sel.last")


global extracted_text


def gettext():
    global extracted_text
    extracted_text = text_box.get("sel.first", "sel.last")
    print(extracted_text)
    annotation_box.insert('', 'end', values=(extracted_text, '', ''))


def delete_annotation():
    selected_item = annotation_box.selection()[0]
    annotation_box.delete(selected_item)


def close_win(top):
    top.destroy()


def add_Tag():
    top = Toplevel(main_window)
    top.geometry("750x250")

    def gettag_values():
        current_item = annotation_box.focus()
        current_value = annotation_box.item(current_item, 'values')
        print(current_value[0])
        annotation_box.item(current_item, values=(current_value[0], dropdown.get(), description_text.get("1.0", END)))
        print(dropdown.get())
        print(description_text.get("1.0", END))


    tag_label = Label(top, text='Select the Tag')
    tag_label.pack(pady=10)
    tags = ['Requirement', 'Follow up', 'Mistake', 'Custom']
    dropdown = ttk.Combobox(top, value=tags)
    dropdown.current(0)
    dropdown.pack(pady=5)

    description_label = Label(top, text='Description')
    description_label.pack(pady=5)

    description_frame = Frame(top)
    description_frame.pack()

    description_scroll = Scrollbar(description_frame)
    description_scroll.pack(side=RIGHT, fill=Y)

    description_text = Text(description_frame, width=40, height=3, font=('times new roman', 16), selectbackground='yellow', selectforeground='black', yscrollcommand=text_scroll.set)
    description_text.pack(pady=10)

    button = Button(top, text="Ok", command=lambda: [gettag_values(), close_win(top)])
    button.pack(pady=10)


# MenuBar Creation
frame = Frame(main_window)
frame.pack()
menuBar = Menu(frame)
home = Menu(menuBar, tearoff=0, activebackground='green', activeforeground='white')
menuBar.add_cascade(label='IE Tool', menu=home)
home.add_command(label='Industry')
home.add_command(label='Research')
home.add_separator()
home.add_command(label='Exit', command=main_window.quit)

leftFrame = Frame(pw)
rightFrame = Frame(pw)
annotationFrame = Frame(pw)

# Initialize mixer module in pygame
pygame.mixer.init()

upload_button = Button(leftFrame, text='Upload Audio File', command=lambda: UploadAction())
upload_button.pack(pady=10)

remove_button = Button(leftFrame, text='Remove Audio File', command=lambda: removeAudio())
remove_button.pack(pady=10)

audio_box = Listbox(leftFrame, bg='white', fg='black', width=60)
audio_box.pack()


play_pause_btn_img = Image.open('images/play_pause.png')
# pause_btn_img = Image.open('images/pause.png')
stop_btn_img = Image.open('images/stop.png')
forward_btn_img = Image.open('images/forward.png')
rewind_btn_img = Image.open('images/rewind.png')

# Resize the Image
resized_play_pause_img = play_pause_btn_img.resize((50, 50), Image.ANTIALIAS)
resized_play_pausebtn_img = ImageTk.PhotoImage(resized_play_pause_img)

# resized_pause_img = pause_btn_img.resize((50, 50), Image.ANTIALIAS)
# resized_pausebtn_img = ImageTk.PhotoImage(resized_pause_img)

resized_stop_img = stop_btn_img.resize((50, 50), Image.ANTIALIAS)
resized_stopbtn_img = ImageTk.PhotoImage(resized_stop_img)

resized_forward_img = forward_btn_img.resize((50, 50), Image.ANTIALIAS)
resized_forwardbtn_img = ImageTk.PhotoImage(resized_forward_img)

resized_rewind_img = rewind_btn_img.resize((50, 50), Image.ANTIALIAS)
resized_rewindbtn_img = ImageTk.PhotoImage(resized_rewind_img)

# label
audio_Label = Label(rightFrame, text='')
audio_Label.pack()

# Create Status Bar
status_bar = Label(rightFrame, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=1)

# Create Player Control Frame
control_frame = Frame(rightFrame)
control_frame.pack(pady=10)
play_pause_btn = Button(control_frame, image=resized_play_pausebtn_img, borderwidth=0, command=lambda: play_pause())
# pause_btn = Button(control_frame, image=resized_pausebtn_img, borderwidth=0, command=lambda: pause_audio(paused))
stop_btn = Button(control_frame, image=resized_stopbtn_img, borderwidth=0, command=stop_audio)
forward_btn = Button(control_frame, image=resized_forwardbtn_img, borderwidth=0)
rewind_btn = Button(control_frame, image=resized_rewindbtn_img, borderwidth=0)
play_pause_btn.grid(row=0, column=0, padx=10)
# pause_btn.grid(row=0, column=1, padx=10)
stop_btn.grid(row=0, column=2, padx=10)
forward_btn.grid(row=0, column=3, padx=10)
rewind_btn.grid(row=0, column=4, padx=10)

slider = ttk.Scale(rightFrame, from_=0, to=100, orient=HORIZONTAL, value=0, length=360, command=slide)
slider.pack(pady=10)

# textBox_label = Label(rightFrame, text='Transcript', font=('times new roman', 16))
# textBox_label.pack(pady=10)
transcribe_button = Button(rightFrame, text='Transcribe', command=lambda: transcribe_action())
transcribe_button.pack(pady=10)

text_frame = Frame(rightFrame)
text_frame.pack(pady=10)

text_scroll = Scrollbar(text_frame)
text_scroll.pack(side=RIGHT, fill=Y)

text_box = Text(text_frame, width=40, height=15, font=('times new roman', 16), selectbackground='yellow', selectforeground='black', yscrollcommand=text_scroll.set)
text_box.pack(pady=10)

# annotation tool bar
tool_bar = Frame(annotationFrame)
tool_bar.pack()

highlight_button = Button(tool_bar, text='Highlight', command=lambda: highlight())
highlight_button.grid(row=0, column=0, sticky=W, padx=5)

clear_highlight_button = Button(tool_bar, text='Clear Highlight', command=lambda: clear_highlight())
clear_highlight_button.grid(row=0, column=1, sticky=W, padx=5)

extract_button = Button(tool_bar, text='Extract', command=lambda: gettext())
extract_button.grid(row=0, column=2, sticky=W, padx=5)

delete_annotation_button = Button(tool_bar, text='Remove Annotation', command=lambda: delete_annotation())
delete_annotation_button.grid(row=0, column=3, sticky=W, padx=5)

s = ttk.Style()
s.theme_use('clam')

annotation_box = ttk.Treeview(annotationFrame, column=("c1", "c2", "c3"), show='headings', height=5)

annotation_box.column("# 1", anchor=CENTER)
annotation_box.heading("# 1", text="Sentence")
annotation_box.column("# 2", anchor=CENTER)
annotation_box.heading("# 2", text="Annotation Tag")
annotation_box.column("# 3", anchor=CENTER)
annotation_box.heading("# 3", text="Description")
annotation_box.pack(pady=20)

# annotation_box = Listbox(annotationFrame, bg='white', fg='black', width=60)

addannotate_Tag = Button(annotationFrame, text='Add Tag', command=lambda: add_Tag())
addannotate_Tag.pack(pady=20)

pw.add(leftFrame, width=150)
pw.add(rightFrame)
pw.add(annotationFrame)
pw.pack(fill=BOTH, expand=True)

text_scroll.config(command=text_box.yview)
# To show sash
pw.configure(sashrelief=RAISED)
main_window.geometry('1400x800')
main_window.config(menu=menuBar)
main_window.title("Interview Elicitation Tool")
main_window.mainloop()