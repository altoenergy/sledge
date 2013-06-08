import urllib
import math
import csv
import json
import numpy as np
import util

class Feature:
    def __init__(self, key, fromDate, toDate):
        path = util.featurePath("%s.feature" % key)
        self.date_, self.value_ = np.loadtxt(open(path, 'r'), delimiter = ',', unpack = True)
        self.date_ = self.date_.astype(np.int)
        self.range_dates(fromDate, toDate)
        
    @staticmethod
    def common_dates(feature_):
        date__ = [set(feature.date_) for feature in feature_]
        commonDate_ = list(set.intersection(*date__))
        commonDate_.sort()
        return commonDate_

    def filter_dates(self, filter_):
        aDict = dict(zip(self.date_, self.value_))
        self.date_, self.value_ = zip(*[(date, aDict[date]) for date in filter_])

    def range_dates(self, fromDate, toDate):
        aDict = dict(zip(self.date_, self.value_))
        rangeDate_ = filter(lambda d: (d >= fromDate and d <= toDate), self.date_)
        self.date_, self.value_ = zip(*[(date, aDict[date]) for date in rangeDate_])
    
class Portfolio:
    def __init__(self, portfolio):
        fromDate = portfolio['fromDate']
        toDate = portfolio['toDate']
        elements = portfolio['elements']
        self.iMax = len(elements)
        tradable_ = [Feature(element['tradable'], fromDate, toDate) for element in elements]
        observable__ = [[Feature(observable, fromDate, toDate) for observable in element['observables']] for element in elements]
        self.c_ = np.array([element['cost'] for element in elements], float)
        self.jLen_ = np.array([len(observable_) + 2 for observable_ in observable__])
        self.jLen = np.sum(self.jLen_)

        jTo_ = np.cumsum(self.jLen_)
        jFrom_ = np.roll(jTo_, 1)
        jFrom_[0] = 0
        self.jFromTo_ = zip(jFrom_, jTo_)
        
        feature_ = tradable_ + [item for sublist in observable__ for item in sublist]
        commonDate_ = Feature.common_dates(feature_)
        for feature in feature_:
            feature.filter_dates(commonDate_)
        self.date_Orig = commonDate_
        
        self.observation__ = [[observable.value_ for observable in observable_] for observable_ in observable__]
            
        price__ = np.swapaxes(np.array([tradable.value_ for tradable in tradable_], float), 0, 1)
        self.r__Orig = price__ - np.roll(price__, 1, 0)
        self.r__Orig[0] = 0

    def instantiate(self, fromDate, toDate, normalize, nFromDate, nToDate):
        npDate_Orig = np.array(self.date_Orig)
        
        fromIdx = (np.abs(npDate_Orig - fromDate)).argmin()
        toIdx = (np.abs(npDate_Orig - toDate)).argmin() + 1
        tMax = toIdx - fromIdx
        
        nFromIdx = (np.abs(npDate_Orig - nFromDate)).argmin()
        nToIdx = (np.abs(npDate_Orig - nToDate)).argmin() + 1
            
        ones = np.ones([tMax])
        zeros = np.zeros([tMax])

        rows = []
        for i in range(self.iMax):
            rows.append(ones)
            for j in range(self.jLen_[i] - 2):
                value_ = self.observation__[i][j]
                nValue_ = value_[nFromIdx:nToIdx]
                m = np.mean(nValue_) if normalize else 0
                st = np.std(nValue_) if normalize else 1
                rows.append((value_[fromIdx:toIdx] - m) / st)
            rows.append(zeros)
        observation__ = np.swapaxes(np.array(rows), 0, 1)
        self.x___ = np.array([self.split(observation__[t]) for t in range(tMax)]) # (date x asset x feature)
        self.date_ = self.date_Orig[fromIdx:toIdx]
        self.r__ = self.r__Orig[fromIdx:toIdx]
        self.tMax = tMax
        
    def split(self, X_):
        x__ = [X_[jFrom:jTo] for (jFrom, jTo) in self.jFromTo_]
        return x__
    
