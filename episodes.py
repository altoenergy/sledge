import sys
sys.dont_write_bytecode = True
import json
import numpy as np
import date

def build_episodes(episodesParams):
    fromDt = date.from_yyyymmdd(episodesParams['fromDate'])
    toDt = date.from_yyyymmdd(episodesParams['toDate'])
    testDays = episodesParams['testDays']
    validateRatio = episodesParams['validateRatio']
    trainRatio = episodesParams['trainRatio']

    validateDays = testDays * validateRatio
    trainDays = testDays * trainRatio
    episodeDays = trainDays + validateDays + testDays
    
    diffDays = date.days_between(fromDt, toDt)
    numEpisodes = int(diffDays / float(testDays))
    subArrays = np.array_split(np.array(range(diffDays)), numEpisodes)
    episodeFrom_ = [int(subArray[0]) for subArray in subArrays[:-(trainRatio + validateRatio)]]
    
    trainFrom_ = [date.add_days(fromDt, episodeFrom) for episodeFrom in episodeFrom_]
    trainTo_ = [date.add_days(fromDt, episodeFrom + trainDays) for episodeFrom in episodeFrom_]
    validateFrom_ = [date.add_days(fromDt, episodeFrom + trainDays + 1) for episodeFrom in episodeFrom_]
    validateTo_ = [date.add_days(fromDt, episodeFrom + trainDays + validateDays) for episodeFrom in episodeFrom_]
    testFrom_ = [date.add_days(fromDt, episodeFrom + trainDays + validateDays + 1) for episodeFrom in episodeFrom_]
    testTo_ = [date.add_days(fromDt, episodeFrom + trainDays + validateDays + testDays) for episodeFrom in episodeFrom_]
    trainFromTo_ = zip(trainFrom_, trainTo_)
    validateFromTo_ = zip(validateFrom_, validateTo_)
    testFromTo_ = zip(testFrom_, testTo_)
    episodes = {'fromDate' : fromDt, 'toDate' : toDt, 'num' : len(episodeFrom_), 'train' : trainFromTo_, 'validate' : validateFromTo_, 'test' : testFromTo_}
    return episodes
