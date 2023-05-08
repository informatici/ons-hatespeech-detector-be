# coding=utf-8
import csv
import random
import re

import numpy
from gensim.models import Word2Vec
from scipy.spatial import distance


def get_jaccard_sim(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))


class VeryDummyChatter:
    def __init__(self):
        self.basic_answer=[
                 'Perché sei cosi scontroso?',
                 'Non hai ragione di essere così violento',
                 'Potremmo moderare il linguaggio e discutere pacatamente.',
                 'Per favore, non essere volgare, ragioniamo in maniera civile.',
              ]

    def return_answer(self):
        return random.choice(self.basic_answer)

class DummyChatter:
    def __init__(self):
        # ATTENZIONE: contenuto di basic_hit_and_answer volgare, potrebbe urtare la vostra sensibilità
        self.basic_hit_and_answer = [
            ('Non compermi il cazzo!', 'Perché sei cosi scontroso?'),
            ('Ti riempirei di schiaffi!!', 'Non hai ragione di essere così violento'),
            ('Ma vai a farti fottere coglione di merda', 'Potremmo moderare il linguaggio e discutere pacatamente.'),
            ('Ficcati nel culo le tue teorie del cazzo', 'Per favore, non essere volgare, ragioniamo in maniera civile.'),
        ]

    def return_answer(self,text):
        best_answer=None
        best_answer_score=0
        for hit,answer in self.basic_hit_and_answer:
            score=get_jaccard_sim(hit,text)
            if score>best_answer_score:
                best_answer_score=score
                best_answer=answer

        if best_answer_score>0:
            return best_answer
        else:
            return random.choice(self.basic_hit_and_answer)[1]


class Chatter:
    def __init__(self):
        # gzip -9 tweets_2019_Word2Vect.bin
        file_name_input = "model/tweets_2019_Word2Vect.bin.gz"

        self.word2vec = Word2Vec.load(file_name_input)

        self.back_and_forth=[]
        csvfile= open('dataset/Tweet_piu_risposte.csv', newline='', encoding="utf8")
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(spamreader, None)  # skip the headers
        for row in spamreader:
            sentence=self.clean_text(row[2])
            doc_vector=self.return_doc_vector(sentence)
            self.back_and_forth.append((doc_vector,row[10]))

        csvfile.close()


    def clean_text(self,text):
        # Cleaing the text
        text = text.lower()
        text = re.sub('[^0-9a-zàáâãäåçèéêëìíîïòóôõöùúûüă]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        # Preparing the dataset
        words = [word for word in text.split(" ") if self.word2vec.wv.__contains__(word) ]
        return words

    def return_doc_vector(self,words):
        doc_vector=[]
        for word in words:
            doc_vector.append(self.word2vec.wv.__getitem__(word))
        if len(doc_vector)==0:
            return [0]
        matrix = numpy.array(doc_vector)
        #print(matrix)
        return  matrix.mean(axis=0)

    def return_answer(self,text):
        sentence=self.clean_text(text)
        doc_vector=self.return_doc_vector(sentence)

        print(sentence)
        print(doc_vector)

        best_i=0
        best_distance=distance.euclidean(self.back_and_forth[0][0], doc_vector)
        for i in range(1,len(self.back_and_forth)):
            cur_distance=distance.euclidean(self.back_and_forth[i][0],doc_vector)
            if best_distance>cur_distance:
                best_distance=cur_distance
                best_i=i
        print(best_distance)
        return  self.back_and_forth[best_i][1]


