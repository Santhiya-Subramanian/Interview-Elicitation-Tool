from view import *
from view import View
from model import Model
import tkinter as TK
from tkinter import *

class Controller:
    def __init__(self):
        # Variables
        self.str_val = None
        self.container = TK.Tk()
        self.model = Model(controller=self) #point to Model Object
        self.view = View(self.container, controller=self)

    def run(self):
        self.container.geometry('1400x800')
        self.container.title("Interview Elicitation Tool")
        self.container.mainloop()

    def uploadAction(self, audios):
        # global path
        for audio in audios:
            path = os.path.split(audio)
            audio = path[1]
            self.view.add_audio(audio)
            self.path = f'{path[0]}/'

    def play_audio(self):
        # self.stopped
        self.stopped = False

        self.audio = self.view.audio_box.get(ACTIVE)
        self.audio_name = self.audio
        self.audio = f'{self.path}{self.audio}'
        # print(self.audio)

        pygame.mixer.music.load(self.audio)
        # print(slider.get())
        pygame.mixer.music.play(loops=0, start=int(self.view.slider.get()))
        self.view.audio_Label.config(text=self.audio_name)
        # call audio length function
        self.audio_Time()

    def audio_Time(self):
        self.current_time = pygame.mixer.music.get_pos() / 1000
        # slider_label.config(text=f'Slider: {int(slider.get())} and Song Pos: {int(current_time)}')
        self.formatted_time = time.strftime('%M:%S', time.gmtime(self.current_time))

        self.audio = self.view.audio_box.get(ACTIVE)
        self.audio = f'{self.path}{self.audio}'
        # loading the song to Mutagen
        self.load_audio_to_mutagen = MP3(self.audio)
        global audio_total_length
        self.audio_total_length = self.load_audio_to_mutagen.info.length
        # print("audio total length type ")
        # print(type(audio_total_length))
        self.formatted_audio_length = time.strftime('%M:%S', time.gmtime(self.audio_total_length))

        self.current_time += 1

        if int(self.view.slider.get()) == int(self.audio_total_length):
            self.view.status_bar.config(text=f'Time Elapsed: {self.formatted_audio_length}')

        elif paused:
            pass

        elif int(self.view.slider.get()) == int(self.current_time):
            self.slider_position = int(self.audio_total_length)
            self.view.slider.config(to=self.slider_position, value=int(self.current_time))

        else:
            self.slider_position = int(self.audio_total_length)
            self.view.slider.config(to=self.slider_position, value=int(self.view.slider.get()))
            self.formatted_time = time.strftime('%M:%S', time.gmtime(int(self.view.slider.get())))
            self.view.status_bar.config(text=f'Time Elapsed: {self.formatted_time} / {self.formatted_audio_length}')

            self.slider_time = int(self.view.slider.get()) + 1
            self.view.slider.config(value=self.slider_time)

        self.view.status_bar.after(1000, self.audio_Time)

    global audio_total_length

    # create Global Pause Variable
    global paused
    paused = False

    def pause_audio(self, is_paused):
        self.is_paused = is_paused
        global paused
        self.paused = is_paused

        if paused:
            pygame.mixer.music.unpause()
            paused = False
        else:
            pygame.mixer.music.pause()
            paused = True

    def transcribe_action(self):
        audio_file = self.view.audio_box.curselection()
        input_file_name = self.view.audio_box.get(audio_file)
        self.view.clear_textbox()
        # upload your json key
        os.environ[
            'GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/santh/PycharmProjects/pythonProject/IET-Tool/json_key.json'
        client = speech.SpeechClient()

        media_uri_path = 'gs://speech_to_text_audio_file/'
        audio_path = f'{media_uri_path}{input_file_name}'
        print(self.path[1])

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
        current_speaker = words_list[0]['speaker_tag']
        speaker_start_time = words_list[0]['start_time']
        speaker_end_time = words_list[0]['end_time']
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
        self.timevalues = []
        for line in script:
            startTime = line['start_time']
            self.str_val = str(startTime)
            print(self.str_val)
            script = f"{self.str_val}  Speaker{line['speaker']}: " + " ".join(line['line'])

            self.view.add_script(script)
            findtext = f"{self.str_val}  {'speaker'}"
            # print('list', self.timevalues)

            if findtext:
                idx = '1.0'
                while 1:
                    # searches for desired string from index 1
                    idx = self.view.text_box.search(findtext, idx, nocase=1, stopindex=END)

                    if not idx: break

                    # last index sum of current index and
                    # length of text
                    lastidx = '%s+%dc' % (idx, len(findtext))

                    self.view.text_box.insert(idx, '\n\n')

                    # overwrite 'Found' at idx
                    self.view.text_box.tag_add('found', idx, lastidx)
                    idx = lastidx

                self.view.text_box.tag_config('found')

            self.r = Button(self.view.text_box, text=self.str_val, background='Green', command=lambda m=self.str_val: self.timelink(m))

            self.timevalue = self.r.cget('text')
            self.timevalues.append(self.timevalue)
            timer_list.append(self.timevalue)
            if (findtext and self.r):
                idx = '1.0'
                while 1:
                    # searches for desired string from index 1
                    idx = self.view.text_box.search(findtext, idx, nocase=1, stopindex=END)
                    if not idx: break
                    # last index sum of current index and
                    # length of text
                    lastidx = '% s+% dc' % (idx, len(findtext))
                    self.view.text_box.insert(idx, '\n\n Speak')
                    self.view.text_box.delete(idx, lastidx)
                    self.view.text_box.window_create(self.view.text_box.index(idx), window=self.r)

                    num = 3
                    lastidx = '% s+% dc' % (idx, num)

                    # overwrite 'Found' at idx
                    self.view.text_box.tag_add('found', idx, lastidx)
                    idx = lastidx

                self.view.text_box.tag_config('found')

    def timelink(self, button_press):
        # print('button pressed', button_press)
        # print('inside', self.timevalues)
        self.view.slider.config(value=int(button_press))
        self.play_audio()

    global opened_file_name
    opened_file_name = False

    def open_file(self):
        if self.view.transcribe_text_file:
            global opened_file_name
            opened_file_name = self.view.transcribe_text_file[0]

        transcribed_file_path = os.path.split(self.view.transcribe_text_file[0])
        print(transcribed_file_path[1])
        self.text_file = transcribed_file_path[1]
        self.view.transcribe_text_file = open((self.view.transcribe_text_file[0]), 'r')
        transcribed_text = self.view.transcribe_text_file.read()
        self.view.add_text(transcribed_text)
        self.view.transcribe_text_file.close()
        self.view.top.destroy()

    def save_file(self):
        global opened_file_name
        if opened_file_name:
            transcribe_file_save = open(opened_file_name, 'w')
            transcribe_file_save.write(self.view.text_box.get("1.0", END))
            transcribe_file_save.close()
        else:
            self.saveAs_file()
        self.view.top.destroy()

    def saveAs_file(self):
        if self.view.transcribe_file_save:
            self.file_name = self.view.transcribe_file_save
            filepath = os.path.split(self.view.transcribe_file_save)
            self.file_name = self.file_name.replace(filepath[0], "")

            transcribe_file_save = open(self.view.transcribe_file_save, 'w')
            transcribe_file_save.write(self.view.text_box.get("1.0", END))
            transcribe_file_save.close()
        self.view.top.destroy()

    def open_list(self):
        if self.view.excel_file_name:
            try:
                self.view.excel_file_name = r"{}".format(self.view.excel_file_name[0])
                self.df = pd.read_excel(self.view.excel_file_name)
            except ValueError:
                print("file couldn't be open")

        self.clear_list()

        self.view.annotation_box['column'] = list(self.df.columns)
        self.view.annotation_box['show'] = "headings"

        for column in self.view.annotation_box["column"]:
            self.view.annotation_box.heading(column, text=column)

        self.df_rows = self.df.to_numpy().tolist()
        for row in self.df_rows:
            self.view.annotation_box.insert("", "end", values=row)

        self.view.listtop.destroy()

    def save_list(self):
        if len(self.view.annotation_box.get_children()) < 1:
            mb.showinfo("No data", "No data to export")
            return False

        with open(self.view.save_annotation_list, mode='a', newline='') as my_excel_file:
            write = csv.writer(my_excel_file, dialect='excel')
            for i in self.view.annotation_box.get_children():
                row = self.view.annotation_box.item(i)['values']
                write.writerow(row)
        mb.showinfo("Message", "Export successfully")
        self.view.listtop.destroy()

    def clear_list(self):
        self.view.annotation_box.delete(*self.view.annotation_box.get_children())

    def lookup(self):
        lookup_record = self.view.search_entry.get()
        selections = []
        # print(lookup_record)
        self.view.annotation_box['column'] = list(self.df.columns)
        self.view.annotation_box['show'] = "headings"

        for record in self.view.annotation_box.get_children():
            if lookup_record in self.view.annotation_box.item(record)['values']:
                print(self.view.annotation_box.item(record)['values'])
                selections.append(record)
        self.view.annotation_box.selection_set(selections)
        self.view.search.destroy()
