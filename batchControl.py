import sys
sys.dont_write_bytecode = True
import logging
import itertools as it
import pprint as pp
import cache
import cloud
import util
import portfolio as ptf
import batcher
import Tkinter as tk

cloud.config.log_level = 'ERROR'
cloud.config.commit()

while (True):
    try:
        print "------batch=?------remote=?------debug=?------"
        batch = util.get_str_input("batch (default) : ", "default")
        remote = util.get_bool_input("remote (False) : ", False)
        debug = util.get_bool_input("debug (False) : ", False)
        logging.getLogger().setLevel(level = logging.DEBUG if debug else logging.INFO)
        
        while (True):
            try:
                print "------batch=%s------remote=%s------debug=%s------" % (batch, remote, debug)
                action = util.get_str_input("action (?) : ", "?")
                
                if (action == "?"):
                    print "portfolio :  create portfolio (can be slow)"
                    print "batch     :  package portfolio with parameters"
                    print "train     :  train per batch parameters"
                    print "validate  :  validate per batch parameters"
                    print "test      :  test per batch parameters"
                    print "report    :  summarise batch results"
                    print "*         :  train, validate, test and report"
                    print "review    :  review batch performance (remote only)"
                    print "dump      :  dump a cache item"
                    print "delete    :  delete a cache item"
                    print "?         :  display help"
                    print "quit      :  quit"
                elif (action == "portfolio"):
                    name = util.get_str_input("name (%s) : " % batch, batch)
                    portfolioParams = util.load_json_file("portfolio/%s.json" % name)
                    portfolio = ptf.Portfolio(portfolioParams)
                    cache.put('portfolio/%s' % name, portfolio, False)
                    if (remote):
                        cache.put('portfolio/%s' % name, portfolio, True)
                elif (action == "batch"):
                    portfolioName = util.get_str_input("portfolio name (%s) : " % batch, batch)
                    episodesFile = util.get_str_input("episodes file (%s) : " % batch, batch)
                    trainFile = util.get_str_input("train file (%s) : " % batch, batch)
                    validateFile = util.get_str_input("validate file (%s) : " % batch, batch)
                    testFile = util.get_str_input("test file (%s) : " % batch, batch)
                    wFile = util.get_str_input("w file (%s) : " % batch, batch)
                    
                    episodesParams = util.load_json_file("episodes/%s.json" % episodesFile)
                    trainParams = util.load_json_file("train/%s.json" % trainFile)
                    validateParams = util.load_json_file("validate/%s.json" % validateFile)
                    testParams = util.load_json_file("test/%s.json" % testFile)
                    wParams = util.load_json_file("w/%s.json" % wFile)
                        
                    params = {'portfolioKey' : "portfolio/%s" % portfolioName, 'episodes' : episodesParams, 'train' : trainParams,
                              'validate' : validateParams, 'test' : testParams, 'w' : wParams}
                    batcher.create(batch, params, remote)
                elif (action == "train"):
                    batcher.train(batch, remote)
                elif (action == "validate"):
                    batcher.validate(batch, remote)
                elif (action == "test"):
                    batcher.test(batch, remote)
                elif (action == "report"):
                    batcher.report(batch, remote)
                elif (action == "track"):
                    batcher.track(batch, remote)
                elif (action == "review"):
                    batcher.review(batch, remote)
                elif (action == "*"):
                    clear = util.get_bool_input("clear (False) : ", False)
                    batcher.run(batch, clear, remote)
                elif (action == "dump"):
                    key = util.get_str_input("key (report) : ", "report")
                    path = util.get_str_input("path () : ", "")
                    obj = cache.get("%s/%s" % (batch, key), remote)
                    obj = cache.xpath(obj, path)
                    pp.pprint(obj)
                elif (action == "export"):
                    key = util.get_str_input("key (report) : ", "report")
                    path = util.get_str_input("path () : ", "")
                    obj = cache.get("%s/%s" % (batch, key), remote)
                    obj = cache.xpath(obj, path)
                    cl = tk.Tk()
                    #cl.withdraw()
                    #cl.clipboard_clear()
                    cl.clipboard_append(pp.pformat(obj))
                    #cl.destroy()
                    #pp.pprint(obj)
                elif (action == "delete"):
                    key = util.get_str_input("key (train) : ", "train")
                    prefix = "%s/%s" % (batch, key)
                    if (remote):
                        k = cloud.call(cache.delete_prefix, "%s" % prefix)
                        logging.info(k)
                    else:
                        cache.clear(prefix, False)
                elif (action == "quit"):
                    sys.exit()
                else:
                    print "action %s unknown" % action
            except (KeyboardInterrupt):
                pass
                print ""
                break
            except:
                print sys.exc_info()
                pass
    except (KeyboardInterrupt):
        pass
        print ""
        break
    except Exception:
        print sys.exc_info()
        pass
