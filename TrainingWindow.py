import csv
import datetime
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
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
import pandas as pd
from google.cloud import speech_v1p1beta1 as speech

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
    # print(audio)

    pygame.mixer.music.load(audio)
    # print(slider.get())
    pygame.mixer.music.play(loops=0, start=int(slider.get()))
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


global play
play = False


def play_pause():
    global play
    play = not play
    if play:
        play_audio()
    else:
        pause_audio(paused)


global audio_total_length


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
    # print("audio total length type ")
    # print(type(audio_total_length))
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
    # print(input_file_name)
    # mb.showinfo("Json key", "Choose Json key")
    text_box.delete("1.0", "end")

    # upload your json key
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/santh/PycharmProjects/pythonProject/IET-Tool/json_key.json'
    client = speech.SpeechClient()

    media_uri_path = 'gs://speech_to_text_audio_file/'
    audio_path = f'{media_uri_path}{input_file_name}'
    print(path[1])

    # client.RecognitionAudio(uri=media_uri)
    audio_file = speech.RecognitionAudio(uri=audio_path)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=2,
        max_speaker_count=10,
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=48000,
        language_code="en-US",
        diarization_config=diarization_config,
        # model='audio'
    )

    operation = client.long_running_recognize(
        config=config,
        audio=audio_file
    )

    response = operation.result(timeout=90)
    # print(response)

    result = response.results[-1]

    words_info = result.alternatives[0].words

    words_list = []

    for word_info in words_info:
        words_list.append({
            'word': word_info.word,
            'speaker_tag': word_info.speaker_tag,
            'start_time': word_info.start_time.seconds,
            'end_time': word_info.end_time,
        })
    # print(words_list)

    current_speaker = words_list[0]['speaker_tag']
    speaker_start_time = words_list[0]['start_time']
    speaker_end_time = words_list[0]['end_time']
    # print(current_speaker)
    # print(speaker_start_time)
    # print(speaker_end_time)
    current_line = []
    script = []

    for item in words_list:
        if item['speaker_tag'] != current_speaker:
            script.append({
                'speaker': current_speaker,
                'line': current_line,
                'start_time': speaker_start_time,
                'end_time': speaker_end_time
            })
            current_line = []
            current_speaker = item['speaker_tag']
            speaker_start_time = item['start_time']
            speaker_end_time = item['end_time']
        else:
            current_line.append(item['word'])

    script.append({
        'speaker': current_speaker,
        'line': current_line,
        'start_time': speaker_start_time,
        'end_time': speaker_end_time
    })
    timer_list = []
    timevalues = []
    for line in script:
        startTime = line['start_time']
        str_val = str(startTime)
        script = f"{str_val}  Speaker{line['speaker']}: " + " ".join(line['line'])

        text_box.insert(END, script)
        findtext = f"{str_val}  {'speaker'}"
        # print('timer_list', {str_val})
        # print('timestamp', timer_list)
        print('list', timevalues)

        def timelink(button_press):
            print('button pressed', button_press)
            print('inside', timevalues)
            slider.config(value=int(button_press))
            play_audio()

        if findtext:
            idx = '1.0'
            while 1:
                # searches for desired string from index 1
                idx = text_box.search(findtext, idx, nocase=1, stopindex=END)

                if not idx: break

                # last index sum of current index and
                # length of text
                lastidx = '%s+%dc' % (idx, len(findtext))

                text_box.insert(idx, '\n\n')

                # overwrite 'Found' at idx
                text_box.tag_add('found', idx, lastidx)
                idx = lastidx
                # print(idx)

            # mark located string as red
            text_box.tag_config('found')

        r = Button(text_box, text=str_val, background='Green', command=lambda m=str_val: timelink(m))

        timevalue = r.cget('text')
        timevalues.append(timevalue)
        # print('out of the function', timevalues)
        timer_list.append(timevalue)
        if (findtext and r):
            idx = '1.0'
            while 1:
                # searches for desired string from index 1
                idx = text_box.search(findtext, idx, nocase=1, stopindex=END)
                # print(idx)
                if not idx: break

                # last index sum of current index and
                # length of text
                lastidx = '% s+% dc' % (idx, len(findtext))
                text_box.insert(idx, '\n\n Speak')
                # print('idx ', idx)
                # print('index(idx)', text_box.index(idx))
                text_box.delete(idx, lastidx)
                text_box.window_create(text_box.index(idx), window=r)

                num = 3
                lastidx = '% s+% dc' % (idx, num)

                # overwrite 'Found' at idx
                text_box.tag_add('found', idx, lastidx)
                idx = lastidx

            # mark located string as red
            text_box.tag_config('found')


