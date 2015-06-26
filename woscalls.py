from wos import Wos
import os
from datetime import datetime

class WosCalls():
    """Run searches against the WOS API using the Wos class."""

    def __init__(self, search_queries=None, sleep_time=1):
        """
        Initialize search queries.

        Keyword arguments:
        search_queries (list) -- Provide queries in a list or leave unset to use default queries below.
        """
        self.wos = Wos(sleep_time=sleep_time)
        self.wos.authorize()
        self.wos.retrieve_parameters()

        if not search_queries:
            self.search_queries = [
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
                        'TS=(ratoon* NEAR/5 sorghum)',
                        ]
        else:
            self.search_queries = search_queries

    def get_all_search_results(self):
        """Return all results from queries defined in __init__."""
        self.total_results = 0
        for search_query in self.search_queries:
            self.wos.query_parameters(search_query)
            self.wos.search(self.wos.qp, self.wos.retrieve_parameters())
            self.total_results += self.wos.records_found
            self.check_session()

        print "Process complete."
        print "Returned {0} records".format(self.total_results)


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


    def get_cited_references(self, get_full_records=True):
        """
        Get all citations mentioned in a given article.

        Keyword arguments:
        get_full_records (bool) -- if true, perform title search on references with full metadata.
        """

        for index, record in enumerate(self.wos.metadata_collection["search_results"]):
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


