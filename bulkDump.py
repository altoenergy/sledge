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
xpath = util.get_str_input("xpath () : ", "")
remote = util.get_bool_input("remote (True) : ", True)
debug = util.get_bool_input("debug (False) : ", False)
logging.basicConfig(level = logging.DEBUG if debug else logging.INFO)

i_ = range(iFrom, iTo)
print "episode, trainRatio, alpha, threshold, value"
for i in i_:
    try:
        batch = "%s/%s" % (root, i)
        params = cache.get("%s/params" % batch, remote)
        trainRatio = params['episodes']['trainRatio']
        alpha = params['train']['alpha']
        threshold = params['train']['threshold']
        obj = cache.get("%s/%s" % (batch, key), remote)
        obj = cache.xpath(obj, xpath)
        print "%s, %s, %s, %s, %s" % (i, trainRatio, alpha, threshold, pp.pformat(obj))
    except Exception:
        print sys.exc_info()
