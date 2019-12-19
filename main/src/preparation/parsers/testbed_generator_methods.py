import os
import os.path
import sys
import ntpath
import random

from os import listdir
from os.path import isfile, join


def read_file(path, start_i, end_i):
    function_c = []
    with open(path, "r", encoding='UTF-8') as fp:
        for i, line in enumerate(fp):
            if i >= (start_i[0]) and i <= (end_i[0]):
                if start_i[0] == end_i[0]:
                    function_c.append(line[start_i[1]:end_i[1]])
                elif i == start_i[0]:
                    function_c.append(line[start_i[1]:])
                elif i == end_i[0]:
                    function_c.append(line[:end_i[1]])
                else:
                    function_c.append(line)

    return function_c


def write_to_file(input_path, file_extension):
    dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(input_path))), 'methods_testbed')
    if (not os.path.isdir(dir_path)):
        os.mkdir(dir_path)

    with open(input_path, 'r', encoding='UTF-8') as fp:
        data = [(random.random(), line) for line in fp]
    data.sort()

    filename = path_leaf(input_path).rsplit(".", 1)[0]
    name = filename + '_testbed.' + file_extension
    name_path = os.path.join(dir_path, name)

    with open(name_path, 'w', encoding='UTF-8') as target:
        for line in data:
            target.write(line[1])
    print('wrote ' + name_path + ' to file')


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


if __name__ == "__main__":
    language_type = sys.argv[1].split('/')[-1]
    allrepos = []
    for repo in listdir(sys.argv[1]):
        if os.path.isdir(os.path.join(sys.argv[1], repo)):
            allrepos.append(os.path.join(sys.argv[1], repo))
    count = 0
    allfiles = []
    allfolders = []
    for repo in allrepos:
        for folder in listdir(repo):
            if os.path.isdir(os.path.join(repo, folder)):
                allfolders.append(os.path.join(repo, folder))
    for folder in allfolders:
        allfiles = [os.path.join(folder, f) for f in listdir(folder) if isfile(join(folder, f))]
        for i in range(len(allfiles)):
            file_extension = path_leaf(allfiles[i]).split(".")[-1]
            if count < 100:
                write_to_file(allfiles[i], file_extension)
                count = count + 1
            else:
                break

