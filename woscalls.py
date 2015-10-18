from wos import Wos
import os
from datetime import datetime
import json
from metawoslite import MetaWosLite
from sift import SiftSearchResults
import time


class WosCalls():
    """Run searches against the WOS API using the Wos class."""

    def __init__(self, search_queries=None, search_term_sets=None, sleep_time=1, database_id="WOS", search_client="Lite"):
        """
        Initialize search queries.

        Keyword arguments:
        search_queries (list) -- Provide fully created queries in a list.
        search_terms (list) -- Provide series of searches as key-value pairs in a list.
        """
        self.search_queries = search_queries
        self.search_term_sets = search_term_sets
        if not search_queries and not search_term_sets:
            print "No searches provided. Include either 'search_queries' or 'search_terms' in argument."
        self.search_client = search_client
        self.database_id = database_id
        self.wos = Wos(sleep_time=sleep_time, client=self.search_client)
        self.wos.authorize()
        self.wos.retrieve_parameters()


    def get_all_search_results(self):
        """Return all results from queries defined in __init__."""
        
        # Keep track of total result count across all searches.
        self.total_results = 0

        for search_query in self.search_queries:
            self.__run_search(search_query)

        print "Process complete."
        print "Returned {0} records".format(self.total_results)


    def __run_search(self, query):
        """
        Communicate with the WOS class to run a search.

        args:
            query (str): complete and well-formatted search query.
        """
        self.wos.query_parameters(query, database_id=self.database_id)
        self.wos.search(self.wos.qp, self.wos.retrieve_parameters())
        self.total_results += self.wos.records_found
        # WOS imposes a limit on number of searches per session -- check after each query and restart session is necessary.
        self.check_session()


    def find_exact_match(self):
        """Search for known item.

        If more than one result returned, sift through results to find most appropriate match. If one record can't be isolated
        store all best guesses as matches for further manual editing.
        """
        self.total_results = 0
        self.article_data = {}
        count = 0
        errors = 0
        for search_data in self.search_term_sets:
            count += 1
            print count,
            all_results = []
            self.search_data_update = search_data.copy()
            try:
                self.__run_search(search_data["query"])

                # Return 1 result, assume with reasonable confidence this is the
                # 'correct' hit.
                if self.wos.records_found == 1:
                    metalite = MetaWosLite(dict(self.wos.search_results.records[0]))
                    wos_metadata = metalite.get_metadata()
                    self.search_data_update.update(wos_metadata)
                    # TODO Fix result count. It always comes out 1.
                    self.search_data_update["wos_result_count"] = 1
                    all_results = [self.search_data_update]


                # With more than 1 results, attempt to sift to find 1 correct, or several
                # plausible results to store.
                elif self.wos.records_found > 1:
                    result_count = 0
                    for search_record in self.wos.search_results.records:

                        metalite = MetaWosLite(dict(search_record))
                        wos_metadata = metalite.get_metadata()
                        sifter = SiftSearchResults(self.search_data_update, wos_metadata)
                        sift_result = sifter.assess_match()
                        print "----{0}".format(sift_result)
                        if sift_result == "exact_match":
                            self.search_data_update.update(wos_metadata)
                            result_count = 1
                            all_results = [self.search_data_update]
                            break

                        elif sift_result == "probable_match":
                            result_count += 1
                            pmatch = self.search_data_update.copy()
                            pmatch.update(wos_metadata)
                            
                            all_results.append(pmatch)

                    print "----Storing {0} record(s)".format(len(all_results))
                else:
                    all_results = [self.search_data_update]

                self.article_data[search_data["id"]] = all_results
            
            except Exception as e:
                print e
                if "Throttle" in e or "throttle" in e:
                    time.sleep(60)
                errors += 1

        #print self.article_data
        print "Processed {0} records, Encountered {1} errors.".format(count, errors)


    def run_phylo_process(self):
        """
        Search algorithm designed specifically to work with Prof Ohlrogge's data.
        """
        self.total_results = 0
        for search_term_set in self.search_term_sets:
            query = self.wos.advanced_search(search_term_set, fields=["author", "source", ""])


    def check_session(self):
        """If session has lasted too long, break and restart session."""
        if self.wos.total_calls > 2000:

            self.wos.close_session()


    def get_citing_articles(self):

        for record in self.wos.metadata_collection["search_results"]:
            uid = record["accession_number"]
            self.wos.citing_articles(uid, self.wos.retrieve_parameters())
            self.check_session()

        print "Process complete."
        print "Searched {0} UIDs".format(len(self.wos.metadata_collection["search_results"]))


    def get_cited_references(self, get_full_records=True, json_file=None):
        """
        Get all citations mentioned in a given article.

        Keyword arguments:
        get_full_records (bool) -- if true, perform title search on references with full metadata.
        """

        if json_file:
            search_returns = json.load(open(json_file, "r"))

        else:
            search_returns = self.wos.metadata_collection["search_results"]

        for index, record in enumerate(search_returns):
            print "Record", index
            uid = record["accession_number"]
            self.wos.cited_references(uid, self.wos.retrieve_parameters(option={"key": "Hot", "value": "On"}), database_id="WOS", get_full_records=get_full_records)
            self.check_session()

        print "Process complete."
        print "Searched {0} UIDs".format(len(self.wos.metadata_collection["search_results"]))


    def make_results_tsv(self, search_type, output_file=None):

        if not output_file:
            output_file = os.path.join(".", "{0}_results_{1}.tsv".format(search_type, datetime.now().strftime("%Y-%m-%d-%H%M")))
        
        if not self.wos.metadata_collection[search_type]:
            print "No search results to process."

        else:
            with open(output_file, "w") as fh:
                fh.write("\t".join(self.wos.metadata_collection[search_type][0].keys()) + "\n")
                for record in self.wos.metadata_collection[search_type]:
                    fh.write("\t".join([record[i] for i in record]).encode("utf8"))
                    """
                    for item in record:
                        fh.write((record[item] + "\t").encode("utf8")) 
                    """
                    fh.write("\n")

    def make_cited_records_tsv(self, output_file=None):
        pass


# archival
grains_queries = [                        
                        'TS=("long duration" NEAR/1 cajanus)',
                        'TS=("long duration" NEAR/1 "pigeon pea")',
                        'TS=("long duration" NEAR/1 pigeonpea)',
                        'TS=(perennial NEAR/1 grain)',
                        'TS=(perennial NEAR/1 cajanus)',
                        'TS=(perennial NEAR/1 "pigeon pea")',
                        'TS=(perennial NEAR/1 pigeonpea)',
                        'TS=(perennial NEAR/1 oryza)',
                        'TS=(perennial NEAR/1 rice)',
                        'TS=(perennial NEAR/1 "rye" not "ryegrass" not "rye-grass" not "rye grass")',
                        'TS=(perennial NEAR/1 "secale" not "ryegrass" not "rye-grass" not "rye grass")',
                        'TS=(perennial NEAR/1 sorghum)',
                        'TS=(perennial NEAR/1 triticum)',
                        'TS=(perennial NEAR/1 wheat)',
                        'TS=(ratoon* NEAR/5 cajanus)',
                        'TS=(ratoon* NEAR/5 "pigeon pea")',
                        'TS=(ratoon* NEAR/5 pigeonpea)',
                        'TS=(ratoon* NEAR/5 oryza)',
                        'TS=(ratoon* NEAR/5 rice)',
                        'TS=(ratoon* NEAR/5 sorghum)'
                        ]

