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
    
def train(batch, i, j, remote):
    logging.info("--------------")
    logging.info("episode %s" % i)
    logging.info("iter %s" % j)
    
    result = {'success' : False, 'error' : None, 'winners' : []}
    
    try:
        params = cache.get("%s/params" % batch, remote)
        portfolio = cache.get(params['portfolioKey'], remote)
        episodesParams = params['episodes']
        episodes = epi.build_episodes(episodesParams)
        trainParams = params['train']
        logging.debug("trainParams : %s" % trainParams)
        wParams = params['w']
        
        fromDate = episodes['train'][i][0]
        toDate = episodes['train'][i][1]
        logging.info("fromDate, toDate : %s, %s" % (fromDate, toDate))
        
        portfolio.instantiate(fromDate, toDate)
        
        iters = trainParams['iters']
        draws = trainParams['draws']
        epochs = trainParams['epochs']
        alpha = trainParams['alpha']
        objective = trainParams['objective']
        threshold = trainParams['threshold']
                
        winner_ = []
        for k in range(draws):
            logging.info("draw %s" % k)
            W_ = w.init(portfolio.jMax, wParams)
                            
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
                    winner_.append({'W_' : W_, 'F__' : F__, 'S' : S})
                    break
                
            logging.info("SFinal : %s", S)
        
        logging.info("winners : %s" % len(winner_))
        
        result['success'] = True
        result['winners'] = winner_
    except (KeyboardInterrupt):
        raise
    except:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("%s/train/%s.%s" % (batch, i, j), result, remote)
    logging.info("--------------")
    return result
