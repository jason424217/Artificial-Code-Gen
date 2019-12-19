import os
import os.path
import sys
import ntpath

from os import listdir
from os.path import isfile, join

from tree_sitter import Language, Parser

Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    'tree-sitter-python',
    'tree-sitter-java',
    'tree-sitter-javascript',
    'tree-sitter-cpp'
  ]
)
  
PY_LANGUAGE = Language('build/my-languages.so', 'python')
J_LANGUAGE = Language('build/my-languages.so', 'java')
JS_LANGUAGE = Language('build/my-languages.so', 'javascript')
CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')



def func_name_extract(file_path):

	if not os.path.isfile(file_path):
		return
	f = open(file_path, "r", encoding='UTF-8', errors='ignore')
	
	tree = parser.parse(bytes(f.read(), "utf8"))

	root_node = tree.root_node
	index = len(root_node.children)
	
	func_list = []
	for i in range(index):
		curr = root_node.children[i]
		if curr.type == 'expression_statement':
			if curr.children[0].type == 'assignment_expression':
				if curr.children[0].children[2].type == 'function':
					startline = curr.start_point
					endline = curr.end_point
					startname = curr.children[0].children[0].start_point
					endname = curr.children[0].children[0].end_point
					with open(file_path, "r", encoding='UTF-8') as f:
						for i, line in enumerate(f):
							#print("test")
							if i == startname[0]:
								funcname = line[startname[1]:endname[1]]
								print(funcname)
								func = [funcname, startline, endline]
								func_list.append(func)
		elif curr.type == 'function_declaration':
			startline = curr.start_point
			endline = curr.end_point
			temp = 0
			while temp != len(curr.children) and curr.children[temp].type != 'identifier':
				temp += 1
			if temp == len(curr.children):
				continue
			startname = curr.children[temp].start_point
			endname = curr.children[temp].end_point
			with open(file_path, "r", encoding='UTF-8') as f:
				for i, line in enumerate(f):
					#print("test")
					if i == startname[0]:
						funcname = line[startname[1]:endname[1]]
						print(funcname)
						func = [funcname, startline, endline]
						func_list.append(func)
	#print(len(func_list))
	return func_list

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


def write_to_file(func_list, input_path, file_extension):
	dir_path = os.path.join(os.path.dirname(input_path), 'methods')
	content = []

	if (not os.path.isdir(dir_path)):
		os.mkdir(dir_path)
	filename = path_leaf(input_path).split(".", maxsplit=1)[0]
	for i in range(len(func_list)):
		function_name = func_list[i][0]
		print(function_name)
		name = filename + "_" + function_name + "_" + str(func_list[i][1]) + "." + file_extension
		name_path = os.path.join(dir_path, name)
		with open(name_path, "w", encoding='UTF-8') as fp:
			content = read_file(input_path, func_list[i][1], func_list[i][2])
			for line in content:
				fp.write(line)
def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)
def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)
if __name__=="__main__":
#def parse_python_repo(repo_path):
	if len(sys.argv) != 2:
		print('''Usage: python func_name_extract_function_all.py <output_file_directory_path>\n''')
		exit(-1)
	language_type = sys.argv[1].split('/')[-1]
	parser = Parser()
	if(language_type == 'py'):
		parser.set_language(PY_LANGUAGE)
	elif(language_type == 'java'):
		parser.set_language(J_LANGUAGE)
	elif(language_type == 'js'):
		parser.set_language(JS_LANGUAGE)
	elif(language_type == 'cpp'):
		parser.set_language(CPP_LANGUAGE)
	
	allfolders = []
	for folder in listdir(sys.argv[1]):
		if os.path.isdir(os.path.join(sys.argv[1], folder)):
			allfolders.append(os.path.join(sys.argv[1], folder))
	allrepos = []
	for folder in allfolders:
		for repo in listdir(folder):
			if os.path.isdir(os.path.join(folder, repo)):
				allrepos.append(os.path.join(folder, repo))
	for repo in allrepos:
		allfiles = [os.path.join(repo, f) for f in listdir(repo) if isfile(join(repo, f))]
		for files in allfiles:
			file_extension = path_leaf(files).split(".")[-1]
			func_list = func_name_extract(files)
			write_to_file(func_list, files, file_extension)


