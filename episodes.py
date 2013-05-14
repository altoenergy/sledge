import sys
sys.dont_write_bytecode = True
import json
import numpy as np
import datetime as dt

def build_episodes(episodesParams):
    fromDate = episodesParams['fromDate']
    toDate = episodesParams['toDate']
    testDays = episodesParams['testDays']
    validateRatio = episodesParams['validateRatio']
    trainRatio = episodesParams['trainRatio']
    
    validateDays = testDays * validateRatio
    trainDays = testDays * trainRatio
    episodeDays = trainDays + validateDays + testDays
    
    dFrom = dt.datetime.strptime(str(fromDate),'%Y%m%d')
    dTo = dt.datetime.strptime(str(toDate),'%Y%m%d')
    diff = dTo - dFrom
    diffDays = diff.days
    numEpisodes = int(diffDays / float(testDays))
    subArrays = np.array_split(np.array(range(diffDays)), numEpisodes)
    subArrays = subArrays[:-(trainRatio + validateRatio)]
    trainFromTos = []
    validateFromTos = []
    testFromTos = []
    for subArray in subArrays:
        trainFrom = dFrom + dt.timedelta(days = int(subArray[0]))
        trainTo = dFrom + dt.timedelta(days = int(subArray[0]) + trainDays)
        validateFrom = dFrom + dt.timedelta(days = int(subArray[0]) + trainDays + 1)
        validateTo = dFrom + dt.timedelta(days = int(subArray[0]) + trainDays + validateDays)
        testFrom = dFrom + dt.timedelta(days = int(subArray[0]) + trainDays + validateDays + 1)
        testTo = dFrom + dt.timedelta(days = int(subArray[0]) + trainDays + validateDays + testDays)
        trainFrom = int(trainFrom.strftime('%Y%m%d'))
        trainTo = int(trainTo.strftime('%Y%m%d'))
        validateFrom = int(validateFrom.strftime('%Y%m%d'))
        validateTo = int(validateTo.strftime('%Y%m%d'))
        testFrom = int(testFrom.strftime('%Y%m%d'))
        testTo = int(testTo.strftime('%Y%m%d'))
        trainFromTos.append((trainFrom, trainTo))
        validateFromTos.append((validateFrom, validateTo))
        testFromTos.append((testFrom, testTo))
    episodes = {'num' : len(subArrays), 'train' : trainFromTos, 'validate' : validateFromTos, 'test' : testFromTos}
    return episodes
