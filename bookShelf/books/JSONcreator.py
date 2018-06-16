import os
import json
import collections
# from . import views


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

def navigate_path(db,path,forced):
    """
        Returns appropriate dict as pointed to by path.
        In case of invalid path raise appropriate exceptions
        If forced, creates path if it doesn't exist
    """
    keys = list(filter(None, path.split(os.sep)))
    for key in keys:
        if forced and key not in db.keys():
        	db[key]={}
        try:
            db = db[key]
        except Exception as e:
            raise InvalidPath
    if type(db) is str:
        raise FilePath
    return db

def truncate_db(db,depth):
    """
        Truncated database according to the given depth.
        Dictionary is truncated as None, while string is not truncated.
        E.g.
            db: {"CO":{"COL100":"foo"},"HU":"bar"}
            depth: 1
            result: {"CO":None,"HU":"bar"}
    """
    depth = int(depth)
    if (db=={}) or (type(db) is str):
        return db
    if depth==0:
        return None
    new_db = {}
    for key in db.keys():
        new_db[key] = truncate_db(db[key],depth-1)
    return new_db


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
    """
        Checks if file with name exists and if it doesnt it recreates all the heirarchy.
    """
    if os.path.isfile(name_of_file):
        f = open(name_of_file, "r").read()
        heirarchy = json.loads(f)
        if heirarchy == "file":
            heirarchy = {}
    else:
        heirarchy = generate_path(path)
        f = open(name_of_file, "w+")
        f.write(json.dumps(heirarchy))
    return heirarchy


def remove_zips_and_metas(data):
    """
        Function to remove all the zip files from the made database.json
    """
    if not isinstance(data, (dict, list)):
        return data
    if isinstance(data, list):
        return [remove_zips_and_metas(val) for val in data]
    return {k: remove_zips_and_metas(val) for k, val in data.items()
            if not k.lower().endswith(('.zip', '.meta'))}


def recreate_path(path, name_of_file):
    """
        Forces Recreation of hierarchy
    """
    heirarchy = generate_path(path)
    heirarchy = remove_zips_and_metas(heirarchy)
    f = open(name_of_file, "w+")
    f.write(json.dumps(heirarchy))
    return heirarchy
