import sys
sys.dont_write_bytecode = True
import logging
import itertools as it
import pprint as pp
import cache
import cloud
import util
import batcher

root = util.get_str_input("batch (bulk) : ", "bulk")
iFrom = util.get_int_input("iFrom (0) : ", 0)
iTo = util.get_int_input("iTo (1) : ", 1)
key = util.get_str_input("key (report) : ", "report")
remote = util.get_bool_input("remote (True) : ", True)
debug = util.get_bool_input("debug (False) : ", False)
logging.basicConfig(level = logging.DEBUG if debug else logging.INFO)

i_ = range(iFrom, iTo)
for i in i_:
    print i
    try:
        batch = "%s/%s" % (root, i)
        obj = cache.get("%s/%s" % (batch, key), remote)
        pp.pprint(obj)
    except Exception:
        print sys.exc_info()
