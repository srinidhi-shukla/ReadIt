#Convert Hindi and English text to audio of desired voice
#....English can have different voices male, female and neutral - done
#....Language Detect - done
#text summerization extraction and abstraction, this model is based on the TextRank Algorithm
#https://towardsdatascience.com/understand-text-summarization-and-create-your-own-summarizer-in-python-b26a9f09fc70

""" tasks
1. OCR configuration
2. Tkinter attachment
3. Final configurations

 """



from gtts import gTTS
import pyttsx3
import os
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from langdetect import detect
import json
import time
from io import BytesIO
from tkinter import *
from tkinter import Menu, BOTH
import tkinter as tk
from tkinter import filedialog as fd
from PIL import Image, ImageEnhance
import pytesseract
from pytesseract import image_to_string
from tkinter.messagebox import showinfo


class Text_summer_audio():
    def __init__(self):
        self.comp_data = dict()  
        self.summaries = []
            

    def read_file(self,filedata):
        article = filedata.split(". ")
        sentences = []
        for sentence in article:
            #print(sentence)
            sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
        sentences.pop() 
        return sentences


    def common_sent(self, sent1, sent2, stopwords=None):
        if stopwords is None:
            stopwords = []
        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]
        all_words = list(set(sent1 + sent2))
        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)
        for w in sent1:
            if w in stopwords:
                continue
            vector1[all_words.index(w)] += 1
        for w in sent2:
            if w in stopwords:
                continue
            vector2[all_words.index(w)] += 1
        return 1 - cosine_distance(vector1, vector2)

    def similar_matrix(self,sentences, stop_words):
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2:
                    continue 
                similarity_matrix[idx1][idx2] = self.common_sent(sentences[idx1], sentences[idx2], stop_words)
        return similarity_matrix

    def summary(self,file_name, top_n=5):
        stop_words = stopwords.words('english')
        summarize_text = []
        sentences =  self.read_file(file_name)
        sentence_similarity_martix = self.similar_matrix(sentences, stop_words)
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
        scores = nx.pagerank(sentence_similarity_graph)
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
        #print("Indexes of top ranked_sentence order are ", ranked_sentence)    
        for i in range(top_n):
            summarize_text.append(" ".join(ranked_sentence[i][1]))
        # Step 5 - Offcourse, output the summarize texr
        comp_text = ' '.join(summarize_text)
        return comp_text




    def OCR_read(self,filename):
        #filename = self.select_file()
        #D:/vSens/python/Python37-32/UNT Codes/Nidhi_project/59b5a8e9ecfc19ea850fed76b4c7f6c6.jpg
        img = Image.open(filename)
        # converts the image to result and saves it into result variable
        enhancer1 = ImageEnhance.Sharpness(img)
        enhancer2 = ImageEnhance.Contrast(img)
        enhancer3 = ImageEnhance.Brightness(img)
        img_edit = enhancer1.enhance(20.0)
        img_edit = enhancer2.enhance(1.5)
        img_edit = enhancer3.enhance(1.5)
        img_edit.save("edited_image.png")
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        result = pytesseract.image_to_string(img_edit,lang = 'eng+tel+hin+kan')
        MyGUI.greet(self,result)
        self.other_speech(result,"audio_file")

    def other_speech(self,mytext,read_data):
        language = detect(mytext)
        mp3_fp = BytesIO()
        myobj = gTTS(text=mytext, lang=language, slow=False)
        myobj.save(read_data+".mp3")
        os.system(read_data+".mp3")
        #myobj.write_to_fp(mp3_fp)

    def Run(self,filename):
        with open(filename) as json_file:
            self.comp_data = json.load(json_file)
        for keys,values in self.comp_data.items():
            summarize_text = self.summary( values, 2)
            print(summarize_text)
            self.other_speech(summarize_text,"audio_file")
            self.summaries.append(summarize_text)
    
        

class MyGUI(Text_summer_audio):
    def __init__(self, master):
        self.master = master
        master.title("Title as you wish")

        self.label = Label(master, text="Select option to either read text from image or Text summerization")
        self.label.pack()

        self.greet_button = Button(master, text="Image to audio", 
                command=lambda : self.intrim(1))
        self.greet_button.pack(side = LEFT)


        self.close_button = Button(master, text="Text Document Summarization", command=lambda : self.intrim(2))
        self.close_button.pack(side = RIGHT)

    def intrim(self,num):
        filetypes = (
            ('image files', '*.jpg'),
            ('image files', '*.jpeg'),
            ('image files', '*.png'),
            ('Text files', '*.txt'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        if num==1:
            Text_summer_audio.OCR_read(self,filename)
        else:
            Text_summer_audio.Run(self,filename)
        

    def greet(self,matter):
        self.label.config(text = matter)

root = Tk()
root.geometry("600x400")
my_gui = MyGUI(root)
root.mainloop()

