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
portfolio = "default"
batches = "base"
remote = False
debug = False
pvdebug = False
logging.getLogger().setLevel(level = logging.DEBUG if pvdebug else logging.INFO)

while (True):
    try:
        print "--study=%s--portfolio=%s--batches=%s--remote=%s--debug=%s--" % (study, portfolio, batches, remote, debug)
        action = util.get_str_input("action () : ", "")
    except (KeyboardInterrupt):
        pass
        print ""
        break
    except:
        print sys.exc_info()
        break
        
    try:
        if (action == ""):
            pass
        elif (action == "?"):
            print "study     :  specify study name"
            print "portfolio :  specify portfolio"
            print "batches   :  specify batches to run (base, * or numbered)"
            print "remote    :  toggle remote mode"
            print "debug     :  toggle debug mode"
            print "create    :  create and cache portfolio"
            print "prepare   :  prepare batches"
            print "train     :  run training"
            print "validate  :  run validation"
            print "test      :  run testing"
            print "report    :  run summary report"
            print "run       :  train, validate, test and report"
            print "track     :  track progress of jobs (remote only)"
            print "review    :  review performance of jobs (remote only)"
            print "dump      :  display cache item(s)"
            print "export    :  copy cache item(s) to clipboard"
            print "clear     :  clear cache item(s)"
            print "quit      :  quit"
            print "?         :  display help"
        elif (action == "portfolio"):
            portfolio = util.get_str_input("portfolio (%s) : " % portfolio, portfolio)
        elif (action == "study"):
            study = util.get_str_input("study (%s) : " % study, study)
        elif (action == "batches"):
            batches = util.get_str_input("batches (%s) : " % batches, batches)
        elif (action == "create"):
            portfolioParams = util.load_json_file("portfolio/%s.json" % portfolio)
            aPortfolio = ptf.Portfolio(portfolioParams)
            print "caching %s" % portfolio
            cache.put('portfolio/%s' % portfolio, aPortfolio, remote)
        elif (action == "remote"):
            remote = not remote
        elif (action == "debug"):
            debug = not debug
        elif (action == "pvdebug"):
            pvdebug = not pvdebug
            print pvdebug
            logging.getLogger().setLevel(level = logging.DEBUG if pvdebug else logging.INFO)
        elif (action == "prepare"):
            batcher.prepare(study, portfolio, remote)
        elif (action == "train"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.train(batch, remote, debug)
        elif (action == "validate"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.validate(batch, remote, debug)
        elif (action == "test"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.test(batch, remote, debug)
        elif (action == "report"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.report(batch, remote, debug)
        elif (action == "run"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.run(batch, remote, debug)
        elif (action == "track"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.track(batch, remote, debug)
        elif (action == "review"):
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.review(batch, remote, debug)
        elif (action == "dump" or action == "export"):
            key = util.get_str_input("key (report) : ", "report")
            xpath = util.get_str_input("xpath () : ", "")
            batch_ = batcher.interpret_batches(study, portfolio, batches, remote)
            for batch in batch_:
                print batch
                batcher.dump(batch, remote, key, xpath, action == "export")
            #batcher.dump_old(study, portfolio, shift, remote, key, xpath, action == "export")
        elif (action == "clear"):
            key = util.get_str_input("key (batch/%s-%s) : " % (study, portfolio), "batch/%s-%s" % (study, portfolio))
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
