# coding=utf-8
import re
import pickle

VERSION = 12

class Hurtlext:

    def __init__(self, path):

        self.conservative = {}
        self.inclusive    = {}
        file=open(path+"hurtlex_IT.tsv", 'r', encoding="utf8")
        is_first=True
        for row in file:
            if is_first:
                is_first=False
                continue
            pos,category,stereotype,lemma,level = row.replace("_"," ").replace("\n","").split("\t")
            #print(pos,category,stereotype,lemma,level)
            if level=='conservative':
                self.conservative[lemma]={'pos':pos,
                                     'category':category,
                                     'stereotype':stereotype}
            elif level=='inclusive':
                self.inclusive[lemma]={'pos':pos,
                                     'category':category,
                                     'stereotype':stereotype}


    def inclusive_score(self,text):
        score=0
        text = text.lower()
        text = re.sub(r"[,.;@#?!&$]+\ *", " ", text)
        text = re.sub(r"[ ]{1,}", " ", text)
        for key, value in self.conservative.items():
            if key in text:
                score+=1
        for key, value in self.inclusive.items():
            if key in text:
                score+=1

        return score

    def conservative_score(self,text):
        score=0
        text = text.lower()
        text = re.sub(r"[,.;@#?!&$]+\ *", " ", text)
        text = re.sub(r"[ ]{1,}", " ", text)
        for key, value in self.conservative.items():
            if key in text:
                score+=1

        return score

import pandas as pd
from langdetect import detect
from embedding_classifier import EmbeddingClassifierRKNN

def detekt(x):
    try:
        return detect(x)
    except:
        return 'ex'

class HateSpeechDictionaryV2:

    def __init__(self, path):
        d = pd.read_excel(path+"hatespeech_dictionary_glob.xlsx")

        # dplyr::select(-to_drop) %>%
        # dplyr::select(-animals) %>%
        # dplyr::select(-aggr_verb_family)
        del d['to_drop']
        del d['animals']
        del d['aggr_verb_family']

        # pivot_longer(
        #    cols = -word, names_to = "group"
        #  ) %>%
        #  filter(!is.na(value)) %>%
        #  dplyr::select(-value) %>%
        d = pd.melt(d, id_vars='word')
        d = d[~d.value.isnull()]
        del d['value']
        d.columns = ['word', 'group']
        d.sort_values(['group', 'word'], inplace=True)

        mymap = {"aggr_verb": "aggr_verb",
                 "despise": "aggr_verb",
                 "discr_pol": "aggr_verb",
                 "disgust": "aggr_verb",
                 "discr_abilism": "discr",
                 "discr_bodyshame": "discr",
                 "discr_homoph": "discr",
                 "discr_racism": "discr",
                 "discr_sexism": "discr",
                 "incivility_sport": "incivility"}
        d.group = d.group.replace(mymap)

        # One regular expression per dimension
        self.d = d
        self.regxs = d.groupby('group')['word'].apply(lambda x : '(\\b|^)(' + '|'.join(x).replace('*', '.*?\\b').replace('_', ' ') + ')(\\b|$)').to_dict()

        # Laser
        self.emb = EmbeddingClassifierRKNN('model/clf.22062024.binary.pickle')

    def score(self, p):

        dims = self.regxs.keys()
        dims_tokens = [d + '_tokens' for d in dims]
        p['text'] = p['text'].str.lower()

        for k, t in zip(dims, dims_tokens):
            p[k] = p['text'].str.count(self.regxs[k])

            matches = p['text'].str.extractall(self.regxs[k]).reset_index().groupby('level_0', as_index = False)[1].agg({t: ' '.join})
            matches.set_index('level_0', drop=True, inplace=True)
            matches.index.name = None

            p = p.merge(matches, how="left", left_index=True, right_index=True)
            p[t].fillna('', inplace=True)

        # dictionary scores
        p['score'] = p[dims].sum(axis=1)
        p['prediction_dict'] = (p['score'] > 0).astype(int)

        # tokens
        p['tokens_dimensions'] = p[dims_tokens].to_dict(orient='records')

        p['tokens'] = p[dims_tokens].stack().groupby(level=0).agg(" ".join).str.split().apply(set).str.join(' ')
        for d in dims_tokens: del p[d]

        # dimensions
        p['dimensions'] = p[dims].to_dict(orient='records')
        p.drop(dims, axis=1, inplace=True)

        # Language hint
        p['is_it'] = (p['text'].apply(detekt) == 'it').astype(int)

        # Embeddings classifier
        predictions, radiuses = self.emb.classify(p['text'].to_list())
        p['prediction_nnr'] = predictions
        # p['radiuses_nnr_bin'] = radiuses

        # Final prediction: dictionary or knn
        p['prediction'] = p['prediction_dict'] | p['prediction_nnr']

        p['version'] = VERSION

        return p.to_dict(orient='records')


class HateSpeechDictionary:

    def __init__(self, path):

        self.word = {}
        file=open(path+"hatespeech_dictionary.csv", 'r')
        is_first=True
        for row in file:
            if is_first:
                is_first=False
                continue
            word,to_drop,vulgar_gen,violence,insult_gen,insult_polit,insult_sport,disgust,hate_feelings,homophobia,ethrel_discr,sexism,bodyshame,disability = row.replace("_"," ").replace("\n","").split(",")

            self.word[word]={
                             'to_drop':to_drop,
                             'vulgar_gen':vulgar_gen,
                             'violence':violence,
                             'insult_gen':insult_gen,
                             'insult_polit':insult_polit,
                             'insult_sport':insult_sport,
                             'disgust':disgust,
                             'hate_feelings':hate_feelings,
                             'homophobia':homophobia,
                             'ethrel_discr':ethrel_discr,
                             'sexism':sexism,
                             'bodyshame':bodyshame,
                             'disability':disability
                             }

    def score(self,text):
        score=0
        dimension=[]
        tokens=[]
        text = text.lower()
        text = re.sub(r"[,.;@#?!&$]+\ *", " ", text)
        text = re.sub(r"[ ]{1,}", " ", text)
        text = " "+text+" "
        keys=[]

        # Check if a word exists
        for key, value in self.word.items():
           if re.findall(u" ("+key.replace("*","{1,}[a-zàèéòìù]")+") ",text.lower()):
            go=True
            for k in keys:
                # Set false if key already found
                if k[:-1] == key[:-1]:
                    go=False
            keys.append(key)
            if go:
                # Add 1 to score, once for key
                score+=1
            # Add all dimensions for this word
            for dim, val in value.items():
                if len(val)>0:
                    dimension.append(dim)
            tokens.append({"word":key,"scores":dimension})

        return score,set(dimension),tokens

from embedding_classifier import EmbeddingClassifierKNN

class AnswerChatterV2:

    def __init__(self):
        # Laser
        self.emb = EmbeddingClassifierKNN('model/clf.22062024.multipass.pickle')
        with open('model/mapping.risposte.pkl', 'rb') as f:
            self.mapping = pickle.load(f)

    def score(self, p):

        # Prediction: dictionary or knn
        predictions, confidences = self.emb.classify(p['text'].to_list())

        p['pattern'] = predictions
        p['confidences_nnr_multi'] = confidences
        p['confidences_nnr_multi_threshold'] = 0.15

        # Map prediction pattern to extended response
        mapped = []
        for y in predictions:
            y = y.strip()
            if y not in self.mapping:
                res = "Error in mapping pattern -> answer: this should never happen!"
            else:
                res = self.mapping[y]
            mapped.append(res.strip())

        p['answer'] = mapped

        p['version'] = VERSION

        return p.to_dict(orient='records')

