#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
COPYRIGHT © 2015
MICHIGAN STATE UNIVERSITY BOARD OF TRUSTEES
ALL RIGHTS RESERVED
 
PERMISSION IS GRANTED TO USE, COPY, CREATE DERIVATIVE WORKS AND REDISTRIBUTE
THIS SOFTWARE AND SUCH DERIVATIVE WORKS FOR ANY PURPOSE, SO LONG AS THE NAME
OF MICHIGAN STATE UNIVERSITY IS NOT USED IN ANY ADVERTISING OR PUBLICITY
PERTAINING TO THE USE OR DISTRIBUTION OF THIS SOFTWARE WITHOUT SPECIFIC,
WRITTEN PRIOR AUTHORIZATION.  IF THE ABOVE COPYRIGHT NOTICE OR ANY OTHER
IDENTIFICATION OF MICHIGAN STATE UNIVERSITY IS INCLUDED IN ANY COPY OF ANY
PORTION OF THIS SOFTWARE, THEN THE DISCLAIMER BELOW MUST ALSO BE INCLUDED.
 
THIS SOFTWARE IS PROVIDED AS IS, WITHOUT REPRESENTATION FROM MICHIGAN STATE
UNIVERSITY AS TO ITS FITNESS FOR ANY PURPOSE, AND WITHOUT WARRANTY BY
MICHIGAN STATE UNIVERSITY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
WITHOUT LIMITATION THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE. THE MICHIGAN STATE UNIVERSITY BOARD OF TRUSTEES SHALL
NOT BE LIABLE FOR ANY DAMAGES, INCLUDING SPECIAL, INDIRECT, INCIDENTAL, OR
CONSEQUENTIAL DAMAGES, WITH RESPECT TO ANY CLAIM ARISING OUT OF OR IN
CONNECTION WITH THE USE OF THE SOFTWARE, EVEN IF IT HAS BEEN OR IS HEREAFTER
ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
 
Code written by Devin Higgins
2015
(c) Michigan State University Board of Trustees
Licensed under GNU General Public License (GPL) Version 2.
"""

from wos import Wos
import os
from datetime import datetime
import json

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


