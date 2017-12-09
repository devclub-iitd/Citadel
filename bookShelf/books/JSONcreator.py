import os
import json
import collections

class FilePath(Exception):
    """
        Raised when the path given is pointing to a file
        instead of a director
    """
    pass
class InvalidPath(Exception):
    """
        Raised when the path given is not a valid heirarchical
        structure in the database
    """
    pass

def navigate_path(db,path):
    """
        Returns appropriate dict as pointed to by path.
        In case of invalid path raise appropriate exceptions
    """
    keys = list(filter(None, path.split("/")))
    for key in keys:
        try:
            db = db[key]
        except Exception as e:
            raise InvalidPath
    if type(db) is str:
        raise FilePath
    return db

def build_nav_path(prefix,path):
    """
        Builds a list of tuple for access links.abs
        E.g.
            prefix: /books/view/
            path: CO/COL100
            result:
                [("Home","/books/view"),("CO","/books/view/CO"),("COL100","/books/view/COL100")]
    """
    result = [("Home",prefix)]
    acc = prefix
    keys = list(filter(None, path.split("/")))
    for key in keys:
        acc = os.path.join(acc,key)
        result.append((key,acc))
    return result

def generate_path(path):
    d = collections.OrderedDict()
    if os.path.isdir(path):
        for x in sorted(os.listdir(path)):
            new_path=generate_path(os.path.join(path,x))
            if not new_path:
                continue
            d[x]=new_path
    else:
        ## TODO: MORE ROBUST PATH CONFIGURATION
        return path[2:]
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
