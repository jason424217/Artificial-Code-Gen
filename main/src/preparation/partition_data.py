# reference to create symlinks: https://www.geeksforgeeks.org/python-os-symlink-method/
# Python program to explain os.symlink() method
import os
import heapq

TRAIN_PERCENT = 0.75
TEST_PERCENT = 0.1
VALIDATION_PERCENT = 0.1
BPE_PERCENT = 0.05

TRANSLATE_EXTENSIONS = {"cpp": "C++", "py": "Python", "scala": "Scala", "js": "JavaScript", "java": "Java"}

# Pass into partition_data() the path of the raw data folder, which is assumed to be in the following structure:
# - main
#   - data
#     - raw (what you pass in)
#       - cpp
#       - java
#       - js
#       - scala
#       - python
#     - partition (where files will be stored)
#       - cpp
#         - test
#         - train
#         - validation
#       - java
#         - test
#         - train
#         - validation
#       - js
#         - test
#         - train
#         - validation
#       - scala
#         - test
#         - train
#         - validation
#       - python
#         - test
#         - train
#         - validation


def partition_data(path_of_data_folder, max_files=-1):
    path_of_raw_data = os.path.join(path_of_data_folder, "raw")
    # /data/raw

    for file_type in os.listdir(path_of_raw_data):
        path_of_raw_and_extension = os.path.join(path_of_raw_data, file_type)
        # /data/raw/[cpp, java, js, python, scala]

        heap, total_files = heap_sort_by_num_of_files(path_of_raw_and_extension, max_files)
        print(heap, total_files)
        sort_heap_across_partitions(heap, total_files, path_of_data_folder, file_type)


def sort_heap_across_partitions(heap, total_files, path_of_data_folder, file_type):
    train_path, test_path, validate_path, bpe_path = make_folders_for_partitions(path_of_data_folder, file_type)
    turns = {0: train_path, 1: test_path, 2: validate_path, 3: bpe_path}
    file_limits = {train_path: total_files*TRAIN_PERCENT, test_path:total_files*TEST_PERCENT,
                   validate_path:total_files*VALIDATION_PERCENT, bpe_path: total_files*BPE_PERCENT}
    file_counts = {train_path: 0, test_path: 0, validate_path: 0, bpe_path: 0}
    turn = 0
    while len(heap) > 0:
        repo = heapq.heappop(heap)
        attempt = 0

        if file_counts[turns[turn]] + (-1 * repo[0]) < file_limits[turns[turn]]:
            symlink_repo(repo[1], turns[turn], repo[2])
            file_counts[turns[turn]] += (-1 * repo[0])

        else:
            for i in range(1, 4):
                attempt = (turn + i) % 4
                if file_counts[turns[attempt]] + (-1 * repo[0]) < file_limits[turns[attempt]]:
                    symlink_repo(repo[1], turns[attempt], repo[2])
                    file_counts[turns[attempt]] += (-1 * repo[0])

        turn = (attempt + turn + 1) % 4


def symlink_repo(repo_name, partition_path, path_of_raw_and_extension):
    src = os.path.join(path_of_raw_and_extension, repo_name)
    dest = os.path.join(partition_path, repo_name)
    print("Creating a symlink between " + src + " and " + dest)
    # if not os.path.exists(dest):
    #     os.makedirs(dest)

    # Create a symbolic link pointing to src named dst using os.symlink() method
    os.symlink(src, dest)


def make_folders_for_partitions(path_of_data_folder, file_type):
    path_of_partition_folder = os.path.join(path_of_data_folder, "partitions")
    # /data/partition
    if not os.path.exists(path_of_partition_folder):
        os.makedirs(path_of_partition_folder)

    path_of_partition_and_extension = os.path.join(path_of_partition_folder, file_type)
    # /data/partition/[cpp, java, js, python, scala]
    if not os.path.exists(path_of_partition_and_extension):
        os.makedirs(path_of_partition_and_extension)

    train_partition = os.path.join(path_of_partition_and_extension, "train")
    # /data/partition/[cpp, java, js, python, scala]/test
    if not os.path.exists(train_partition):
        os.makedirs(train_partition)

    test_partition = os.path.join(path_of_partition_and_extension, "test")
    # /data/partition/[cpp, java, js, python, scala]/test
    if not os.path.exists(test_partition):
        os.makedirs(test_partition)

    validate_partition = os.path.join(path_of_partition_and_extension, "validate")
    # /data/partition/[cpp, java, js, python, scala]/test
    if not os.path.exists(validate_partition):
        os.makedirs(validate_partition)

    bpe_partition = os.path.join(path_of_partition_and_extension, "bpe")
    # /data/partition/[cpp, java, js, python, scala]/test
    if not os.path.exists(bpe_partition):
        os.makedirs(bpe_partition)

    return train_partition, test_partition, validate_partition, bpe_partition


def heap_sort_by_num_of_files(path_of_raw_and_extension, max_files=-1):

    heap = list()
    total_files = 0

    # go through all repos in /data/raw/[cpp, java, js, python, scala] and label them according to file size
    for dirName, subdirList, fileList in os.walk(path_of_raw_and_extension):

        repo_name = split_the_path_into_a_list(dirName)[-1]

        # Check if you're at the repo level
        if repo_name not in TRANSLATE_EXTENSIONS.keys():
            # print("Repo name: " + repo_name + " has " + str(len(fileList)) + " files")
            repo_tuple = (-1 * len(fileList), repo_name, path_of_raw_and_extension)
            heapq.heappush(heap, repo_tuple)
            total_files += len(fileList)

        if max_files != -1 and total_files > max_files:
        	break

    return heap, total_files


def split_the_path_into_a_list(path):

    folders = []
    while 1:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break
    folders.reverse()
    return folders


partition_data("../../data", max_files=17376)
