import sys
import logging
import itertools as it
import collections as co
import Tkinter as tk
import pprint as pp
import numpy as np
import copy
import cloud
import cache
import util
import episodes as epi
import portfolio as ptf
import objective as obj
import episodes as epi
import trainer
import validater
import tester
import reporter

def apply_search(params, target_, value_):
    for target, value in zip(target_, value_):
        if (value is None):
            continue
        if (target == "testDays"):
            params['episodes']['testDays'] = value
        elif (target == "trainRatio"):
            params['episodes']['trainRatio'] = value
        elif (target == "validateRatio"):
            params['episodes']['validateRatio'] = value
        elif (target == "alpha"):
            params['train']['alpha'] = value
        elif (target == "threshold"):
            params['train']['threshold'] = value
            params['validate']['threshold'] = value
        else:
            raise InputError("Search target %s unknown" % target)

def read_search(params, target_):
    value_ = []
    for target in target_:
        if (target == "testDays"):
            value_.append(params['episodes']['testDays'])
        elif (target == "trainRatio"):
            value_.append(params['episodes']['trainRatio'])
        elif (target == "validateRatio"):
            value_.append(params['episodes']['validateRatio'])
        elif (target == "alpha"):
            value_.append(params['train']['alpha'])
        elif (target == "threshold"):
            value_.append(params['train']['threshold'])
        else:
            raise InputError("Search target %s unknown" % target)
    return value_

def build_search(study, portfolio, params):
    searchParams = params.get('shift')
    batch_ = ["%s-%s/base" % (study, portfolio)]
    target_ = []
    value__ = [[None]]
    if (searchParams):
        target_ = searchParams.keys()
        combo__ = list(it.product(*(searchParams.values())))
        value__ = [tuple(read_search(params, target_))] + combo__
        batch_ += (["%s-%s/%s" % (study, portfolio, i) for i in range(len(combo__))])
    search = {'target_' : target_, 'value__' : value__, 'batch_' : batch_}
    return search

def prepare(study, portfolio, remote):
    studyParams = util.load_json_file("study/%s.json" % study)
    
    search = build_search(study, portfolio, studyParams)
    logging.info("Caching %s-%s/search" % (study, portfolio))
    cache.put("batch/%s-%s/search" % (study, portfolio), search, remote)

    batch_ = search['batch_']
    target_ = search['target_']
    value__ = search['value__']
    for batch, value_ in zip(batch_, value__):
        params = copy.deepcopy(studyParams)
        del params['shift']
        params['portfolioKey'] = "portfolio/%s" % portfolio
        apply_search(params, target_, value_)
        params['episodes'].update(epi.build_episodes(params['episodes']))
        logging.info("Caching %s" % batch)
        cache.put("batch/%s/params" % batch, params, remote)

def interpret_batches(study, portfolio, batchList, remote):
    search = cache.get("batch/%s-%s/search" % (study, portfolio), remote)
    batchName_ = search['batch_']
    if (batchList == "base"):
        return [batchName_[0]]
    elif (batchList == "*"):
        return batchName_
    else:
        batchNum_ = util.parse_number_list(batchList)
        return [batchName_[batchNum + 1] for batchNum in batchNum_]

def dump_key(search, batch, remote, key, xpath, showSearchValues):
    elem = util.xpath_elem(cache.get("batch/%s/%s" % (batch, key), remote), xpath)
    outStr = ""
    if (showSearchValues):
        i = search['batch_'].index(batch)
        value_ = search['value__'][i]
        outStr += batch + "," + ",".join(map(str, value_)) + ","
    else:
        outStr += batch + "\n"
    outStr += str(elem) if xpath == "excel" else pp.pformat(elem)
    return outStr

def dump_single(search, batch, remote, key, xpath, showSearchValues):
    if (key == "train/*" or key == "validate/*" or key == "test/*"):
        outStr = ""
        params = cache.get("batch/%s/params" % batch, remote)
        numEpisodes = params['episodes']['num']
        base = key[:key.find("/")]
        for i in range(numEpisodes):
            outStr += "\n%s/%s\n" % (base, i)
            outStr += dump_key(search, batch, remote, "%s/%s" % (base, i), xpath, showSearchValues)
        return outStr
    else:
        return dump_key(search, batch, remote, key, xpath, showSearchValues)
    
