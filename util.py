import sys
import distutils.util as du
import json

def load_json_file(path):
    return json.loads(open(path, 'r').read())

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
