"""

"""
import rule_one_db
import rule_one_utils
# import logging.config

# from multiprocessing import Pool
import numpy as np
import time

# logging.config.fileConfig('logging.conf')
# logger = logging.getLogger('RuleOneLogger')




if __name__ == "__main__":

    logger = rule_one_utils.RuleOneLogger().logger

    tickers = ["AAPL", "GOOG", "BRK.B", "MRK", "DDD", "CEM", "WPXP", "ARES",
               "NFLX", "AMZN", "RTN", "BA", "BAC", "GOOGL", "ADT", "AEO",
               "AET", "AJRD", "AMC", "ANF", "AZO", "BAH", "BB", "BBY",
               "BGG", "BUD", "CAT", "ZBK", "FAX", "WPXP", "MITT^A", "ALP^O",
               "BML^G", "GS^N"]

    bob = rule_one_db.RuleOneDatabase(host='localhost', db='rule1_devdb',
                                      user='ryan', password='password')

    # ans, dt = rule_one_utils.function_to_multithread(rule_one_utils.CalcEPS,
    #                                                  tickers[:10])
    # for ii in ans:
    #     if bool(ii.eps):
    #         if not np.isnan(ii.eps):
    #             print("{} {:.2f} - Confidence: {}\n".format(ii.ticker, ii.eps,
    #                                                         ii.confidence))
    # print("\nEPS for {} tickers calculated in {:.3f} seconds"
    #       "".format(len(ans), dt))

    import multiprocessing
    from multiprocessing.dummy import Pool as ThreadPool
    from functools import partial






    # start_time = time.time()
    # pool = ThreadPool(3)
    # results = pool.map(partial(rule_one_utils.CalcEPS, year=2017,
    #                            redundancy=2), tickers[0:10])
    #
    # # results = pool.map(partial(rule_one_utils.ScrapeMorningStarHTML,
    # #                            statements=["cash", "balance"]), tickers[0:10])
    #
    # pool.close()
    # pool.join()
    #
    # for ii in results:
    #     if bool(ii.eps):
    #         if not np.isnan(ii.eps):
    #             print("{} {:.2f} - Confidence: {}\n"
    #                   "".format(ii.ticker, ii.eps, ii.confidence))
    #
    # print("\nEPS for {} tickers calculated in {:.3f} seconds"
    #       "".format(len(results), time.time()-start_time))



    # tmp = rule_one_utils.ScrapeMorningStarHTML(tickers[0],
    #                                            statements=["cash", "balance"])
    #
    # print(tmp.data)

    start_time = time.time()
    pool = ThreadPool(10)
    results = pool.map(partial(rule_one_utils.ScrapeMorningStarHTML,
                               statements=["cash"]), tickers[:10])

    pool.close()
    pool.join()

    print("\nMorningStart data for {} tickers fetched in {:.3f} seconds"
          "".format(len(results), time.time()-start_time))

    pass

    # data = bob.get_stocks(active=True)
    # print(data[:3], "\n\n", len(data), 6852)




