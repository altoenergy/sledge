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
action = util.get_str_input("action (*) : ", "*")
remote = util.get_bool_input("remote (False) : ", False)
debug = util.get_bool_input("debug (False) : ", False)
logging.basicConfig(level = logging.DEBUG if debug else logging.INFO)

i_ = range(iFrom, iTo)
for i in i_:
    batch = "%s/%s" % (root, i)
    logging.info("running %s", batch)
    if (action == "*"):
        batcher.run(batch, remote)
    elif (action == "train"):
        batcher.train(batch, remote)
    elif (action == "validate"):
        batcher.validate(batch, remote)
    elif (action == "test"):
        batcher.test(batch, remote)
    elif (action == "report"):
        batcher.report(batch, remote)
    else:
        print "action %s unknown" % action

