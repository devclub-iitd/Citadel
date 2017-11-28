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
          d[x]=path_to_dict(os.path.join(path,x))
    #    d[os.path.basename(path)] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        return "file"
    return d

# print(json.dumps(path_to_dict('.')))
def path_to_dict(path):
        if os.path.isfile("paths.txt"):
            f=open("paths.txt","r").read()
            heirarchy=json.loads(f)
        else:
            heirarchy=generate_path(path)
            # print(heirarchy)
            f = open("paths.txt","w+")
            f.write(json.dumps(heirarchy))
        return heirarchy

def recreate_path(path):
    heirarchy=generate_path(path)
    # print(heirarchy)
    f = open("paths.txt","w+")
    f.write(json.dumps(heirarchy))
    return heirarchy
