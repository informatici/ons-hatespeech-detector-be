# coding=utf-8
import numpy as np
from laserembeddings import Laser
import pickle
from sklearn.neighbors import RadiusNeighborsClassifier


# only nearest within radius counts
def weightmax(mylist):
    myweights = []
    for d in mylist:
        if len(d) < 1:
            myweights.append(np.array([], dtype=np.float64))
        else:
            w = np.zeros(d.shape, dtype=np.float64)
            w[np.argmin(d)] = 1.
            myweights.append(w)
    return np.array(myweights, dtype=np.float64)


class EmbeddingClassifier:

    def __init__(self, path):
        self.laser = Laser()
        with open(path, 'rb') as fin:
            self.clf = pickle.load(fin)
        self.clf.weights = weightmax # piggyback

    # Expects a list of italian texts
    def embed(self, texts):
        return self.laser.embed_sentences(texts, lang='it')

    def classify(self, texts):
        return self.clf.predict(self.embed(texts))
