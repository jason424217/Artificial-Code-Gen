import os
import numpy as np
import glob
import pickle
import gensim
import tqdm
import collections
import random
from pathlib import Path

def load_dataset(path):
    paths = []
    if os.path.isfile(path):
        # Simple file
        paths.append(path)
    elif os.path.isdir(path):
        # Directory
        for i, (dirpath, _, fnames) in enumerate(os.walk(path)):
            for fname in fnames:
                paths.append(os.path.join(dirpath, fname))
    else:
        # Assume glob
        paths = glob.glob(path)

        
    token_chunks = []
    raw_text = ''
    for i, path in enumerate(tqdm.tqdm(paths)):
        try:
            with open(path, 'r', encoding="iso-8859-1") as fp:
                raw_text += fp.read()
            tokens = raw_text
            token_chunks.append(tokens)
            raw_text = ''
        except Exception as e:
            print(e)
    return token_chunks
    
def generate_corpus(dataset, tokens_only=False):
    for i, method in enumerate(dataset):
        try:
            if tokens_only:
                yield gensim.utils.simple_preprocess(method)
            else:
                # For training data, add tags
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(method), [i])
        except Exception as e:
            print(e)
            continue

class D2VEmbedder:
    def __init__(self, model_path):
        self.model = gensim.models.doc2vec.Doc2Vec.load(model_path)
        
    def __call__(self, ds_path):
        methods = load_dataset(ds_path)
        d2v_methods = list(tqdm.tqdm(generate_corpus(methods, tokens_only = True)))
        
        feature_dict = {}
        for i in tqdm.tqdm(range(len(d2v_methods))):
            features = self.model.infer_vector(d2v_methods[i])
            feature_dict[methods[i]] = features
            
        return feature_dict