import sys
sys.dont_write_bytecode = True
import logging
import util
import numpy as np

asset = util.get_str_input("asset (corn) : ", "corn")
numReturns = util.get_int_input("num returns (5) : ", 5)

path = util.featurePath("%s.spot.feature" % asset)
spotDate_, spotValue_ = np.loadtxt(open(path, 'r'), delimiter = ',', unpack = True)

pathOut = util.featurePath("%s.-spot.feature" % asset)
dateSpot_ = zip(spotDate_, -spotValue_)
np.savetxt(pathOut, dateSpot_, fmt=['%8i', '%s'], delimiter = ',')

for i in range(numReturns):
    date_ = spotDate_[i + 1:]
    return_ = (np.roll(spotValue_, i, 0) - np.roll(spotValue_, i + 1, 0))[i + 1:]
    pathOut = util.featurePath("%s.r%s.feature" % (asset, i))
    dateReturn_ = zip(date_, return_)
    np.savetxt(pathOut, dateReturn_, fmt=['%8i', '%s'], delimiter = ',')
