from pathlib import Path
import os
import glob
import tqdm

def load_dataset(enc, path, sample = None):
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
        if sample is not None:
            if i >= sample:
                break
        try:
            with open(path, 'r') as fp:
                raw_text += fp.read()
            tokens = raw_text
            token_chunks.append(tokens)
            raw_text = ''
        except Exception as e:
            print(e)
        
    return token_chunks