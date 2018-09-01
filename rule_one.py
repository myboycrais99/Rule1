"""

"""

import rule_one_utils
import logging.config
from multiprocessing.dummy import Pool as ThreadPool
# from multiprocessing import Pool
import time

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('RuleOneLogger')


if __name__ == "__main__":

    tickers = ["AAPL", "GOOG", "BRK.B", "MRK", "DDD", "NFLX", "AMZN"]

    # bob = rule_one_utils.ScrapeBarchartBalanceSheetHTML("AAPL")
    # print(bob.data)
    # cat = rule_one_utils.ScrapeTDAmeritradeHTML("AAPL")
    # print(cat.data)

    if True:

        # make the Pool of workers
        pool = ThreadPool(len(tickers))

        start_time = time.time()
        # results = pool.map(rule_one_utils.ScrapeTDAmeritradeHTML,
        #                    tickers)

        results = pool.map(rule_one_utils.ScrapeFinancialModelingPrepJSON,
                           tickers)

        pool.close()
        pool.join()

        # print(results[0].ticker, results[0].data)
        print("\n\nThreaded Total Time: {}".format(time.time() - start_time))

        for ii in results:
            try:
                print(ii.ticker, ii.data["Net income"], ii.report_month)
            except KeyError:
                print("ERROR: ", ii.ticker)

    # dog = rule_one_utils.ScrapeIEXTradingFinancialsJSON("WMT")
    # print(dog.status_code, dog.data["currentAssets"], dog.data)

    # pig = rule_one_utils.ScrapeFinancialModelingPrepJSON("NFLX")
    # print(pig.data)

    pass
