import sys
sys.dont_write_bytecode = True
import logging
import numpy as np
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w

def report(batch, remote):
    logging.info("--------------")
    
    result = {'success' : False, 'error' : None, 'SMeanMean' : None}

    try:
        params = cache.get("%s/params" % batch, remote)
        episodesParams = params['episodes']
        episodes = epi.build_episodes(episodesParams)
        
        numEpisodes = episodes['num']
        numSuccess = 0
        SMeanMean = 0
        for i in range(numEpisodes):
            testResult = cache.get("%s/test/%s" % (batch, i), remote)
            SMean = testResult['SMean']
            logging.info("S mean : %s" % SMean)            
            if (SMean is not None):
                SMeanMean += SMean
                numSuccess += 1
        SMeanMean /= numSuccess
        logging.info("S mean mean : %s" % SMeanMean)
        result['success'] = True
        result['SMeanMean'] = SMeanMean
        
    except (KeyboardInterrupt):
        raise
    except Exception:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("%s/report" % batch, result, remote)
    logging.info("--------------")
    return result