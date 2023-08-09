# coding=utf-8
import os
import urllib.request
import numpy as np
import laserembeddings
from laserembeddings import Laser
import pickle
from sklearn.neighbors import RadiusNeighborsClassifier


def download_file(url, dest):
    if os.path.exists(dest):
        print(f'{url} already downloaded')
    else:
        print(f'Downloading {url}...')
        urllib.request.urlretrieve(url, dest)


def download_models(path):
    print(f'Downloading models into {path}')

    if not os.path.exists(path):
        os.makedirs(path)

    download_file('https://dl.fbaipublicfiles.com/laser/models/93langs.fcodes',
                  os.path.join(path, '93langs.fcodes'))
    download_file('https://dl.fbaipublicfiles.com/laser/models/93langs.fvocab',
                  os.path.join(path, '93langs.fvocab'))
    download_file(
        'https://dl.fbaipublicfiles.com/laser/models/bilstm.93langs.2018-12-26.pt',
        os.path.join(path, 'bilstm.93langs.2018-12-26.pt'))

    print('All set!')


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
        path = os.path.join(os.path.dirname(laserembeddings.__file__), 'data')
        download_models(path)
        self.laser = Laser()
        with open('model/clf.pkl', 'rb') as fin:
            self.clf = pickle.load(fin)
        self.clf.weights = weightmax # piggyback

    # Expects a list of italian texts
    def embed(self, texts):
        return self.laser.embed_sentences(texts, lang='it')

    def classify(self, texts):
        return self.clf.predict(self.embed(texts))
