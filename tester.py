import sys
sys.dont_write_bytecode = True
import logging
import numpy as np
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w
import util

def test(batch, params, i, remote, debug):
    logging.info("--------------")
    logging.info("episode %s" % i)
    
    result = {'success' : False, 'error' : 'none'}
    
    try:
        portfolio = cache.get(params['portfolioKey'], remote)
        episodes = params['episodes']
        testParams = params['test']
        wParams = params['w']
        logging.debug("testParams : %s" % testParams)
        
        fromDate = episodes['test'][i][0]
        toDate = episodes['test'][i][1]
        logging.info("fromDate, toDate : %s, %s" % (fromDate, toDate))
        
        nFromDate = episodes['train'][i][0]
        nToDate = episodes['train'][i][1]
        portfolio.instantiate(fromDate, toDate, True, nFromDate, nToDate)
        
        objective = testParams['objective']
        
        validateResult = cache.get("batch/%s/validate/%s" % (batch, i), remote)
        validateWinner_ = validateResult['winner_']
        numValidateWinners = len(validateWinner_)
                
        logging.info("candidates : %s" % numValidateWinners)
        
        F__Total = np.zeros([portfolio.tMax, portfolio.iMax])
        S_ = []
        provenance_ = []
        for validateWinner in validateWinner_:
            W_ = validateWinner['W_']
            provenance = validateWinner['provenance']
            F__ = w.run_W(portfolio, W_, wParams)
            S = obj.score(objective, portfolio, F__)
            logging.info("S : %s" % S)
            S_.append(S)
            provenance_.append(provenance)
            F__Total += F__

        F__Blend = np.zeros([portfolio.tMax, portfolio.iMax])
        SBlend = 0
        if (numValidateWinners > 0):
            F__Blend = F__Total / numValidateWinners
            SBlend = obj.score(objective, portfolio, F__Blend)
            
        logging.info("SBlend : %s" % SBlend)
        
        #points = [util.Point(validateWinner['W_'].tolist()) for validateWinner in validateWinner_]
        #k = max(2, int(0.25 * len(points)))
        #cutoff = 0.5
        #clusters = util.kmeans(points, k, cutoff)
        #
        #validateWinner_ = [{'W_' : np.array(c.centroid.coords, dtype=float), 'provenance' : -1} for c in clusters]
        
        header_0 = ["t", "date"]
        header_1 = ["F[%s]" % k for k in range(portfolio.iMax)]
        header_2 = ["r[%s]" % k for k in range(portfolio.iMax)]
        header__ = [header_0 + header_1 + header_2]
        body__ = [[j] + [portfolio.date_[j]] + list(F__Blend[j]) + list(portfolio.r__[j]) for j in range(portfolio.tMax)]
        excel__ = header__ + body__
        excelStr = "\n".join([",".join(str(val) for val in row) for row in excel__])
        #excelStr = "\n".join(str(excel__))
        
        result = {'success' : True, 'error' : 'none', 'S_' : S_, 'SBlend' : SBlend, 'provenance' : provenance_, 'F__Blend' : F__Blend, 'excel' : excelStr}
    except (KeyboardInterrupt):
        raise
    except Exception:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("batch/%s/test/%s" % (batch, i), result, remote)
    logging.info("--------------")
    return result

