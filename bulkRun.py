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
remote = util.get_bool_input("remote (False) : ", False)
debug = util.get_bool_input("debug (False) : ", False)
logging.basicConfig(level = logging.DEBUG if debug else logging.INFO)

clear = util.get_bool_input("clear (False) : ", False)

i_ = range(iFrom, iTo)
for i in i_:
    batch = "%s/%s" % (root, i)
    logging.info("running %s", batch)
    batcher.run(batch, clear, remote)
