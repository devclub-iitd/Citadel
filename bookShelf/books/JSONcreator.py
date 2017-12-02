import os
import json

def generate_path(path):
    d = {}
    if os.path.isdir(path):
        for x in sorted(os.listdir(path)):
            new_path=generate_path(os.path.join(path,x))
            if not new_path:
                continue
            d[x]=new_path
    else:
        return "file"
    return d

def path_to_dict(path,name_of_file):

    """Checks if file with name exists and if it doesnt it recreates all the heirarchy."""

    if os.path.isfile(name_of_file):
        f=open(name_of_file,"r").read()
        heirarchy=json.loads(f)
        if(heirarchy=="file"):
            heirarchy={}
    else:
        heirarchy=generate_path(path)
        f = open(name_of_file,"w+")
        f.write(json.dumps(heirarchy))
    return heirarchy

def recreate_path(path,name_of_file):

    """Forces the recreation of heirarchy."""

    heirarchy=generate_path(path)
    f = open(name_of_file,"w+")
    f.write(json.dumps(heirarchy))
    return heirarchy
