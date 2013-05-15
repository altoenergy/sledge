import sys
import os.path
import distutils.util as du
import json

def featurePath(path):
    return os.path.expanduser("~/alto/features/%s" % path)

def cachePath(path):
    return os.path.expanduser("~/alto/cache/%s" % path)

def jsonPath(path):
    return os.path.expanduser("~/alto/json/%s" % path)
    
def load_json_file(path):
    return json.loads(open(jsonPath(path), 'r').read())

def get_str_input(prompt, default):
    response = raw_input(prompt)
    if (response == ""):
        return default
    return response

def get_bool_input(prompt, default):
    response = raw_input(prompt)
    if (response == ""):
        return default
    return bool(du.strtobool(response.lower()))

def get_int_input(prompt, default):
    response = raw_input(prompt)
    if (response == ""):
        return default
    return int(response)
