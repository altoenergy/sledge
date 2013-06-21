import sys
sys.dont_write_bytecode = True
import logging
import numpy as np
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w
import moody as moo
import date
    
def train(batch, params, i, j, remote, debug):
    logging.info("--------------")
    logging.info("episode %s" % i)
    logging.info("iter %s" % j)
    
    result = {'success' : False, 'error' : 'none'}
    
    try:
        portfolio = cache.get(params['portfolioKey'], remote)
        episodes = params['episodes']
        trainParams = params['train']
        logging.debug("trainParams : %s" % trainParams)
        wParams = params['w']
        
        fromDate = episodes['train'][i][0]
        toDate = episodes['train'][i][1]
        logging.info("fromDate, toDate : %s, %s" % (date.to_yyyymmdd(fromDate), date.to_yyyymmdd(toDate)))
        
        nFromDate = episodes['train'][i][0]
        nToDate = episodes['train'][i][1]
        logging.info("nFromDate, nToDate : %s, %s" % (date.to_yyyymmdd(nFromDate), date.to_yyyymmdd(nToDate)))
        
        portfolio.instantiate(fromDate, toDate, True, nFromDate, nToDate)
        
        iters = trainParams['iters']
        draws = trainParams['draws']
        epochs = trainParams['epochs']
        alpha = trainParams['alpha']
        objective = trainParams['objective']
        threshold = trainParams['threshold']
                
        winner_ = []
        loser_ = []
        for k in range(draws):
            try:
                logging.info("draw %s" % k)
                W_ = w.init(portfolio.jLen, wParams)

                for e in range(epochs + 1):
                    if (e > 0):
                        W_ = moo.run_epoch(portfolio, W_, alpha, wParams)
                    F__ = w.run_W(portfolio, W_, wParams)
                    logging.debug(F__)
                    logging.debug(portfolio.x___)
                    S = obj.score(objective, portfolio, F__)
                    if (e == 0):
                        logging.info("SInit : %s", S)
                    if (S >= threshold):
                        break
                logging.info("SFinal : %s", S)
                outcome = {'W_' : W_, 'S' : S, 'provenance' : i}
                if (debug):
                    outcome.update({'F__' : F__})
                if (S >= threshold):
                    winner_.append(outcome)
                else:
                    loser_.append(outcome)
            except (KeyboardInterrupt):
                raise
            except:
                result['error'] = sys.exc_info()[0]
                logging.info("error %s", result['error'])                
        
        logging.info("winners : %s" % len(winner_))
        logging.info("losers : %s" % len(loser_))
        
        result = {'success' : True, 'error' : 'none', 'winner_' : winner_, 'loser_' : loser_}
    except (KeyboardInterrupt):
        raise
    except:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("batch/%s/train/%s.%s" % (batch, i, j), result, remote)
    logging.info("--------------")
    return result
