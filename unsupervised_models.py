# coding=utf-8
import re

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


class HateSpeechDictionary:

    def __init__(self, path):

        self.word = {}
        file=open(path+"hatespeech_dictionary.csv", 'r')
        is_first=True
        for row in file:
            if is_first:
                is_first=False
                continue
            #print(row)
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

        for key, value in self.word.items():
           if re.findall(u" ("+key.replace("*","{1,}[a-zàèéòìù]")+") ",text.lower()):
            go=True
            for k in keys:
                #print(k,key)
                if k[:-1] == key[:-1]:
                    go=False
            keys.append(key)
            if go:
                score+=1
            for dim, val in value.items():
                if len(val)>0:
                    dimension.append(dim)
            tokens.append({"word":key,"scores":dimension})


        return score,set(dimension),tokens

