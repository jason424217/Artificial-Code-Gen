import os
import os.path

from os import listdir
from os.path import isfile, join

import pickle
import re
import sys
import ntpath

type_list = ['int', 'char', 'float', 'double', 'bool', 'void', 'short', 'long', 'signed', 'struct']


def pickle_dump(root_path, data, file_name):
    os.chdir(root_path)
    fp = open(file_name, "w", encoding='UTF-8')
    pickle.dump(data, fp)
    fp.close()

def pickle_load(root_path, file_name):
    os.chdir(root_path)
    fp_case = open(file_name, "r", encoding='UTF-8')
    dict_case = pickle.load(fp_case)
    fp_case.close()
    return dict_case


def is_valid_name(name):
    if re.match("[a-zA-Z_][a-zA-Z0-9_]*", name) == None:
        return False
    return True

def is_func(line):
#int, __int64, void, char*, char *, struct Node, long long int, (void *)
#int func(int a, int *b, (char *) c)
    line = line.strip()
    if len(line) < 2:
        return None
# Rule 1: def must always start the function
    if 'def' not in line:
        return None
# Rule 2: (*) must in
    if '(' not in line: #or ')' not in line:
        return None
# Rule 3: # stands for #include or other primitives; / start a comment
    if line[0] == '#' or line[0] == '/':
        return None

# replace pointer * and & as space
    line = re.sub('\*', ' ', line)
    line = re.sub('\&', ' ', line)


# replace '(' as ' ('
    #re.sub('(', ' ( ', line)
    line = re.sub('\(', ' \( ', line)
    line_split = line.split()

    if len(line_split) < 2:
        return None

    bracket_num = 0
    for ch in line:
        if ch == '(':
            bracket_num += 1

    has_type = False
    for type_a in type_list:
        if type_a in line_split[0]:
            has_type = True
#    if has_type == False:
#        return None
#    print line
    if bracket_num == 1:
        for index in range(len(line_split)):
            if '(' in line_split[index]:
                return line_split[index - 1]
    else:
        line = re.sub('\(', ' ', line)
        line = re.sub('\)', ' ', line)
        line_split = line.split()
        index = 0
        for one in line_split:
            if is_valid_name(one):
                index += 1
                if index == 2:
                    return one
        return None

def get_line_type(line):
    #TODO not just start but also in-text, can done with first find the location of special character
    #then use the location to split the string to get rid of the part after #
    line = line.strip()
    if line.startswith("/*"):
#        print line
        return "comment_paragraph"
    elif line.startswith("//"):
        return "comment_line"


#def is_comment_begin(line):
#    if line.startswith("/*"):
#        return True
#    return False

def is_comment_end(line):
    #print line
    if '*/' in line:
        if(re.search(r"(\*\/)(?=(?:[^\"\']|[\"|\'][^\"\']*\")*$)", line) is not None):
            return True
    return False


def func_name_extract(file_path):

    if not os.path.isfile(file_path):
        return


    file_list = []
    with open(file_path, "r", encoding='UTF-8') as fp:
        for line in fp.readlines():
            file_list.append(line)

    func_list = []

    i = -1
    while i < len(file_list) - 1:
        i += 1
        line = file_list[i]
        line_type = get_line_type(line)
        if line_type == "comment_line" or line_type == "macro":
            continue
        elif line_type == "comment_paragraph":
            while not is_comment_end(file_list[i].strip()):
                i += 1
        else:
            func_name = is_func(line)
            if func_name != None:
                start_line = i
                left_brack_num = 0
                while True:
                    if(i >= len(file_list)):
                        print(file_path, "2")
                        break
                    line_type = get_line_type(file_list[i])
                    if line_type == "comment_line" or line_type == "macro":
                        i += 1
                        continue
                    elif line_type == "comment_paragraph":
                        while not is_comment_end(file_list[i].strip()):
                            if(i+1 >= len(file_list)):
                                print(file_path, i, len(file_list))
                                break                            
                            i += 1
                        i += 1
                        continue
                    line = (file_list[i]).strip()
                    if(re.search(r"({)(?=(?:[^\"\']|[\"|\'][^\"\']*\")*$)", line) is not None):
                        brack_list = re.findall(r"({)(?=(?:[^\"\']|[\"|\'][^\"\']*\")*$)", line)
                        left_brack_num += len(brack_list)
                    if(re.search(r"(})(?=(?:[^\"\']|[\"|\'][^\"\']*\")*$)", line) is not None):
                        brack_list = re.findall(r"(})(?=(?:[^\"\']|[\"|\'][^\"\']*\")*$)", line)
                        left_brack_num -= len(brack_list)
                        if left_brack_num < 1:
                            break
                    i += 1
                end_line = i
               # if func_name != None:
                func_list.append([func_name, start_line+1, end_line + 1])
    return func_list

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def read_file(path, start_i, end_i):
    function_s = []
    with open(path, "r", encoding='UTF-8') as fp:
        for i, line in enumerate(fp):
            if i >= (start_i-1) and i <= (end_i-1):
                function_s.append(line)
                
    return function_s

def write_to_file(func_list, input_path):
    dir_path = os.path.join(os.path.dirname(input_path), 'methods')
    content = []
    
    if(not os.path.isdir(dir_path)):
        os.mkdir(dir_path)
    filename = path_leaf(input_path).split(".", maxsplit=1)[0]
    for i in range(len(func_list)):
        function_name = re.sub('[^A-Za-z0-9]+', '_', str(func_list[i][0]))
        name = filename+"_"+function_name+"_"+str(func_list[i][1])+".scala"
        name_path = os.path.join(dir_path, name)
        with open(name_path, "w", encoding='UTF-8') as fp:
            content = read_file(input_path, func_list[i][1], func_list[i][2])
            for line in content:
                fp.write(line)
                
            

if __name__=="__main__":
#def parse_python_repo(repo_path):
	if len(sys.argv) != 2:
		print('''Usage: python func_name_extract_function_all.py <output_file_directory_path>\n''')
		exit(-1)	
	
	allrepos = []
	for repo in listdir(sys.argv[1]):
		if os.path.isdir(os.path.join(sys.argv[1], repo)):
			allrepos.append(os.path.join(sys.argv[1], repo))

	for repo in allrepos:
		allfiles = [os.path.join(repo, f) for f in listdir(repo) if isfile(join(repo, f))]
		for files in allfiles:
			file_extension = path_leaf(files).split(".")[-1]
			func_list = func_name_extract(files)
			write_to_file(func_list, files, file_extension)


