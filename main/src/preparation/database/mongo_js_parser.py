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



def func_name_extract(doc_contents):
	
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
					for j, line in enumerate(doc_contents.splitlines()):
						if j == startname[0]:
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
				for j, line in enumerate(doc_contents.splitlines()):
					if j == startname[0]:
						funcname = line[startname[1]:endname[1]]
						print(funcname)
						func = [funcname, startline, endline]
						func_list.append(func)

	return func_list

def read_file(content, start_i, end_i):
	results = ""
	for i, line in enumerate(content.splitlines(True)):
		if i >= (start_i[0]) and i <= (end_i[0]):
			if start_i[0] == end_i[0]:
				results = results + line[start_i[1]:end_i[1]]
			elif i == start_i[0]:
				results = results + line[start_i[1]:]
			elif i == end_i[0]:
				results = results + line[:end_i[1]]
			else:
                		results = results + line
		i += 1
	return results

def write_to_methods_collection(func_list, doc, input_path, num):
	for i in range(len(func_list)):
		function_name = func_list[i][0]
		content = read_file(doc.file_contents, func_list[i][1], func_list[i][2])
		insert = {"repo_name": doc.repo_name,
			"path_in_repo": doc.path_in_repo,
			"url":doc.url,
			"file_name": doc.file_name,
			"method_number": num,
			"method_name": function_name,
			"method_contents": content,
			"partition": doc.partition}
			num +=1
		collection.insert_one(insert)
	return num

if __name__=="__main__":
	try:
		conn = MongoClient()
		print("Connected successfully!!!")
	except:
		print("Could not connect to MongoDB")

	db = conn.file_level
	file_collection = db.js
	parser.set_language(JS_LANGUAGE)
	
	db2 = conn.method_level
	method_collection = db2.js

	num = 0
	for doc in file_collection.find():
		func_list = func_name_extract(doc.file_contents)
		num = write_to_methods_collection(func_list, doc, method_collection, num)


