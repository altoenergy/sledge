import sys
sys.dont_write_bytecode = True
import logging
import itertools as it
import collections as co
import cache
import cloud
import util
import episodes as epi
import portfolio as ptf
import episodes as epi
import trainer
import validater
import tester
import reporter

def run(batch, clear, remote):
    if (clear):
        logging.info("clearing %s train, validate, test" % batch)
        cache.clear("%s/train" % batch, remote)
        cache.clear("%s/validate" % batch, remote)
        cache.clear("%s/test" % batch, remote)
    k_Train = train(batch, remote)
    k_Validate = validate(batch, remote, dependency = k_Train)
    k_Test = test(batch, remote, dependency = k_Validate)
    kReport = report(batch, remote, dependency = k_Test)
    cache.put("%s/jobs" % batch, {'train' : list(k_Train), 'validate' : list(k_Validate), 'test' : list(k_Test), 'report' : kReport}, remote)
    
def create(batch, params, remote):
    logging.info("caching %s locally" % batch)
    cache.clear("%s" % batch, False)
    cache.put("%s/params" % batch, params, False)
    if (remote):
        logging.info("caching %s remotely" % batch)
        cache.clear("%s" % batch, True)
        cache.put("%s/params" % batch, params, True)

def train(batch, remote, dependency = []):
    params = cache.get("%s/params" % batch, False)
    episodes = epi.build_episodes(params['episodes'])
    numEpisodes = episodes['num']
    
    trainParams = params['train']
    numIters = trainParams['iters']
    
    ij_ = [(i, j) for i, j in it.product(range(numEpisodes), range(numIters))]
    f = lambda (i, j) : trainer.train(batch, i, j, remote)
    
    if (remote):
        logging.info("remoting %s train instances" % len(ij_))
        k_ = cloud.map(f, ij_, _label = "%s/train" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        logging.info("running %s train instances" % len(ij_))
        results = map(f, ij_)
        return results

def validate(batch, remote, dependency = []):
    params = cache.get("%s/params" % batch, False)
    episodes = epi.build_episodes(params['episodes'])
    numEpisodes = episodes['num']
    
    i_ = range(numEpisodes)
    f = lambda i : validater.validate(batch, i, remote)
    
    if (remote):
        logging.info("remoting %s validate instances" % len(i_))
        k_ = cloud.map(f, i_, _label = "%s/validate" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        logging.info("running %s validate instances" % len(i_))
        results = map(f, i_)
        return results

def test(batch, remote, dependency = []):
    params = cache.get("%s/params" % batch, False)
    episodes = epi.build_episodes(params['episodes'])
    numEpisodes = episodes['num']
    
    i_ = range(numEpisodes)
    f = lambda i : tester.test(batch, i, remote)
    
    if (remote):
        logging.info("remoting %s test instances" % len(i_))
        k_ = cloud.map(f, i_, _label = "%s/test" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k_ %s" % k_)
        return k_
    else:
        logging.info("running %s test instances" % len(i_))
        results = map(f, i_)
        return results
        
def report(batch, remote, dependency = []):
    if (remote):
        logging.info("remoting reporter instance")
        k = cloud.call(reporter.report, batch, remote, _label = "%s/report" % batch, _depends_on = dependency, _type = 'c1', _max_runtime = 30)
        logging.info("k %s" % k)
        return k
    else:
        logging.info("running reporter instance")
        result = reporter.report(batch, remote)
        return result
    
def track(batch, remote):
    if (not remote):
        logging.info("cannot track locally")
        return
    jobs = cache.get("%s/jobs" % batch, True)
    k_ = jobs['train'] + jobs['validate'] + jobs['test'] + [jobs['report']]
    
    status_ = cloud.status(k_)
    count = co.Counter(status_)
    print count

def review(batch, remote):
    if (not remote):
        logging.info("cannot review locally")
        return
    jobs = cache.get("%s/jobs" % batch, True)
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