def dump_multiple(study, portfolio, batch_, remote, key, xpath, clipboard, showSearchValues):
    cl = tk.Tk() if clipboard else None
    outStr = ""
    search = cache.get("batch/%s-%s/search" % (study, portfolio), remote)
    if (showSearchValues):
        outStr += "batch," + ",".join(map(str, search['target_'])) + ",value\n"
    for batch in batch_:
        outStr += dump_single(search, batch, remote, key, xpath, showSearchValues)
        if (batch != batch_[-1]):
            outStr += "\n"
    print outStr
    if clipboard:
        cl.clipboard_append(outStr)

def run(batch, remote, debug):
    k_Train = train(batch, remote, debug)
    k_Validate = validate(batch, remote, debug, dependency = k_Train)
    k_Test = test(batch, remote, debug, dependency = k_Validate)
    kReport = report(batch, remote, debug, dependency = k_Test)
    cache.put("batch/%s/jobs" % batch, {'train' : list(k_Train), 'validate' : list(k_Validate), 'test' : list(k_Test), 'report' : kReport}, remote)
        
def train(batch, remote, debug, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    numEpisodes = params['episodes']['num']
    
    trainParams = params['train']
    numIters = trainParams['iters']
    
    ij_ = [(i, j) for i, j in it.product(range(numEpisodes), range(numIters))]
    f = lambda (i, j) : trainer.train(batch, params, i, j, remote, debug)
    
    logging.info("running %s train instances" % len(ij_))
    if (remote):
        k_ = cloud.map(f, ij_, _label = "%s/train" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        results = map(f, ij_)
        return results

def validate(batch, remote, debug, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    numEpisodes = params['episodes']['num']
    
    i_ = range(numEpisodes)
    f = lambda i : validater.validate(batch, params, i, remote, debug)
    
    logging.info("running %s validate instances" % len(i_))
    if (remote):
        k_ = cloud.map(f, i_, _label = "%s/validate" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        results = map(f, i_)
        return results

def test(batch, remote, debug, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    numEpisodes = params['episodes']['num']
    
    i_ = range(numEpisodes)
    f = lambda i : tester.test(batch, params, i, remote, debug)
    
    logging.info("running %s test instances" % len(i_))
    if (remote):
        k_ = cloud.map(f, i_, _label = "%s/test" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        results = map(f, i_)
        return results
        
def report(batch, remote, debug, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    logging.info("running reporter instance")
    if (remote):
        k = cloud.call(reporter.report, batch, params, remote, debug, _label = "%s/report" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k %s" % k)
        return k
    else:
        result = reporter.report(batch, params, remote, debug)
        return result

def track(batch, remote, debug):
    try:
        if (not remote):
            logging.info("cannot track locally")
            return
        jobs = cache.get("batch/%s/jobs" % batch, remote)
        k_ = jobs['train'] + jobs['validate'] + jobs['test'] + [jobs['report']]
        
        status_ = cloud.status(k_)
        count = co.Counter(status_)
        print count
    except:
        print "status failed"
        pass

def review(batch, remote, debug):
    if (not remote):
        logging.info("cannot review locally")
        return
    jobs = cache.get("batch/%s/jobs" % batch, remote)
    review_jobs("train", jobs['train'])
    review_jobs("validate", jobs['validate'])
    review_jobs("test", jobs['test'])
    review_jobs("report", [jobs['report']])
    
def review_jobs(label, jobs):
    info = cloud.info(jobs, ['runtime'])
    runtime = 0
    count = len(info)
    tMin = 50000
    tMax = 0
    for value in info.values():
        time = value['runtime']
        if (time < tMin):
            tMin = time
        if (time > tMax):
            tMax = time
        runtime += time
    mean = runtime / count
    print "%s : %s : %s : %s : %s" % (label, runtime, tMin, tMax, mean)
