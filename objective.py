import math
import numpy as np
import w

def score(objective, portfolio, F__):
    if (objective == "returns"):
        return returns(portfolio, F__)
    elif (objective == "sharp"):
        return sharp(portfolio, F__)
    else:
        return 0

def is_winner(winners, objective, threshold, portfolio, W_, wParams):
    F__ = w.run_W(portfolio, W_, wParams)  
    S = score(objective, portfolio, F__)
    if (S >= threshold):
        winners.append((S, W_))
        return True
    return False
    
def returns(portfolio, F__):
    R = 0
    for t in range(1, portfolio.tMax):
        R += np.dot(F__[t - 1], portfolio.r__[t]) - np.dot(portfolio.c_, np.absolute(F__[t] - F__[t - 1]))
    return R

def sharp(portfolio, F__):
    sumR = sumR2 = 0
    for t in range(1, portfolio.tMax):
        R = np.dot(F__[t - 1], portfolio.r__[t]) - np.dot(portfolio.c_, np.absolute(F__[t] - F__[t - 1]))
        sumR += R
        sumR2 += R * R
    A = sumR / portfolio.tMax
    B = sumR2 / portfolio.tMax
    S = A / (math.sqrt(B - A * A))
    return S
