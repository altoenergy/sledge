import sys
sys.dont_write_bytecode = True
import logging
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w

def validate(batch, i, remote):
    logging.info("--------------")
    logging.info("episode %s" % i)
    
    result = {'success' : False, 'error' : None, 'winners' : []}
    
    try:
        params = cache.get("%s/params" % batch, remote)
        portfolio = cache.get(params['portfolioKey'], remote)
        episodesParams = params['episodes']
        episodes = epi.build_episodes(episodesParams)
        validateParams = params['validate']
        logging.debug("validateParams : %s" % validateParams)
        trainParams = params['train']
        wParams = params['w']
        
        fromDate = episodes['validate'][i][0]
        toDate = episodes['validate'][i][1]
        logging.info("fromDate, toDate : %s, %s" % (fromDate, toDate))
        
        portfolio.instantiate(fromDate, toDate)
        
        numTrainIters = trainParams['iters']
        
        objective = validateParams['objective']
        threshold = validateParams['threshold']
            
        trainLibrary = []
        winner_ = []
        numCandidates = 0
        for iTrain in range(i + 1):
            for j in range(numTrainIters):
                logging.info("train %s.%s : " % (iTrain, j))
                trainResult = cache.get("%s/train/%s.%s" % (batch, iTrain, j), remote)
                trainWinner_ = trainResult['winners']
                numCandidates += len(trainWinner_)
                for trainWinner in trainWinner_:
                    W_ = trainWinner['W_']
                    F__ = w.run_W(portfolio, W_, wParams)  
                    S = obj.score(objective, portfolio, F__)
                    if (S >= threshold):
                        winner_.append({'W_' : W_, 'F__' : F__, 'S' : S})
                            
        logging.info("candidates : %s" % numCandidates)
        logging.info("winners : %s" % len(winner_))
        
        result['success'] = True
        result['winners'] = winner_
    except (KeyboardInterrupt):
        raise
    except:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("%s/validate/%s" % (batch, i), result, remote)
    logging.info("--------------")
    return result