global opened_file_name
opened_file_name = False


def fileoption():
    top = Toplevel(main_window)
    top.title("File Menu")
    top.geometry("150x150")

    def open_file():
        text_box.delete("1.0", END)
        transcribe_text_file = filedialog.askopenfilenames()

        if transcribe_text_file:
            global opened_file_name
            opened_file_name = transcribe_text_file[0]

        print(opened_file_name)
        transcribed_file_path = os.path.split(transcribe_text_file[0])
        print(transcribed_file_path[1])
        text_file = transcribed_file_path[1]
        transcribe_text_file = open((transcribe_text_file[0]), 'r')
        transcribed_text = transcribe_text_file.read()
        text_box.insert(END, transcribed_text)
        transcribe_text_file.close()
        top.destroy()

    def save_file():
        global opened_file_name
        if opened_file_name:
            transcribe_file_save = open(opened_file_name, 'w')
            transcribe_file_save.write(text_box.get("1.0", END))
            transcribe_file_save.close()
        else:
            saveAs_file()
        top.destroy()

    def saveAs_file():
        transcribe_file_save = filedialog.asksaveasfilename(defaultextension=".*",
                                                            filetypes=(("Text File", "*.txt"), ("Word File", "*.docx")))
        if transcribe_file_save:
            file_name = transcribe_file_save
            filepath = os.path.split(transcribe_file_save)
            file_name = file_name.replace(filepath[0], "")

            transcribe_file_save = open(transcribe_file_save, 'w')
            transcribe_file_save.write(text_box.get("1.0", END))
            transcribe_file_save.close()
        top.destroy()

    open_btn = Button(top, text="Open", command=lambda: open_file())
    open_btn.pack(pady=5)
    open_btn = Button(top, text="Save", command=lambda: save_file())
    open_btn.pack(pady=5)
    open_btn = Button(top, text="SaveAs", command=lambda: saveAs_file())
    open_btn.pack(pady=5)


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


def annotation_box_file():
    top = Toplevel(main_window)
    top.title("File Menu")
    top.geometry("150x150")

    current_item = annotation_box.focus()
    current_value = annotation_box.item(current_item, 'values')
    print(current_value)

    def open_list():
        global df
        excel_file_name = filedialog.askopenfilenames()
        if excel_file_name:
            try:
                excel_file_name = r"{}".format(excel_file_name[0])
                df = pd.read_excel(excel_file_name)
            except ValueError:
                print("file couldn't be open")

        clear_list()

        annotation_box['column'] = list(df.columns)
        annotation_box['show'] = "headings"

        for column in annotation_box["column"]:
            annotation_box.heading(column, text=column)

        df_rows = df.to_numpy().tolist()
        for row in df_rows:
            annotation_box.insert("", "end", values=row)

        top.destroy()

    def save_list():
        if len(annotation_box.get_children()) < 1:
            mb.showinfo("No data", "No data to export")
            return False
        save_annotation_list = filedialog.asksaveasfilename(defaultextension=".*",
                                                            filetypes=(("CSV File", "*.csv"), ("Word File", "*.docx")))
        with open(save_annotation_list, mode='a', newline='') as my_excel_file:
            write = csv.writer(my_excel_file, dialect='excel')
            for i in annotation_box.get_children():
                row = annotation_box.item(i)['values']
                write.writerow(row)
        mb.showinfo("Message", "Export successfully")
        top.destroy()

    def clear_list():
        annotation_box.delete(*annotation_box.get_children())

    open_btn = Button(top, text="Open", command=lambda: open_list())
    open_btn.pack(pady=5)
    open_btn = Button(top, text="Save", command=lambda: save_list())
    open_btn.pack(pady=5)
    open_btn = Button(top, text="Clear", command=lambda: clear_list())
    open_btn.pack(pady=5)


