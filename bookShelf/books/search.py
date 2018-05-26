from . import views 

EXCLUDE_SET=['Assignments', 'Question-Papers','Minor1','Minor2','Major','Books','Others']


def searchterm_match(term, string):
	# returns 2 for perfect match, and 1 if term is substring
	if term.lower() in string.lower():
		if term.lower() == string.lower():
			return 2
		else:
			return 1
	else:
		return 0

def match_string(keyword_list, check_list):
	#placeholder function for more sophisticated keyword matching
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

def get_search_list(db,result,path_prefix,keyword_list):
	
	for key in db:
		is_dict=type(db[key]) is dict
		name=key
		check_list=[]
		if not is_dict:
			(name,location)=views.get_file_loc(name)
			if location != None :
				pass #add metadata to check_list
				###watch for newline errors

		check_list=[name]
		(matches,perfect_matches)=match_string(keyword_list, check_list)
		if matches and key not in EXCLUDE_SET:
			new_path_prefix=path_prefix[:]
			new_path_prefix.append([name])
			result.append((new_path_prefix,matches,perfect_matches))

		if is_dict:
			new_path_prefix=path_prefix[:]
			new_path_prefix.append([name])
			get_search_list(db[key],result,new_path_prefix,keyword_list)


def search_dic(db,path_prefix,keyword_list):
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
	temp_path=list(filter(None, path.split("/")))
	j=0
	path_prefix=[]
	for node in temp_path:
		path_prefix.append([node])
	return path_prefix




