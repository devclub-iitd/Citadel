def match_string(keyword_list, check_list):
	#placeholder function for more sophisticated keyword matching
	for word in keyword_list:
		if word not in check_list:
			return False
	return True

def search_dic(dic,result,path_prefix,keyword_list):
	
	for key in dic:

		is_match=match_string(keyword_list,[key])
		is_dict=type(dic[key]) is dict

		if is_match:
			new_path_prefix=path_prefix[:]
			new_path_prefix.append([key])
			result.append(new_path_prefix)

		if is_dict:
			new_path_prefix=path_prefix[:]
			new_path_prefix.append([key])
			search_dic(dic[key],result,new_path_prefix,keyword_list)

		if not(is_match or is_dict):
			# metadata search
			pass
		
