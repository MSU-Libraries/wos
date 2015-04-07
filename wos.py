from __future__ import division
from suds.client import Client
from suds.transport.http import HttpTransport
from metawos import MetaWos
from datetime import date
from lxml import etree, objectify
import urllib2
import time

import logging
logging.basicConfig(level=logging.INFO)

logging.getLogger('suds.client').setLevel(logging.ERROR)

class Wos():
    """Handle requests to the Web of Knowledge API"""

    def __init__(self, client="Search"):
        """
        Establish URLs for authentication, search, and search lite methods.

        Keyword arguments:
        client (str) -- search client to initialize: choose "Lite" or "Search"
        """

        self.client = client
        self.auth_url = "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl"
        self.search_lite_url = "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl"
        self.search_url = "http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl"
        self.auth_client = None
        self.search_client = None
        self.metadata_collection = {"search_results": [],
                                    "forward_citations": [],
                                    "backward_citations": []}
        self.qp = None
        self.rp = None
        self.uids = []

    def authorize(self):
        """Run authenticate service to retrieve token."""
        auth_client = Client(self.auth_url)
        try:
            self.sid_token = auth_client.service.authenticate()
            self._add_sid()
            print "Search client authorized."
            
        except Exception as e:
            print "Authentication failed."
            print e

    def _add_sid(self):
        """Create URL opener with authentication token as header."""
        opener = urllib2.build_opener()
        opener.addheaders = [('Cookie', 'SID="'+self.sid_token+'"')]
        http = HttpTransport()
        http.urlopener = opener
        self._establish_search_client(http)

    def _establish_search_client(self, http):
        """Establish search client for "Search" or "SearchLite" client."""
        if self.client == "Search":
            self.search_client = Client(self.search_url, transport=http)
        elif self.client == "Lite": 
            self.search_client = Client(self.search_lite_url, transport=http)
        else:
            print "Invalid search client"

    def print_wsdl(self):
        """Print WSDL information, including methods and types."""
        if self.search_client:
            print self.search_client
        else:
            print "Search client not established"

    def search(self, qp, rp):
        """
        Send search query to WOS and return results object.

        Arguments:
        qp (obj) -- QueryParameters object created via query_parameters method.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.
        """
        self.qp = qp
        self.rp = rp
        self.category = "search_results"
        if self.client == "Lite":
            self.search_results = self.search_client.service.search(qp, rp)
            self.query_id = self.search_results.queryId
            self.records_returned = self.search_results.records
            self.records_found = self.search_results.recordsFound
            self.records_searched = self.search_results.recordsSearched
            self.uids = [i.uid for i in self.search_results.records]
            self._MakeDict()
        elif self.client == "Search":
            self._run_search()

        return self.search_results

    def query_parameters(self, query, time_begin="1900-01-01", time_end=None, database_id="WOS", query_language="en", symbolic_timespan=None, editions=None):
        """
        Create QueryParameters object for use in search function.

        Positional arguments:
        query (string) -- Query formatted according to WOS specifications.

        Keyword arguments:
        time_begin (str) -- date in YYYY-MM-DD format.
        time_end (str) -- date in YYYY-MM-DD format.
        database_id (str) -- from the WOS set of database abbreviations. "WOS" correpsonds to the WOS core collection.
        query_language (str) -- "en" the only currently allowed value.
        symbolic_timespan (str) -- a human-readable timespan, e.g. "4weeks", must be null if time_begin and time_end used.
        editions (list) -- TODO list of sub-components of the selected database to use.
        """
        self.query = query
        self.time_begin = time_begin
        self.time_end = time_end
        self.database_id = database_id
        self.query_language = query_language
        self.symbolic_timespan = symbolic_timespan
        self.editions = editions

        self.qp = self.search_client.factory.create("queryParameters")
        self.qp.userQuery = query
        
        if symbolic_timespan is None:
            self.qp.timeSpan = self._time_span(time_begin, time_end)
        else:
            self.qp.symbolicTimeSpan = self.symbolic_timespan
        
        self.qp.databaseId = database_id
        self.qp.queryLanguage = query_language
        
        return self.qp

    def _time_span(self, time_begin, time_end):
        """
        Use time span variables from search function to establish timespan settings.

        Positional arguments:
        time_begin (str) -- date in YYYY-MM-DD format.
        time_end (str) -- date in YYYY-MM-DD format
        """
        timespan = self.search_client.factory.create("timeSpan")
        timespan.begin = time_begin
        if time_end is not None:
            timespan.end = time_end
        else:
            d = date.today()
            timespan.end = d.isoformat()
        return timespan


    def retrieve_parameters(self, first_record=1, count=100, sort_field=None, view_field=None, option=None):
        """
        Create RetrieveParameters object for use in search function.

        Keyword arguments:
        first_record (int) -- The number of the first record to return in the search.
        count (int) -- Number of records to return (maximum 100).
        sort_field (list) -- TODO Field to sort by (should be WOS field abbreviation).
        view_field (list) -- TODO Fields to return in matched records.
        option (dict) -- TODO Requests for additional metadata.        
        """
        self.first_record = first_record
        self.count = count
        self.sort_field = sort_field
        self.view_field = view_field
        # Use 'key' and 'value' pair of "RecordIDs" and "On" to get list of unique IDs
        self.option = option

        self.rp = self.search_client.factory.create("retrieveParameters")

        if option:
            self.rp.option = option

        self.rp.firstRecord = first_record
        self.rp.count = count
         
        return self.rp

    def cited_references(self, uid, rp, database_id="WOS", query_language="en"):
        """
        Return cited references for a given article based on uid.

        Position arguments:
        uid (str) -- unique ID for a WOS document.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.

        Keyword arguments:
        query_language (str) -- "en" the only currently allowed value.
        database_id (str) -- from the WOS set of database abbreviations. "WOS" correpsonds to the WOS core collection.
        """
        self.uid = uid
        self.rp = rp
        self.category = "backward_citations"
        self.database_id = database_id
        self.query_language = query_language

        self.search_results = self.search_client.service.citedReferences(database_id, uid, query_language, rp)
        time.sleep(0.5)

        self._process_results()
        if self.records_found <> 0:
            self._get_metadata_citation(self.uid)

        if self.records_found > self.count:
            self._iterations = int(self.records_found / self.rp.count) + 1
            for i in range(1, self._iterations, 1):
                print "Getting result page {0}".format(i+1)
                self.rp = self.retrieve_parameters(first_record=1+(i)*self.count, count=self.count, 
                                                  sort_field=self.sort_field, view_field=self.view_field, option=self.option)
                self.search_client.service.citedReferences(database_id, uid, query_language, self.rp)
                time.sleep(0.5)
                self._get_metadata_citation(self.uid)


    def citing_articles(self, uid, rp, database_id="WOS", query_language="en", time_begin="1900-01-01", time_end=None, symbolic_timespan=None):
        """
        Return citing articles for a given reference based on uid.

        Position arguments:
        uid (str) -- unique ID for a WOS document.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.

        Keyword arguments:
        time_begin (str) -- date in YYYY-MM-DD format.
        time_end (str) -- date in YYYY-MM-DD format.
        database_id (str) -- from the WOS set of database abbreviations. "WOS" correpsonds to the WOS core collection.
        query_language (str) -- "en" the only currently allowed value.
        symbolic_timespan (str) -- a human-readable timespan, e.g. "4weeks", must be null if time_begin and time_end used.
        """
        self.uid = uid
        self.rp = rp
        self.database_id = database_id
        self.query_language = query_language
        self.category = "forward_citations"

        # For now, this is not configurable. TODO: make configurable.
        self.edition_desc = self.search_client.factory.create("editionDesc")

        if symbolic_timespan is None:
            self.time_span = self._time_span(time_begin, time_end)
        else:
            self.time_span = self.symbolic_timespan

        self.search_results = self.search_client.service.citingArticles(database_id, uid, self.edition_desc, self.time_span, query_language, rp)
        time.sleep(0.5)

        self._process_results()
        if self.records_found <> 0:
            self._get_metadata(self.uid)

        if self.records_found > self.count:
            self._iterations = int(self.records_found / self.rp.count) + 1
            for i in range(1, self._iterations, 1):
                self.rp = self.retrieve_parameters(first_record=1+(i)*self.count, count=self.count, 
                                                  sort_field=self.sort_field, view_field=self.view_field, option=self.option)
                self.retrieve(self.query_id, self.rp)
                time.sleep(0.5)
                self._get_metadata(self.uid)


    def retrieve_by_id(self, uid, rp, query_language="en", database_id="WOS"):
        """
        Return record by unique ID.
        
        Position arguments:
        uid (str) -- unique ID for a WOS document.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.

        Keyword arguments:
        query_language (str) -- "en" the only currently allowed value.
        database_id (str) -- from the WOS set of database abbreviations. "WOS" correpsonds to the WOS core collection.
        """
        self.item = self.search_client.service.retrieveById(database_id, uid, query_language, rp)
        return self.item


    def retrieve(self, query_id, rp):
        """
        Retrieve results based on ID from previously run search.

        Positional arguments:
        query_id (str) -- ID from previously run search.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.
        """
        self.search_results = self.search_client.service.retrieve(query_id, rp)
        time.sleep(0.5)


    def cited_references_retrieve(self, query_id):
        """
        Retrieve results based on ID from previously run cited references search.

        Positional arguments:
        query_id (str) -- ID from previously run search.
        """
        self.search_results = self.search_client.service.citedReferencesRetrieve(query_id)
        time.sleep(0.5)


    def _get_uids(self):
        """Retrieve uids from all search results and store in list with search query string."""
        uid_tag = "{http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord}UID"
        tree = etree.fromstring(self.search_results.records)
        for element in tree:
            for subelement in element:
                if subelement.tag == uid_tag:
                    self.uids.append((subelement.text, self.query))

    def _get_metadata(self, query):
        """
        Retrieve metadata from all search results and store in dictionary of elements.
        Positional arguments:
        query (str) -- the initial query string for the given search results.
        """
        self.tree = etree.fromstring(self.search_results.records)
        objectify.deannotate(self.tree, cleanup_namespaces=True)
        for record in self.tree:
            self.meta_record = MetaWos(record, query)
            self.metadata_collection[self.category].append(self.meta_record.compile_metadata())

    def _get_metadata_citation(self, query):
        """
        Special metadata processing for meager results from citedReferences search.

        query (str) -- key search term that produced the results.
        """
        for item in self.search_results.references:
            meta_record = {"docid":"",
                           "citedAuthor":"",
                           "citedTitle":"",
                           "citedWork":"",
                           "hot":"",
                           "year":""}

            for key in meta_record.keys():
                if key in item:
                    meta_record[key] = item[key]

                else:
                    meta_record[key] = "NONE"
                    
            meta_record["source_id"] = self.uid
            self.metadata_collection[self.category].append(meta_record)



    def _run_search(self):
        """Run search page by page until all results are retrieved."""
        self.search_results = self.search_client.service.search(self.qp, self.rp)
        self._get_metadata(self.query)
        time.sleep(0.5)

        self._process_results()

        if self.records_found > self.count:
            self._iterations = int(self.records_found / self.rp.count) + 1
            for i in range(1, self._iterations, 1):
                print "Getting result page {0}".format(i+1)

                self.rp = self.retrieve_parameters(first_record=1+(i)*self.count, count=self.count, 
                                                  sort_field=self.sort_field, view_field=self.view_field, option=self.option)
                self.retrieve(self.query_id, self.rp)
                time.sleep(0.5)
                self._get_metadata(self.query)

    def _process_results(self):

        self.query_id = self.search_results.queryId
        self.records_found = self.search_results.recordsFound
        self.records_searched = self.search_results.recordsSearched
        print "Found {0} Results".format(self.records_found)




