import sys
sys.dont_write_bytecode = True
import logging
import util
import cache
import batcher

root = util.get_str_input("root (bulk) : ", "bulk")
remote = util.get_bool_input("remote (False) : ", False)
portfolioName = util.get_str_input("portfolio (default) : ", "default")

debug = False
logging.basicConfig(level = logging.DEBUG if debug else logging.INFO)

trainRatio_ = [1, 3, 5, 9]
alpha_ = [0.01, 0.05, 0.1]
threshold_ = [0.05, 0.15, 0.25, 0.4]

i = 0
for trainRatio in trainRatio_:
    for alpha in alpha_:
        for threshold in threshold_:
            batch = "%s/%s" % (root, i)
            episodesParams = {
                "fromDate" : 19851118,
                "toDate" : 19920922,
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
                "accumulate" : True,
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
