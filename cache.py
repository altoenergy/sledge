import sys
sys.dont_write_bytecode = True
import os
import threading
import shutil as sh
import logging
import pickle
import cloud

def get(key, remote):
    if remote:
        return pickle.loads(cloud.bucket.getf(key).read())
    else:
        return pickle.load(open("cache/%s" % key, 'r'))

def put(key, obj, remote):
    if remote:
        cloud.bucket.putf(pickle.dumps(obj), key)
    else:
        path = "cache/%s" % key
        dire = os.path.dirname(path)
        if not os.path.exists(dire):
            os.makedirs(dire)       
        pickle.dump(obj, open(path, 'w'))
        
def delete_prefix(prefix):
    num_threads = 10
    object_iterator = cloud.bucket.iterlist(prefix=prefix)
    iterator_lock = threading.Lock()

    def delete_file():
        try:
          while True:
              with iterator_lock:
                  obj_path = object_iterator.next()
              cloud.bucket.remove(obj_path)

        except StopIteration:
          pass

    remove_threads = []
    for _ in xrange(num_threads):
        remove_thread = threading.Thread(target=delete_file)
        remove_thread.start()
        remove_threads.append(remove_thread)

    for remove_thread in remove_threads:
        remove_thread.join()
        
def clear(prefix, remote):
    if (remote):
        k = cloud.call(delete_prefix, prefix)
        return cloud.result(k)
    else:
        path = "cache/%s" % prefix
        if (os.path.isdir(path)):
            sh.rmtree(path)
        elif (os.path.isfile(path)):
            os.remove(path)
