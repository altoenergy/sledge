import sys
import os.path
import distutils.util as du
import pprint as pp
import json
import random
import math

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
    if (response == "_"):
        return ""
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

def xpath_elem(obj, path):
    elem = obj
    if (path == ""):
        return elem
    try:
        for x in path.strip("/").split("/"):
            try:
                x = int(x)
                elem = elem[x]
            except ValueError:
                elem = elem.get(x)
    except:
        pass

    return elem

def parse_number_list(s):
    ranges = (x.split("-") for x in s.split(","))
    return [i for r in ranges for i in range(int(r[0]), int(r[-1]) + 1)]

class Point:
    def __init__(self, coords, reference=None):
        self.coords = coords
        self.n = len(coords)
        self.reference = reference
    def __repr__(self):
        return str(self.coords)

class Cluster:
    def __init__(self, points):
        if len(points) == 0: raise Exception("ILLEGAL: empty cluster")
        self.points = points
        self.n = points[0].n
        for p in points:
            if p.n != self.n: raise Exception("ILLEGAL: wrong dimensions")
        self.centroid = self.calculateCentroid()
    def __repr__(self):
        return str(self.points)
    def update(self, points):
        old_centroid = self.centroid
        self.points = points
        self.centroid = self.calculateCentroid()
        return getDistance(old_centroid, self.centroid)
    def calculateCentroid(self):
        reduce_coord = lambda i:reduce(lambda x,p : x + p.coords[i],self.points,0.0)    
        centroid_coords = [reduce_coord(i)/len(self.points) for i in range(self.n)] 
        return Point(centroid_coords)

def getDistance(a, b):
    if a.n != b.n: raise Exception("ILLEGAL: non comparable points")
    ret = reduce(lambda x,y: x + pow((a.coords[y]-b.coords[y]), 2),range(a.n),0.0)
    return math.sqrt(ret)

def kmeans(points, k, cutoff):
    initial = random.sample(points, k)
    clusters = [Cluster([p]) for p in initial]
    while True:
        lists = [ [] for c in clusters]
        for p in points:
            smallest_distance = getDistance(p,clusters[0].centroid)
            index = 0
            for i in range(len(clusters[1:])):
                distance = getDistance(p, clusters[i+1].centroid)
                if distance < smallest_distance:
                    smallest_distance = distance
                    index = i+1
            lists[index].append(p)
        biggest_shift = 0.0
        for i in range(len(clusters)):
            shift = clusters[i].update(lists[i])
            biggest_shift = max(biggest_shift, shift)
        if biggest_shift < cutoff: 
            break
    return clusters
