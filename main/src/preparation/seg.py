# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:40:31 2019

@author: shzho
"""

import sentencepiece as spm
import os
import operator
import collections
from itertools import islice
import json
import statistics
import numpy as np
import pandas as pd


os.chdir("C:/Users/shzho/Desktop/cs435/java")
sp = spm.SentencePieceProcessor()
#C:\Users\shzho\Desktop\cs435\java\caged_microsis

datafram1 = pd.read_csv('javafile.csv', delimiter = ',')
datafram2 = pd.read_csv('javamethod.csv', delimiter = ',')

fileAll = "fileAll.txt"
with open(fileAll, "w+", encoding='UTF-8') as fp:
    for file in datafram1.file:
        fp.write(file+"\n")
    
spm.SentencePieceTrainer.Train('--input=fileAll.txt \
                               --model_prefix=m --vocab_size=1000 --model_type=bpe')

sp.Load("m.model")
decodefile = "decode.txt"
freq = {}
method_token_num = []

#with open(encodefile, "r", encoding='UTF-8') as fp1:
with open(decodefile, "w+", encoding='UTF-8') as fp:
    for methods in datafram2.method: #TODO
        str1 = sp.encode_as_pieces(methods)
        for piece in str1:
            freq.setdefault(piece, 0)
            freq[piece] += 1
        str2 = sp.decode_pieces(str1)
        fp.write(str2+"\n")
        method_token_num.append(len(str1))

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

sorted_freq_in = sorted(freq.items(), key=operator.itemgetter(1))
sorted_freq_de = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
sorted_dict_in = collections.OrderedDict(sorted_freq_in)
sorted_dict_de = collections.OrderedDict(sorted_freq_de)
most_freq_20 = take(20, sorted_dict_de.items())
least_freq_20 = take(20, sorted_dict_in.items())
#print(most_freq_20)
#print(least_freq_20)
mostfreqfile = "mostfrequence.txt"
leastfreqfile = "leastfrequence.txt"
statfile = "stat.txt"
#print(len(freq))
#print(freq)
mean = statistics.mean(method_token_num)
if(len(method_token_num)>=2):
    variance = statistics.variance(method_token_num)
else:
    variance = None
    
    
    
    
with open(mostfreqfile, "w+", encoding='UTF-8') as fp:
    fp.write(json.dumps(most_freq_20))
with open(leastfreqfile, "w+", encoding='UTF-8') as fp:
    fp.write(json.dumps(least_freq_20))
    
with open(statfile, "w+", encoding='UTF-8') as fp:
    fp.write("mean value of this type of code methods' token number is: "+str(mean)+"\n")
    if(variance is not None):
        fp.write("variance value of this type of code methods' token number is: "+str(variance)+"\n")