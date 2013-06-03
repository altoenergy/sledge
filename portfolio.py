import urllib
import math
import csv
import json
import numpy as np
import util

class Feature:
    def __init__(self, key, normalize, fromDate, toDate):
        path = util.featurePath("%s.feature" % key)
        self.date_, self.value_ = np.loadtxt(open(path, 'r'), delimiter = ',', unpack = True)
        self.date_ = self.date_.astype(np.int)
        self.range_dates(fromDate, toDate)
        if (normalize):
            st = np.std(self.value_)
            m = np.mean(self.value_)
            self.value_ = (self.value_ - m) / st
        
    @staticmethod
    def common_dates(feature_):
        date__ = [set(feature.date_) for feature in feature_]
        commonDate_ = list(set.intersection(*date__))
        commonDate_.sort()
        return commonDate_

    def filter_dates(self, filterDate_):
        aDict = dict(zip(self.date_, self.value_))
        self.date_, self.value_ = zip(*[(date, aDict[date]) for date in filterDate_])

    def range_dates(self, fromDate, toDate):
        aDict = dict(zip(self.date_, self.value_))
        rangeDate_ = filter(lambda d: (d >= fromDate and d <= toDate), self.date_)
        self.date_, self.value_ = zip(*[(date, aDict[date]) for date in rangeDate_])
    
class Portfolio:
    def __init__(self, portfolio):
        fromDate = portfolio['fromDate']
        toDate = portfolio['toDate']
        normalize = portfolio['normalize']
        elements = portfolio['elements']
        self.tradable_ = [Feature(element['tradable'], False, fromDate, toDate) for element in elements]
        self.observable__ = [[Feature(observable, normalize, fromDate, toDate) for observable in element['observables']] for element in elements]
        self.c_ = np.array([element['cost'] for element in elements], float)
        self.iMax = len(self.c_)
        self.jLen_ = np.array([len(observable_) + 2 for observable_ in self.observable__])
        self.jLen = np.sum(self.jLen_)

        jTo_ = np.cumsum(self.jLen_)
        jFrom_ = np.roll(jTo_, 1)
        jFrom_[0] = 0
        self.jFromTo_ = zip(jFrom_, jTo_)
        
        feature_ = self.tradable_ + [item for sublist in self.observable__ for item in sublist]
        commonDate_ = Feature.common_dates(feature_)
        for feature in feature_:
            feature.filter_dates(commonDate_)
        self.date_Orig = commonDate_
            
        price__ = np.swapaxes(np.array([tradable.value_ for tradable in self.tradable_], float), 0, 1)
        self.r__Orig = price__ - np.roll(price__, 1, 0)
        self.r__Orig[0] = 0
        self.tMaxOrig = len(self.r__Orig)
        self.observation__Orig = np.array([np.concatenate([np.array([1] + [observable.value_[i] for observable in observable_] + [0]) for observable_ in self.observable__]) for i in range(self.tMaxOrig)])
        self.x___Orig = np.array([self.split(self.observation__Orig[t]) for t in range(self.tMaxOrig)]) # (date x asset x feature)

    def instantiate(self, fromDate, toDate):
        npDate_Orig = np.array(self.date_Orig)
        fromIdx = (np.abs(npDate_Orig - fromDate)).argmin()
        toIdx = (np.abs(npDate_Orig - toDate)).argmin() + 1
        self.date_ = self.date_Orig[fromIdx:toIdx]
        self.r__ = self.r__Orig[fromIdx:toIdx]
        self.tMax = len(self.r__)
        self.observation__ = self.observation__Orig[fromIdx:toIdx]
        self.x___ = self.x___Orig[fromIdx:toIdx]
        
    def split(self, X_):
        x__ = [X_[jFrom:jTo] for (jFrom, jTo) in self.jFromTo_]
        return x__
    
