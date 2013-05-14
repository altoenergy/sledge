import sys
sys.dont_write_bytecode = True
import logging
import numpy as np
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w

def test(batch, i, remote):
    logging.info("--------------")
    logging.info("episode %s" % i)
    
    result = {'success' : False, 'error' : None}
    
    try:
        params = cache.get("%s/params" % batch, remote)
        portfolio = cache.get(params['portfolioKey'], remote)
        episodesParams = params['episodes']
        episodes = epi.build_episodes(episodesParams)
        testParams = params['test']
        wParams = params['w']
        logging.debug("testParams : %s" % testParams)
        
        fromDate = episodes['test'][i][0]
        toDate = episodes['test'][i][1]
        logging.info("fromDate, toDate : %s, %s" % (fromDate, toDate))
        
        portfolio.instantiate(fromDate, toDate)
        
        objective = testParams['objective']
        
        validateResult = cache.get("%s/validate/%s" % (batch, i), remote)
        validateWinner_ = validateResult['winners']
        numValidateWinners = len(validateWinner_)
                
        logging.info("candidates : %s" % numValidateWinners)
        
        F__Total = np.zeros([portfolio.tMax, portfolio.iMax])
        S_ = []
        for validateWinner in validateWinner_:
            W_ = validateWinner['W_']
            F__ = w.run_W(portfolio, W_, wParams)
            S = obj.score(objective, portfolio, F__)
            logging.info("S : %s" % S)
            S_.append(S)
            F__Total += F__

        F__Mean = None
        SMean = None
        if (numValidateWinners > 0):
            F__Mean = F__Total / numValidateWinners
            SMean = obj.score(objective, portfolio, F__Mean)
            
        logging.info("S mean : %s" % SMean)
        
        result['F__Mean'] = F__Mean
        result['SMean'] = SMean        
        result['success'] = True
        result['S_'] = S_
    except (KeyboardInterrupt):
        raise
    except Exception:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("%s/test/%s" % (batch, i), result, remote)
    logging.info("--------------")
    return result

