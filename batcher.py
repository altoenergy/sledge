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

def apply_shift(params, target, amount):
    if (target == "testDays"):
        params['episodes']['testDays'] = amount
    elif (target == "trainRatio"):
        params['episodes']['trainRatio'] = amount
    elif (target == "validateRatio"):
        params['episodes']['validateRatio'] = amount
    elif (target == "alpha"):
        params['train']['alpha'] = amount
    elif (target == "threshold"):
        params['train']['threshold'] = amount
        params['validate']['threshold'] = amount
    else:
        raise InputError("Shift target %s unknown" % target)

def expand_shifts(study, portfolio, params):
    shiftParams = params.get('shift')
    shifts = {'count' : 0, 'target_' : [], 'batch_' : [], 'amount__' : []}
    if (shiftParams):
        shifts['target_'] = shiftParams.keys()
        amount__ = list(it.product(*(shiftParams.values())))
        shifts['amount__'] = amount__
        shifts['count'] = len(amount__)
        shifts['batch_'] = ["%s-%s/%s" % (study, portfolio, i) for i in range(len(amount__))]
    return shifts

def prepare(study, portfolio, remote):
    origParams = util.load_json_file("study/%s.json" % study)
    origParams['portfolioKey'] = "portfolio/%s" % portfolio
    origParams['shift'] = expand_shifts(study, portfolio, origParams)
    
    baseParams = copy.deepcopy(origParams)
    baseParams['episodes'].update(epi.build_episodes(baseParams['episodes']))

    shifts = baseParams['shift']    
    logging.info("Caching %s-%s/base" % (study, portfolio))
    cache.put("batch/%s-%s/base/params" % (study, portfolio), baseParams, remote)
    target_ = shifts['target_']
    for batch, amount_ in zip(shifts['batch_'], shifts['amount__']):
        params = copy.deepcopy(origParams)
        for target, amount in zip(target_, amount_):
            apply_shift(params, target, amount)
        del params['shift']
        params['episodes'].update(epi.build_episodes(params['episodes']))
        logging.info("Caching %s" % batch)
        cache.put("batch/%s/params" % batch, params, remote)

def interpret_batches(study, portfolio, batch, remote):
    params = cache.get("batch/%s-%s/base/params" % (study, portfolio), remote)
    base = "%s-%s/base" % (study, portfolio)
    shifts = params['shift']['batch_']
    if (batch == "base"):
        return [base]
    elif (batch == "*"):
        return [base] + shifts
    else:
        batch_ = util.parse_number_list(batch)
        return [shifts[batch] for batch in batch_]

def dump(batch, remote, key, xpath, clipboard):
    cl = tk.Tk() if clipboard else None
    elem = util.xpath_elem(cache.get("batch/%s/%s" % (batch, key), remote), xpath)
    outStr = elem if xpath == "excel" else pp.pformat(elem)
    print outStr
    if clipboard:
        cl.clipboard_append(outStr)

def dump_old(study, portfolio, shift, remote, key, xpath, clipboard):
    cl = tk.Tk() if clipboard else None
    params = cache.get("batch/%s-%s/params" % (study, portfolio), remote)
    if shift:
        shifts = params['shift']
        outStr = "name," + ",".join(shifts['target_']) +",value"
        print outStr
        if clipboard:
            cl.clipboard_append("%s\n" % outStr)
        for batch, amount_ in zip(shifts['batch_'], shifts['amount__']):
            elem = util.xpath_elem(cache.get("batch/%s/%s" % (batch, key), remote), xpath)
            outStr = batch + "," + ",".join(map(str, amount_)) + "," + pp.pformat(elem)
            print outStr
            if clipboard:
                cl.clipboard_append("%s\n" % outStr)
    else:
        elem = util.xpath_elem(cache.get("batch/%s-%s/%s" % (study, portfolio, key), remote), xpath)
        outStr = elem if xpath == "excel" else pp.pformat(elem)
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
