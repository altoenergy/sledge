import sys
import logging
import itertools as it
import pprint as pp
import collections as co
import Tkinter as tk
import numpy as np
import copy
import cloud
import cache
import util
import episodes as epi
import portfolio as ptf
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

def create_batches(study, remote):
    params = util.load_json_file("study/%s.json" % study)
    shifts = expand_shifts(study, params)
    params['shift'] = shifts
    
    logging.info("Caching %s" % study)
    cache.put("batch/%s/params" % study, params, remote)
    target_ = shifts['target_']
    for name, amount_ in zip(shifts['name_'], shifts['amount__']):
        for target, amount in zip(target_, amount_):
            apply_shift(params, target, amount)
        logging.info("Caching %s" % name)
        cache.put("batch/%s/params" % name, params, remote)
        
def get_batch_names(study, shift, remote):        
    if shift:
        params = cache.get("batch/%s/params" % study, remote)
        return params['shift']['name_']
    else:
        return [study]

def act(action, study, shift, remote):
    if (action == "create"):
        create_batches(study, remote)
    elif (action == "train"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            train(batch, remote)
    elif (action == "validate"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            validate(batch, remote)
    elif (action == "test"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            test(batch, remote)
    elif (action == "report"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            report(batch, remote)
    elif (action == "*"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            run(batch, remote)
    elif (action == "track"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            track(batch, remote)
    elif (action == "review"):
        for batch in get_batch_names(study, shift, remote):
            print batch
            review(batch, remote)
    else:
        raise InputError("Action %s unknown" % action)

def dump(study, shift, remote, key, xpath, clipboard):
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
        outStr = pp.pformat(elem)
        print outStr
        if clipboard:
            cl.clipboard_append(outStr)

def run(batch, remote):
    k_Train = train(batch, remote)
    k_Validate = validate(batch, remote, dependency = k_Train)
    k_Test = test(batch, remote, dependency = k_Validate)
    kReport = report(batch, remote, dependency = k_Test)
    cache.put("batch/%s/jobs" % batch, {'train' : list(k_Train), 'validate' : list(k_Validate), 'test' : list(k_Test), 'report' : kReport}, remote)
        
def train(batch, remote, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    episodes = epi.build_episodes(params['episodes'])
    numEpisodes = episodes['num']
    
    trainParams = params['train']
    numIters = trainParams['iters']
    
    ij_ = [(i, j) for i, j in it.product(range(numEpisodes), range(numIters))]
    f = lambda (i, j) : trainer.train(batch, params, i, j, remote)
    
    logging.info("running %s train instances" % len(ij_))
    if (remote):
        k_ = cloud.map(f, ij_, _label = "%s/train" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        results = map(f, ij_)
        return results

def validate(batch, remote, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    episodes = epi.build_episodes(params['episodes'])
    numEpisodes = episodes['num']
    
    i_ = range(numEpisodes)
    f = lambda i : validater.validate(batch, params, i, remote)
    
    logging.info("running %s validate instances" % len(i_))
    if (remote):
        k_ = cloud.map(f, i_, _label = "%s/validate" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        results = map(f, i_)
        return results

def test(batch, remote, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    episodes = epi.build_episodes(params['episodes'])
    numEpisodes = episodes['num']
    
    i_ = range(numEpisodes)
    f = lambda i : tester.test(batch, params, i, remote)
    
    logging.info("running %s test instances" % len(i_))
    if (remote):
        k_ = cloud.map(f, i_, _label = "%s/test" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        results = map(f, i_)
        return results
        
def report(batch, remote, dependency = []):
    params = cache.get("batch/%s/params" % batch, remote)
    logging.info("running reporter instance")
    if (remote):
        k = cloud.call(reporter.report, batch, params, remote, _label = "%s/report" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k %s" % k)
        return k
    else:
        result = reporter.report(batch, params, remote)
        return result
    
def track(batch, remote):
    if (not remote):
        logging.info("cannot track locally")
        return
    jobs = cache.get("batch/%s/jobs" % batch, remote)
    k_ = jobs['train'] + jobs['validate'] + jobs['test'] + [jobs['report']]
    
    status_ = cloud.status(k_)
    count = co.Counter(status_)
    print count

def review(batch, remote):
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
