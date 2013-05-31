import sys
sys.dont_write_bytecode = True
import logging
import numpy as np
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w

def report(batch, params, remote):
    logging.info("--------------")
    
    result = {'success' : False, 'error' : None}

    try:
        episodesParams = params['episodes']
        episodes = epi.build_episodes(episodesParams)
        
        testParams = params['test']
        objective = testParams['objective']
        
        SMean_ = []
        numEpisodes = episodes['num']
        SMeanTotal = 0
        for i in range(numEpisodes):
            testResult = cache.get("batch/%s/test/%s" % (batch, i), remote)
            SMean = None
            success = testResult['success']
            if success:
                SMean = testResult['SMean']
                
            if (SMean is not None):
                SMean_.append(SMean)
            else:
                SMean_.append(0)
                
        SMean_ = np.array(SMean_)
        SMeanMean = np.mean(SMean_)
        SMeanMin = np.min(SMean_)
        SMeanMax = np.max(SMean_)
            
        logging.info("SMeanMean : %s" % SMeanMean)
        logging.info("SMeanMin : %s" % SMeanMin)
        logging.info("SMeanMax : %s" % SMeanMax)
        result['success'] = True
        result['SMean_'] = list(SMean_)
        result['SMeanMean'] = SMeanMean
        result['SMeanMin'] = SMeanMin
        result['SMeanMax'] = SMeanMax
        
    except (KeyboardInterrupt):
        raise
    except Exception:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("batch/%s/report" % batch, result, remote)
    logging.info("--------------")
    return result