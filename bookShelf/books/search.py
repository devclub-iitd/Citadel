import os

TAG = "=="
META_EXTENSION = ".meta"
DATABASE_DIR = "../media/database"
EXCLUDE_SET=['Assignments', 'Question-Papers','Minor1','Minor2','Major','Books','Others','Professors']

				
def get_file_loc(meta_file):
	"""
		function to provide the actual file location and name from the name of its metafile
	"""
	desc = meta_file.split(TAG)
	if (len(desc) == 3):
		if (desc[-1] == META_EXTENSION):
			file_name = desc[0]
			raw_loc = desc[1]
			dirs = raw_loc.split('-')
			file_dir = os.path.join(*dirs)
			file_loc = os.path.join(file_dir, file_name)
			return (file_name, file_loc)
	return (meta_file, None)

def searchterm_match(term, string):
	"""
		returns 2 for perfect match, and 1 if term is substring
	"""
	if term.lower() in string.lower():
		if term.lower() == string.lower():
			return 2
		else:
			return 1
	else:
		return 0

def match_string(keyword_list, check_list):
	"""
		gives degree of matching for ranking 
	"""
	matches=0
	perfect_matches=0
	for term in keyword_list:
		match_value=0   # to reset for each term, in case of empty keyword_list
		for string in check_list:
			match_value=searchterm_match(term,string)
			if match_value:
				break
		if match_value>0:
			matches+=1
			if match_value>1:
				perfect_matches+=1
	return (matches,perfect_matches)

def get_meta(meta_path_prefix, check_list):
	"""
		reads meta tags and adds to check_list
	"""
	path=''
	for node in meta_path_prefix:
		path+= '/'+ node[0]
	path=DATABASE_DIR+path
	f = open(path, "r")
	for line in f:
		check_list.append(line.rstrip())
	f.close()


def get_search_list(db,result,path_prefix,keyword_list):
	"""
		passes matching path_prefixes and their matches into result
	"""
	for key in db:
		is_dict=type(db[key]) is dict
		name=key
		check_list=[]
		if not is_dict:
			(name,location)=get_file_loc(name)
			if location != None :
				meta_path_prefix=path_prefix[:]
				meta_path_prefix.append([key])
				get_meta(meta_path_prefix,check_list)
				pass

		check_list.append(name)
		(matches,perfect_matches)=match_string(keyword_list, check_list)
		if matches and key not in EXCLUDE_SET:
			new_path_prefix=path_prefix[:]
			new_path_prefix.append([key])
			result.append((new_path_prefix,matches,perfect_matches))

		if is_dict:
			new_path_prefix=path_prefix[:]
			new_path_prefix.append([key])
			get_search_list(db[key],result,new_path_prefix,keyword_list)


def search_dic(db,path_prefix,keyword_list):
	"""
		sorts results based on no of matches, perfect matches, and depth in structure.
		python search is stable, so sorted in reverse order of criteria importance
	"""
	result=[]
	get_search_list(db,result,path_prefix,keyword_list)
 
	result.sort(key=lambda x: len(x[0]))
	result.sort(key=lambda x: x[2], reverse=True)
	result.sort(key=lambda x: x[1], reverse=True)
	path_list=[]
	for i in result:
		path_list.append(i[0])
	return path_list

def get_path_prefix(path):
	"""
		gets path_prefixe given path
	"""
	temp_path=list(filter(None, path.split("/")))
	j=0
	path_prefix=[]
	for node in temp_path:
		path_prefix.append([node])
	return path_prefix
	