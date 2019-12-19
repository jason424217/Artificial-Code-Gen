from pymongo import MongoClient
import os
import pandas as pd
import json

client = MongoClient('localhost', 27017)
db = client.test
collection = db.file_level

LANGUAGE_PATH='../../../data/data_frames'
LANGUAGE = 'cpp'
path = os.path.join(LANGUAGE_PATH, LANGUAGE)
train_path = os.path.join(path, str(LANGUAGE + '_file_' +'train_df.pkl'))
test_path = os.path.join(path, str(LANGUAGE + '_file_' +'test_df.pkl'))
validation_path = os.path.join(path, str(LANGUAGE + '_file_' +'validate_df.pkl'))

train_df = pd.read_pickle(train_path, compression='gzip')
test_df = pd.read_pickle(test_path, compression='gzip')
validate_df = pd.read_pickle(validation_path, compression='gzip')

records = json.loads(test_df.to_json(orient='records'))
for record in records:
    record['partition'] = 'test'
    # print(record)
    collection.insert_one(record)
