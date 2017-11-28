# import os
# import json

# def path_to_dict(path):
#     d = {}
#     if os.path.isdir(path):
#         # d['type'] = "directory"
#         d[os.path.basename(path)] = [path_to_dict(os.path.join(path,x)) for x in os.listdir\
# (path)]
#     else:
#         d[os.path.basename(path)] = "file"
#     return d

import os
import json

def generate_path(path):
    d = {}
    if os.path.isdir(path):
        # d['type'] = "directory"
        for x in os.listdir(path):
          d[x]=generate_path(os.path.join(path,x))
    #    d[os.path.basename(path)] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        return "file"
    return d

# print(json.dumps(path_to_dict('.')))
def path_to_dict(path,name_of_file):
    ## checks if file with name exists and if it doesnt it recreates a all the heirarchy
        if os.path.isfile(name_of_file):
            f=open(name_of_file,"r").read()
            heirarchy=json.loads(f)
        else:
            heirarchy=generate_path(path)
            # print(heirarchy)
            f = open(name_of_file,"w+")
            f.write(json.dumps(heirarchy))
        return heirarchy

def recreate_path(path,name_of_file):
    ##forces the recreation of heirarchy
    heirarchy=generate_path(path)
    # print(heirarchy)
    f = open(name_of_file,"w+")
    f.write(json.dumps(heirarchy))
    return heirarchy
