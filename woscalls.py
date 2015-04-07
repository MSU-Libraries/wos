from wos import Wos
import os

class WosCalls():
    """Run searches against the WOS API using the Wos class."""

    def __init__(self, search_queries=None):
        """
        Initialize search queries.

        Keyword arguments:
        search_queries (list) -- Provide queries in a list or leave unset to use queries below.
        """
        self.wos = Wos()
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
            print "Processing query: {0}".format(search_query)
            self.wos.query_parameters(search_query)
            self.wos.search(self.wos.qp, self.wos.retrieve_parameters())
            self.total_results += self.wos.records_found

        print "Process complete."
        print "Returned {0} records".format(self.total_results)


    def get_citing_articles(self):

        for record in self.wos.metadata_collection["search_results"]:
            uid = record["accession_number"]
            self.wos.citing_articles(uid, self.wos.retrieve_parameters())

        print "Process complete."
        print "Searched {0} UIDs".format(len(self.wos.metadata_collection))


    def get_cited_references(self):

        for record in self.wos.metadata_collection["search_results"]:
            uid = record["accession_number"]
            self.wos.cited_references(uid, self.wos.retrieve_parameters(option={"key": "Hot", "value": "On"}))

        print "Process complete."
        print "Searched {0} UIDs".format(len(self.wos.metadata_collection))


    def make_results_tsv(self, search_type, output_file=None):

        if not output_file:
            output_file = os.path.join(".", search_type+"_results.tsv")
        
        if not self.wos.metadata_collection[search_type]:
            print "No search results to process."

        else:
            with open(output_file, "w") as fh:
                fh.write("\t".join(self.wos.metadata_collection[search_type][0].keys()) + "\n")
                for record in self.wos.metadata_collection[search_type]:
                    for item in record:
                        fh.write((record[item] + "\t").encode("utf8")) 
                    fh.write("\n")

    def make_cited_records_tsv(self, output_file=None):
        pass


