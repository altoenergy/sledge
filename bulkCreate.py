import sys
sys.dont_write_bytecode = True
import logging
import util
import cache
import batcher

root = util.get_str_input("root (bulk) : ", "bulk")
remote = util.get_bool_input("remote (False) : ", False)
portfolioName = util.get_str_input("portfolio (default) : ", "default")
clear = util.get_bool_input("clear (False) : ", False)

debug = False
logging.basicConfig(level = logging.DEBUG if debug else logging.INFO)

trainRatio_ = [3, 5, 9]
alpha_ = [0.01, 0.02, 0.05, 0.1]
threshold_ = [0.10, 0.15, 0.25]

i = 0
if (clear):
    logging.info("clearing %s locally" % root)
    cache.clear(root, False)
    if (remote):
        logging.info("clearing %s remotely" % root)
        cache.clear(root, True)
        
for trainRatio in trainRatio_:
    for alpha in alpha_:
        for threshold in threshold_:
            batch = "%s/%s" % (root, i)
            episodesParams = {
                "fromDate" : 19851118,
                "toDate" : 20130404,
                "testDays" : 100,
                "validateRatio" : 1,
                "trainRatio" : trainRatio
            }
            trainParams = {
                "iters" : 5,
                "draws" : 20,
                "epochs" : 20,
                "alpha" : alpha,
                "objective" : "sharp",
                "threshold" : threshold
            }
            validateParams = {
                "objective" : "sharp",
                "threshold" : threshold
            }
            testParams = {
                "objective" : "sharp"
            }
            wParams = {
                "init" : "rand",
                "eval" : "exp",
                "dFdW" : "numeric"
            }
            params = {'portfolioKey' : "portfolio/%s" % portfolioName, 'episodes' : episodesParams, 'train' : trainParams,
                      'validate' : validateParams, 'test' : testParams, 'w' : wParams}
            batcher.create(batch, params, remote)
            i += 1
