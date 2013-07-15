import math
import numpy as np
import portfolio as ptf

def init_f(size):
    initF_ = np.empty(size)
    initF_.fill(1.0 / size)
    return initF_

def eval_w(prevF_, x__, w__, wParams):
    iMax = np.size(prevF_)
    f_ = np.empty(iMax)
    wEval = wParams['eval']
    if (wEval == 'exp'):
        for i in range(iMax):
#            x__[i, -1] = prevF_[i]
            x__[i][-1] = prevF_[i]
            f_[i] = math.exp(np.dot(w__[i], x__[i]))
        F_ = f_ / np.sum(f_)
    elif (wEval == 'pv'):
        for i in range(iMax):
            x__[i, -1] = prevF_[i]
            f_[i] = np.dot(w__[i], x__[i])
        m = 1.0 / iMax
        F_ = np.minimum(m, np.maximum(-m, f_))
    else:
        raise InputError("wEval %s unknown" % wEval)
    return F_

def run_w(portfolio, w__, wParams):
    F__ = np.empty([portfolio.tMax, portfolio.iMax])
    F__[0] = init_f(portfolio.iMax)
    for t in range(1, portfolio.tMax):
        F__[t] = eval_w(F__[t - 1], portfolio.x___[t], w__, wParams)
    return F__

def run_W(portfolio, W_, wParams):
    return run_w(portfolio, portfolio.split(W_), wParams)

def init(size, wParams):
    wInit = wParams['init']
    if (wInit == 'rand'):
        return math.sqrt(3.0 / size) * (2 * np.array(np.random.random(size)) - 1)
    elif (wInit == 'es'):
        return np.array([-17.8315784643401, 7.54831415172555, 7.10669245771246, 3.08458031669017,
                        -18.0719442410111, 10.4235863115538, 9.09097757214456, 3.27278753890559,
                        -14.7971106946605, 0.803001968346536, 0.649026283159846, -3.4110717061195])
    elif (wInit == 'pv'):
        return (2 * np.array(np.random.random(size)) - 1) / size
    else:
        raise InputError("wInit %s unknown" % wInit)
