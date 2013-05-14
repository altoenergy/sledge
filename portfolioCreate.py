import sys
sys.dont_write_bytecode = True
import pickle
import util
import cache
import portfolio as ptf

name = util.get_str_input("name (default) : ", "default")
remote = util.get_bool_input("and remote (False) : ", False)
portfolioParams = util.load_json_file("json/portfolio/%s.json" % name)
portfolio = ptf.Portfolio(portfolioParams)
cache.put('portfolio/%s' % name, portfolio, False)
if (remote):
    cache.put('portfolio/%s' % name, portfolio, True)
