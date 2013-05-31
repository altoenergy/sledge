import sys
sys.dont_write_bytecode = True
import logging
import cache
import cloud
import util
import portfolio as ptf
import batcher

cloud.config.log_level = 'ERROR'
cloud.config.commit()

study = "default"
shift = False
remote = False
debug = False
logging.getLogger().setLevel(level = logging.DEBUG if debug else logging.INFO)

while (True):
    try:
        print "------study=%s------shift=%s------remote=%s------debug=%s------" % (study, shift, remote, debug)
        action = util.get_str_input("action (?) : ", "?")
    except (KeyboardInterrupt):
        pass
        print ""
        break
    except:
        print sys.exc_info()
        break
        
    try:
        if (action == "?"):
            print "portfolio :  create portfolio (can be slow)"
            print "study     :  specify study name"
            print "remote    :  toggle remote mode"
            print "shift     :  toggle shift mode"
            print "debug     :  toggle debug mode"
            print "create    :  create all batches in study"
            print "train     :  run all training"
            print "validate  :  run all validation"
            print "test      :  run all testing"
            print "report    :  summarise batch results"
            print "*         :  train, validate, test and report"
            print "track     :  track progress of jobs (remote only)"
            print "review    :  review performance of jobs (remote only)"
            print "dump      :  display cache item(s)"
            print "export    :  copy cache item(s) to clipboard"
            print "clear     :  clear cache item(s)"
            print "quit      :  quit"
            print "?         :  display help"
        elif (action == "portfolio"):
            name = util.get_str_input("name (%s) : " % batch, batch)
            portfolioParams = util.load_json_file("portfolio/%s.json" % name)
            portfolio = ptf.Portfolio(portfolioParams)
            cache.put('portfolio/%s' % name, portfolio, remote)
        elif (action == "study"):
            study = util.get_str_input("study (%s) : " % study, study)
        elif (action == "remote"):
            remote = not remote
        elif (action == "shift"):
            shift = not shift
        elif (action == "debug"):
            debug = not debug
            logging.getLogger().setLevel(level = logging.DEBUG if debug else logging.INFO)
        elif (action in ["create", "train", "validate", "test", "report", "*", "track", "review"]):
            batcher.act(action, study, shift, remote)
        elif (action == "dump" or action == "export"):
            key = util.get_str_input("key (report) : ", "report")
            xpath = util.get_str_input("xpath () : ", "")
            batcher.dump(study, shift, remote, key, xpath, action == "export")
        elif (action == "clear"):
            key = util.get_str_input("key (batch/%s) : " % study, "batch/%s" % study)
            if (remote):
                k = cloud.call(cache.delete_prefix, key)
                logging.info(k)
            else:
                cache.clear(key, False)
        elif (action == "quit"):
            sys.exit()
        else:
            print "action %s unknown" % action
    except (KeyboardInterrupt):
        pass
        print ""
    except:
        print sys.exc_info()
        pass
