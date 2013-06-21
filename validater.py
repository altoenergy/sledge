import sys
sys.dont_write_bytecode = True
import logging
import cache
import episodes as epi
import portfolio as ptf
import objective as obj
import w
import date

def validate(batch, params, i, remote, debug):
    logging.info("--------------")
    logging.info("episode %s" % i)
    
    result = {'success' : False, 'error' : 'none'}
    
    try:
        portfolio = cache.get(params['portfolioKey'], remote)
        episodes = params['episodes']
        validateParams = params['validate']
        logging.debug("validateParams : %s" % validateParams)
        trainParams = params['train']
        wParams = params['w']
        
        fromDate = episodes['validate'][i][0]
        toDate = episodes['validate'][i][1]
        logging.info("fromDate, toDate : %s, %s" % (date.to_yyyymmdd(fromDate), date.to_yyyymmdd(toDate)))
        
        nFromDate = episodes['train'][i][0]
        nToDate = episodes['train'][i][1]
        logging.info("nFromDate, nToDate : %s, %s" % (date.to_yyyymmdd(nFromDate), date.to_yyyymmdd(nToDate)))
        
        portfolio.instantiate(fromDate, toDate, True, nFromDate, nToDate)
        
        numTrainIters = trainParams['iters']
        
        accumulate = validateParams['accumulate']
        objective = validateParams['objective']
        threshold = validateParams['threshold']
            
        trainLibrary = []
        winner_ = []
        loser_ = []
        numCandidates = 0
        iTrainFrom = 0 if accumulate else i
        iTrainTo = i + 1
        for iTrain in range(iTrainFrom, iTrainTo):
            for j in range(numTrainIters):
                logging.info("train %s.%s : " % (iTrain, j))
                trainResult = cache.get("batch/%s/train/%s.%s" % (batch, iTrain, j), remote)
                trainWinner_ = trainResult['winner_']
                numCandidates += len(trainWinner_)
                for trainWinner in trainWinner_:
                    W_ = trainWinner['W_']
                    F__ = w.run_W(portfolio, W_, wParams)  
                    S = obj.score(objective, portfolio, F__)
                    outcome = {'W_' : W_, 'S' : S, 'provenance' : iTrain}
                    if (debug):
                        outcome.update({'F__' : F__})
                    if (S >= threshold):
                        winner_.append(outcome)
                    else:
                        loser_.append(outcome)
                        
                            
        logging.info("candidates : %s" % numCandidates)
        logging.info("winners : %s" % len(winner_))
        logging.info("losers : %s" % len(loser_))
        
        result = {'success' : True, 'error' : 'none', 'winner_' : winner_, 'loser_' : loser_}
    except (KeyboardInterrupt):
        raise
    except:
        result['error'] = sys.exc_info()[0]
        logging.info("error %s", result['error'])

    cache.put("batch/%s/validate/%s" % (batch, i), result, remote)
    logging.info("--------------")
    return result
