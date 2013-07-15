import logging
import math
import numpy as np
import portfolio as ptf
import w
  
def dF_dW_numeric(portfolio, F__, w__, dw, wParams):
    dF_dW_ = np.empty([portfolio.iMax, portfolio.jLen])
    F_base = w.eval_w(F__[0], portfolio.x___[1], w__, wParams)
    J = 0
    for i in range(portfolio.iMax):
        for j in range(portfolio.jLen_[i]):
            w__[i][j] += dw
            F_ = w.eval_w(F__[0], portfolio.x___[1], w__, wParams)
            w__[i][j] -= dw
            dF_dW_[:, J] = (F_ - F_base) / dw
            J += 1
    return dF_dW_

def dF_dW_init_ES(portfolio, F__, w__, dw):
    dF_dW_ = np.empty([portfolio.iMax, portfolio.jLen])
    for n in range(portfolio.iMax):
        J = 0
        for i in range(portfolio.iMax):
            for j in range(portfolio.jLen_[i]):
                m = 2.0 / 9 if (n == i) else -1.0 / 9
#                dF_dW_[n, J] = m * portfolio.x___[1, i, j]
                dF_dW_[n, J] = m * portfolio.x___[1][i, j]
                J += 1
    return dF_dW_
    
def run_epoch(portfolio, W_, alpha, wParams):
    w__ = portfolio.split(W_)
    F__ = np.empty([portfolio.tMax, portfolio.iMax])
    F__[0] = w.init_f(portfolio.iMax)
    dFdWMethod = wParams['dFdW']
    if (dFdWMethod == 'numeric'):
        dF_dW_ = dF_dW_numeric(portfolio, F__, w__, 0.01, wParams)
    elif (dFdWMethod == 'es'):
        dF_dW_ = dF_dW_init_ES(portfolio, F__, w__, 0.01)
    else:
        raise InputError("dFdWMethod %s unknown" % dFdWMethod)
                        
    #logging.debug("dFdW %s" % dF_dW_)
    
    #logging.debug("W_ %s" % W_)
    sumR = sumR2 = 0
    for t in range(1, portfolio.tMax):
        x__ = portfolio.x___[t] # (asset x feature)
        r_ = portfolio.r__[t] # (asset)
        F__[t] = w.eval_w(F__[t - 1], x__, w__, wParams)
        dF_ = F__[t] - F__[t - 1]
        R = np.dot(F__[t - 1], r_) - np.dot(portfolio.c_, np.absolute(dF_))
        sumR += R
        sumR2 += R * R
        A = sumR / t
        B = sumR2 / t
        BmA2 = B - A * A

        dRdF_ = -portfolio.c_ * np.sign(dF_)
        dRdF_1 = r_ + portfolio.c_ * np.sign(dF_)
        dSdW_a = np.dot(dRdF_1, dF_dW_)
        
        for n in range(portfolio.iMax):
            J = 0
            for i in range(portfolio.iMax):
                for j in range(portfolio.jLen_[i]):
                    x = x__[n][j] if (n == i) else 0
                    dF_dW_[n, J] = F__[t, n] * (1 - F__[t, n]) * (x + w__[n][-1] * dF_dW_[n, J])
                    J += 1
        
        #logging.debug("x__ %s" % x__)
        #logging.debug("dFdW %s" % dF_dW_)
        #logging.debug("dRdF %s" % dRdF_)
        #logging.debug("dRdF_1 %s" % dRdF_1)
        dSdW_b = np.dot(dRdF_, dF_dW_)
        c = 0 if (BmA2 == 0) else (B - A * R) / math.pow(BmA2, 1.5)
        dSdW_ = c * (dSdW_a + dSdW_b)
        #logging.debug("dSdW_ %s" % dSdW_)
        W_ += alpha * c * (dSdW_a + dSdW_b)
        #logging.debug("W_ %s" % W_)
    return W_
