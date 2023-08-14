# coding=utf-8
import os
import urllib.request
import numpy as np
from laserembeddings import Laser
# import pickle
# from sklearn.neighbors import RadiusNeighborsClassifier


# only nearest within radius counts
def weightmax(mylist):
    myweights = []
    for d in mylist:
        if len(d) < 1:
            myweights.append(np.array([]))
        else:
            w = np.zeros(d.shape)
            w[np.argmin(d)] = 1.
            myweights.append(w)
    return np.array(myweights, dtype=object)


class EmbeddingClassifier:

    def __init__(self):
        self.laser = Laser()
        #with open('model/clf.pkl', 'rb') as fin:
        #    self.clf = pickle.load(fin)
        #self.clf.weights = weightmax # piggyback

    # Expects a list of italian texts
    def embed(self, texts):
        return self.laser.embed_sentences(texts, lang='it')

    def classify(self, texts):
        deleteme = self.embed(texts)
        return True # self.clf.predict(self.embed(texts))