def add_Tag():
    top = Toplevel(main_window)
    top.geometry("750x250")

    def gettag_values():
        current_item = annotation_box.focus()
        current_value = annotation_box.item(current_item, 'values')
        print(current_value[0])
        annotation_box.item(current_item,
                            values=(current_value[0], dropdown_label.get("1.0", END), description_text.get("1.0", END)))
        # print(dropdown_label.get("1.0", END))
        # print(description_text.get("1.0", END))

    tag_label = Label(top, text='Select the Tag')
    tag_label.pack(pady=10)
    tags = ['Requirement', 'Follow up', 'Mistake', 'Custom']
    list_frame = Frame(top)
    list_frame.pack()

    list_scroll = Scrollbar(list_frame)
    list_scroll.pack(side=RIGHT, fill=Y)

    dropdown_label = Text(list_frame, width=20, height=1)
    dropdown_label.pack()

    def selectedValue(evt):
        for dropvalue in dropdown.curselection():
            print(dropvalue)
        dropdown_label.delete("1.0", "end")
        for dropvalue in dropdown.curselection():
            selected_tag_value = dropdown.get(dropvalue)
            dropdown_label.insert(END, f'{selected_tag_value}, ')

    dropdown = Listbox(list_frame, selectmode="multiple", yscrollcommand=list_scroll.set)
    dropdown.bind('<<ListboxSelect>>', selectedValue)
    dropdown.pack(pady=5)

    for each_item in range(len(tags)):
        dropdown.insert(END, tags[each_item])
        dropdown.itemconfig(each_item)

    description_label = Label(top, text='Description')
    description_label.pack(pady=5)

    description_frame = Frame(top)
    description_frame.pack()

    description_scroll = Scrollbar(description_frame)
    description_scroll.pack(side=RIGHT, fill=Y)

    description_text = Text(description_frame, width=60, height=3, font=('times new roman', 16),
                            selectbackground='yellow', selectforeground='black', yscrollcommand=text_scroll.set)
    description_text.pack(pady=10)

    button = Button(top, text="Ok", command=lambda: [gettag_values(), close_win(top)])
    button.pack(pady=10)


def lookup():
    # query = search_entry.get()
    # selections = []
    # for child in tree.get_children():
    #     if query.lower() in tree.item(child)['values'].lower():  # compare strings in  lower cases.
    #         print(tree.item(child)['values'])
    #         selections.append(child)
    # print('search completed')
    # tree.selection_set(selections)
    lookup_record = search_entry.get()
    selections = []
    # print(lookup_record)
    annotation_box['column'] = list(df.columns)
    annotation_box['show'] = "headings"

    for record in annotation_box.get_children():
        if lookup_record in annotation_box.item(record)['values']:
            print(annotation_box.item(record)['values'])
            selections.append(record)
    annotation_box.selection_set(selections)

    search.destroy()


def searchRecords():
    global search_entry, search
    search = Toplevel(main_window)
    search.title('Lookup Records')
    search.geometry('400x200')

    search_frame = LabelFrame(search, text='Annotation Name')
    search_frame.pack(padx=10, pady=10)

    search_entry = Entry(search_frame)
    search_entry.pack(padx=20, pady=20)

    search_button = Button(search_frame, text='Search Annotation', command=lookup)
    search_button.pack(padx=20, pady=20)


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

transcribe_file = Button(rightFrame, text='File', command=lambda: fileoption())
transcribe_file.pack()

text_frame = Frame(rightFrame)
text_frame.pack(pady=10)

text_scroll = Scrollbar(text_frame)
text_scroll.pack(side=RIGHT, fill=Y)

text_box = Text(text_frame, width=40, height=15, font=('times new roman', 16), selectbackground='yellow',
                selectforeground='black', yscrollcommand=text_scroll.set)
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

annotation_file = Button(tool_bar, text='File', command=lambda: annotation_box_file())
annotation_file.grid(row=0, column=4, sticky=W, padx=5)

annotation_search = Button(tool_bar, text='Search', command=lambda: searchRecords())
annotation_search.grid(row=0, column=5, sticky=W, padx=5)

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

