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
            myweights.append(np.array([0.]))
        else:
            w = np.zeros(d.shape)
            w[np.argmin(d)] = 1.
            myweights.append(w)

    m = np.array(myweights, dtype=np.float64)

    return m

# A classic KNN classifier
class EmbeddingClassifierKNN:

    def __init__(self, path):
        self.laser = Laser()
        with open(path, 'rb') as fin:
            self.clf = pickle.load(fin)

    # Expects a list of italian texts
    def embed(self, texts):
        return self.laser.embed_sentences(texts, lang='it')

    def classify(self, texts):

        confidences = self.clf.predict_proba(self.embed(texts))

        predictions = [self.clf.classes_[i] for i in confidences.argmax(axis=1)]
        confidences = [np.round(c, 2) for c in list(confidences.max(axis=1) / 1)]

        return predictions, confidences

# A KNN with radius threshold classifier
class EmbeddingClassifierRKNN:

    def __init__(self, path):
        self.laser = Laser()
        with open(path, 'rb') as fin:
            self.clf = pickle.load(fin)
        # self.clf.weights = weightmax # piggyback
        # self.clf.weights = "distance"

    # Expects a list of italian texts
    def embed(self, texts):
        return self.laser.embed_sentences(texts, lang='it')

    def classify(self, texts):

        predictions = self.clf.predict(self.embed(texts))

        radiuses = []
        for t_, p_ in zip(self.clf.radius_neighbors(self.embed(texts))[0], predictions):
            if t_.size == 0 or p_ == 0.:
                radiuses.append(0.)
            else:
                radiuses.append(np.round(1. - np.average(t_), 2))

        return (predictions, radiuses)