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

def expand_shifts(study, params):
    shiftParams = params.get('shift')
    shifts = {'count' : 0, 'target_' : [], 'name_' : [], 'amount__' : []}
    if (shiftParams):
        shifts['target_'] = shiftParams.keys()
        amount__ = list(it.product(*(shiftParams.values())))
        shifts['amount__'] = amount__
        shifts['count'] = len(amount__)
        shifts['name_'] = ["%s/%s" % (study, i) for i in range(len(amount__))]
    return shifts

def create_batches(portfolio, study, remote):
    origParams = util.load_json_file("study/%s.json" % study)
    origParams['portfolioKey'] = "portfolio/%s" % portfolio
    origParams['shift'] = expand_shifts(study, origParams)
    
    baseParams = copy.deepcopy(origParams)
    baseParams['episodes'] = epi.build_episodes(baseParams['episodes'])

    shifts = baseParams['shift']    
    logging.info("Caching %s" % study)
    cache.put("batch/%s/params" % study, baseParams, remote)
    target_ = shifts['target_']
    for name, amount_ in zip(shifts['name_'], shifts['amount__']):
        params = copy.deepcopy(origParams)
        for target, amount in zip(target_, amount_):
            apply_shift(params, target, amount)
        del params['shift']
        params['episodes'] = epi.build_episodes(params['episodes'])
        logging.info("Caching %s" % name)
        cache.put("batch/%s/params" % name, params, remote)
        
def get_batch_names(study, shift, remote):        
    if shift:
        params = cache.get("batch/%s/params" % study, remote)
        return params['shift']['name_']
    else:
        return [study]

def act_study(action, study, shift, remote, debug):
    if (action == "train"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            train_batch(batch, remote, debug)
    elif (action == "validate"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            validate_batch(batch, remote, debug)
    elif (action == "test"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            test_batch(batch, remote, debug)
    elif (action == "report"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            report_batch(batch, remote, debug)
    elif (action == "*"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            run_batch(batch, remote, debug)
    elif (action == "track"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            track_batch(batch, remote, debug)
    elif (action == "review"):
        for batch in get_batch_names(study, shift, remote):
            if shift:
                print batch
            review_batch(batch, remote, debug)
    else:
        raise InputError("Action %s unknown" % action)

def dump_study(study, shift, remote, key, xpath, clipboard):
    cl = tk.Tk() if clipboard else None
    params = cache.get("batch/%s/params" % study, remote)
    if shift:
        shifts = params['shift']
        outStr = "name," + ",".join(shifts['target_']) +",value"
        print outStr
        if clipboard:
            cl.clipboard_append("%s\n" % outStr)
        for name, amount_ in zip(shifts['name_'], shifts['amount__']):
            elem = util.xpath_elem(cache.get("batch/%s/%s" % (name, key), remote), xpath)
            outStr = name + "," + ",".join(map(str, amount_)) + "," + pp.pformat(elem)
            print outStr
            if clipboard:
                cl.clipboard_append("%s\n" % outStr)
    else:
        elem = util.xpath_elem(cache.get("batch/%s/%s" % (study, key), remote), xpath)
        outStr = elem if xpath == "excel" else pp.pformat(elem)
        print outStr
        if clipboard:
            cl.clipboard_append(outStr)

def run_batch(batch, remote, debug):
    k_Train = train_batch(batch, remote, debug)
    k_Validate = validate_batch(batch, remote, debug, dependency = k_Train)
    k_Test = test_batch(batch, remote, debug, dependency = k_Validate)
    kReport = report_batch(batch, remote, debug, dependency = k_Test)
    cache.put("batch/%s/jobs" % batch, {'train' : list(k_Train), 'validate' : list(k_Validate), 'test' : list(k_Test), 'report' : kReport}, remote)
        
def train_batch(batch, remote, debug, dependency = []):
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

def validate_batch(batch, remote, debug, dependency = []):
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

def test_batch(batch, remote, debug, dependency = []):
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
        
def report_batch(batch, remote, debug, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    logging.info("running reporter instance")
    if (remote):
        k = cloud.call(reporter.report, batch, params, remote, debug, _label = "%s/report" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k %s" % k)
        return k
    else:
        result = reporter.report(batch, params, remote, debug)
        return result

def track_batch(batch, remote, debug):
    if (not remote):
        logging.info("cannot track locally")
        return
    jobs = cache.get("batch/%s/jobs" % batch, remote)
    k_ = jobs['train'] + jobs['validate'] + jobs['test'] + [jobs['report']]
    
    status_ = cloud.status(k_)
    count = co.Counter(status_)
    print count

def review_batch(batch, remote, debug):
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
