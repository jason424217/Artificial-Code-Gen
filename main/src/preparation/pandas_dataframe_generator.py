import pandas as pd
import sys
import os


def save_to_pickle(dataframe, path, language, partition, data_level):
    pickle_path = os.path.join(path, "../dataframes", language)
    if not os.path.exists(pickle_path):
        os.makedirs(pickle_path)
    pickle_name = f"{language}_{data_level}_{partition}.pkl"
    pickle_path = os.path.join(pickle_path, pickle_name)
    dataframe.to_pickle(pickle_path, compression="gzip")

def file_level_data(data_level, language, partition_type, path):
    data = []
    for repository in os.listdir(path):
        repository_path = os.path.join(path, repository)
        if not os.path.isdir(repository_path): # This is just a failsafe in case a file gets in the folder of repositories
            continue
        for file in os.listdir(repository_path):
            file_path = os.path.join(repository_path, file)
            if os.path.isdir(file_path): # Skips over the methods folder within each repository
                continue
            with open (file_path, "r") as myfile:
                data.append([data_level, language, partition_type, repository, file, myfile.read()])
    return data

def function_level_data(data_level, language, partition_type, path):
    data = []
    for repository in os.listdir(path):
        repository_path = os.path.join(path, repository)
        if not os.path.isdir(repository_path):
            continue
        for file in os.listdir(repository_path):
            file_path = os.path.join(repository_path, file)
            if os.path.isdir(file_path) and file == "methods":
                for method in os.listdir(file_path):
                    method_path = os.path.join(file_path, method)
                    with open (method_path, "r") as myfile:
                        data.append([data_level, language, partition_type, repository, method, myfile.read()])
    return data

def dataframe_from_partition(language, path, partition_type, data_level):
    if data_level == 'file':
        data = file_level_data(data_level, language, partition_type, path)
    elif data_level == 'function':
        data = function_level_data(data_level, language, partition_type, path)
    field_names = ["data_level", "language", "partition", "repository", "file_name", "contents"]
    df = pd.DataFrame(data, columns=field_names)
    return df

def process_path(path, language_target, partition_target, data_level):
    for language in os.listdir(path):
        language_path = os.path.join(path, language)
        if (not os.path.isdir(language_path) or (language_target and (language != language_target))):
            continue
        for partition in os.listdir(language_path):
            partition_path = os.path.join(language_path, partition)
            if (not os.path.isdir(partition_path) or (partition_target and (partition != partition_target))):
                continue
            pd_dataframe = dataframe_from_partition(language, partition_path, partition, data_level)
            save_to_pickle(pd_dataframe, path, language, partition, data_level)

def main():
    if len(sys.argv) > 2:
        path = sys.argv[1]
        data_level = sys.argv[2]
        if (data_level != 'file') and (data_level != 'function'):
            print("Error: 'data_level' input must be 'file' or 'function'")
            exit()
        language_target = None
        partition_target = None
        if len(sys.argv) > 3: # If a language is specified, pass that into process_path()
            language_target = sys.argv[3]
            if len(sys.argv) > 4: # If a partition type is specified, pass that into process_path()
                partition_target = sys.argv[4]
        process_path(path, language_target, partition_target, data_level)
    else:
        print("ERROR: Path and data level inputs required, please run again with both")

if __name__ == "__main__":
    main()
