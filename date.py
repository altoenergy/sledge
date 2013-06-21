import sys
import datetime

def from_yyyymmdd(yyyymmdd):
    return datetime.datetime.strptime(str(yyyymmdd), '%Y%m%d')

def to_yyyymmdd(dt):    
    return int(datetime.datetime.strftime(dt, '%Y%m%d'))

def add_days(fromDt, numDays):
    return fromDt + datetime.timedelta(days = int(numDays))

def days_between(fromDt, toDt):
    return (toDt - fromDt).days

def nearest_index(dt_, dtTarget):
    return min(range(len(dt_)), key=lambda i: abs(days_between(dt_[i], dtTarget)))