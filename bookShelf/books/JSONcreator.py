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

def path_to_dict(path):
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