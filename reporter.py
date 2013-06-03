import sys
sys.dont_write_bytecode = True
import logging
import numpy as np
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w

def report(batch, params, remote, debug):
    logging.info("--------------")
    
    result = {'success' : False, 'error' : 'none'}

    try:
        numEpisodes = params['episodes']['num']
        
        testParams = params['test']
        objective = testParams['objective']
        
        SBlend_ = []
        for i in range(numEpisodes):
            testResult = cache.get("batch/%s/test/%s" % (batch, i), remote)
            SBlend = None
            success = testResult['success']
            if success:
                SBlend_.append(testResult['SBlend'])

        SBlend_ = np.array(SBlend_)
        SBlendMean = np.mean(SBlend_)
        SBlendMin = np.min(SBlend_)
        SBlendMax = np.max(SBlend_)
            
        logging.info("SBlendMean : %s" % SBlendMean)
        logging.info("SBlendMin : %s" % SBlendMin)
        logging.info("SBlendMax : %s" % SBlendMax)
        
        result = {'success' : True, 'error' : 'none', 'SBlendMean' : SBlendMean, 'SBlendMin' : SBlendMin, 'SBlendMax' : SBlendMax}
        if (debug):
            result.update({'SBlend_' : list(SBlend_)})        
    except (KeyboardInterrupt):
        raise
    except Exception:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("batch/%s/report" % batch, result, remote)
    logging.info("--------------")
    return result