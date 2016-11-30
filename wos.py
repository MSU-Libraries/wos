# -*- coding: utf-8 -*-

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

    def __init__(self, client="Search", sleep_time=1):
        """
        Establish URLs for authentication, search, and search lite methods.

        Keyword arguments:
        client (str) -- search client to initialize: choose "Lite" or "Search"
        """
        self.citing_metadata = False
        self.total_calls = 0
        self.sleep_time = sleep_time
        self.client = client
        self.auth_url = "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl"
        self.search_lite_url = "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl"
        self.search_url = "http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl"
        self.auth_client = None
        self.search_client = None
        self.metadata_collection = {"search_results": [],
                                    "forward_citations": [],
                                    "backward_citations": [],
                                    "hot_records": [], }
        self.qp = None
        self.rp = None
        self.uids = []

    def authorize(self):
        """Run authenticate service to retrieve token."""
        self.auth_client = Client(self.auth_url)
        try:
            self.sid_token = self.auth_client.service.authenticate()
            self._add_sid()
            print "Search client authorized."
            self.total_calls += 1
            
        except Exception as e:
            print "Authentication failed."
            print e

    def close_session(self):
        """Close session."""
        self.auth_client.service.closeSession()
        self.total_calls = 0
        self.authorize()

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

    def search(self, qp, rp, get_metadata=True):
        """
        Send search query to WOS and return results object.

        Arguments:
        qp (obj) -- QueryParameters object created via query_parameters method.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.
        """
        self.qp = qp
        self.rp = rp
        self.get_metadata = get_metadata
        if self.client == "Lite":
            self._run_search()
            """
            self.search_results = self.search_client.service.search(qp, rp)
            self.query_id = self.search_results.queryId
            self.records_returned = self.search_results.records
            self.records_found = self.search_results.recordsFound
            self.records_searched = self.search_results.recordsSearched
            self.uids = [i.uid for i in self.search_results.records]
            self._MakeDict()
            """
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

    def _view_fields(self):
        """Add view fields to retrieve parameters object."""
        

        #TODO: Complete this method.
        view_fields = self.search_client.factory.create("viewField")
        for field in self.view_field:
            view_fields.fieldName = self.view_fields
            

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

        # viewField seems not to be an option in 
        if self.view_field is not None and self.client=="Search":
            self._view_fields()



        if option:
            self.rp.option = option

        self.rp.firstRecord = first_record
        self.rp.count = count
         
        return self.rp

    def cited_references(self, uid, rp, database_id="WOS", query_language="en", get_full_records=True):
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
        self.get_full_records = get_full_records
        self.database_id = database_id
        self.query_language = query_language
        self.query = self.uid

        self.search_results = self.search_client.service.citedReferences(database_id, uid, query_language, rp)
        self.total_calls += 1
        time.sleep(self.sleep_time)

        self._process_results()
        if self.records_found <> 0:
            self._get_metadata_citation(self.uid, "backward_citations")

        if self.records_found > self.count:
            self._iterations = int(self.records_found / self.rp.count) + 1
            for i in range(1, self._iterations, 1):
                print "Getting result page {0}".format(i+1)
                self.rp = self.retrieve_parameters(first_record=1+(i)*self.count, count=self.count, 
                                                  sort_field=self.sort_field, view_field=self.view_field, option=self.option)
                self.search_client.service.citedReferences(database_id, uid, query_language, self.rp)
                self.total_calls += 1
                time.sleep(self.sleep_time)
                self._get_metadata_citation(self.uid, "backward_citations")


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
        self.citing_metadata = True
        self.uid = uid
        self.query = uid
        self.rp = rp
        self.database_id = database_id
        self.query_language = query_language

        # For now, this is not configurable. TODO: make configurable.
        self.edition_desc = self.search_client.factory.create("editionDesc")

        if symbolic_timespan is None:
            self.time_span = self._time_span(time_begin, time_end)
        else:
            self.time_span = self.symbolic_timespan

        self.search_results = self.search_client.service.citingArticles(database_id, uid, self.edition_desc, self.time_span, query_language, rp)
        time.sleep(self.sleep_time)
        self.total_calls += 1

        self._process_results()
        if self.records_found <> 0:
            self._get_metadata(self.uid, "forward_citations")

        if self.records_found > self.count:
            self._iterations = int(self.records_found / self.rp.count) + 1
            for i in range(1, self._iterations, 1):
                self.rp = self.retrieve_parameters(first_record=1+(i)*self.count, count=self.count, 
                                                  sort_field=self.sort_field, view_field=self.view_field, option=self.option)
                self.retrieve(self.query_id, self.rp)
                time.sleep(self.sleep_time)
                self._get_metadata(self.uid, "forward_citations")


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
        self.total_calls += 1
        return self.item


    def retrieve(self, query_id, rp):
        """
        Retrieve results based on ID from previously run search.

        Positional arguments:
        query_id (str) -- ID from previously run search.
        rp (obj) -- RetrieveParameters object created via retrieve_parameters method.
        """
        self.search_results = self.search_client.service.retrieve(query_id, rp)
        self.total_calls += 1
        time.sleep(self.sleep_time)


    def cited_references_retrieve(self, query_id):
        """
        Retrieve results based on ID from previously run cited references search.

        Positional arguments:
        query_id (str) -- ID from previously run search.
        """
        self.search_results = self.search_client.service.citedReferencesRetrieve(query_id)
        self.total_calls += 1
        time.sleep(self.sleep_time)


    def _get_uids(self):
        """Retrieve uids from all search results and store in list with search query string."""
        uid_tag = "{http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord}UID"
        tree = etree.fromstring(self.search_results.records)
        for element in tree:
            for subelement in element:
                if subelement.tag == uid_tag:
                    self.uids.append((subelement.text, self.query))

    def _get_metadata(self, query, category, crossref=False):
        """
        Retrieve metadata from all search results and store in dictionary of elements.

        Positional arguments:
        query (str) -- the initial query string for the given search results.
        category (str) -- the container in which to store the gathered metadata.
            See self.metadata_collection template in __init__.
        """
        # It seems results are returned in a totally different format depending on search client used.
        # The 'premium' client ("Search") returns XML of matching records.
        self.crossref = crossref
        if self.client == "Search":
            self.tree = etree.fromstring(self.search_results.records)
            objectify.deannotate(self.tree, cleanup_namespaces=True)
            for record in self.tree:
                self.meta_record = MetaWos(record, query)
                article_metadata = self.meta_record.compile_metadata()
                if self.citing_metadata:
                    article_metadata["source_id"] = self.uid

                self.metadata_collection[category].append(article_metadata)

        # The 'lite' client returns a list of dictionary-like objects
        elif self.client == "Lite":
            for record in self.search_results.records:
                article_metadata = dict(record)
                if self.crossref:
                    abstract = CrossRef.get_abstract(article_metadata)
                self.metadata_collection[category].append(article_metadata)

        else:
            print "Inappropriate method for metadata retrieval: {0}".format(self.client)

    def _get_metadata_citation(self, query, category):
        """
        Special metadata processing for meager results from citedReferences search.

        query (str) -- key search term that produced the results.
        category (str) -- the container in which to store the gathered metadata. See self.metadata_collection template in __init__.
        """
        for item in self.search_results.references:
            meta_record = {"docid":"",
                           "citedAuthor":"",
                           "citedTitle":"",
                           "citedWork":"",
                           "hot":"",
                           "year":""}

            if self.get_full_records and item["hot"] == "yes":
                self.hot_item = item
                self.get_full_record()

            for key in meta_record.keys():
                if key in item:
                    meta_record[key] = item[key]

                else:
                    meta_record[key] = "NONE"
                    
            meta_record["source_id"] = self.uid
            self.metadata_collection[category].append(meta_record)


    def get_full_record(self):
        """
        Run title search on 'hot' records, that is, ones with WOS ids.

        Start with most stringent search, then progressively loosen to improve likelihood of a match:
        Search 1: journal_title AND pub_year AND title
        Search 2: journal_title AND title
        Search 3: title
        """
        booleans = ["and", "near", "or", "not"]

        record_title = " ".join([w.lower().strip("?;:.,-_()[]<>{}!`'").lstrip().rstrip().replace("=", "").replace("(", "").replace(")", "").replace("[", "").replace("]", "") for w in self.hot_item["citedTitle"].split() if w.lower() not in booleans])

        if "citedWork" in self.hot_item:
            journal_title = self.hot_item["citedWork"]
        else:
            journal_title = "NONE"

        if "year" in self.hot_item:
            pub_year = self.hot_item["year"]
        else:
            pub_year = "NONE"

        self.rp_title_search = self.retrieve_parameters(count="1")
        try:
            # Search 1
            if self._run_full_record_search(record_title, pub_year=pub_year, journal_title=journal_title) >= 1:
                self.tree = etree.fromstring(self.title_search_results.records)

            # Search 2
            elif self._run_full_record_search(record_title, journal_title=journal_title) >= 1:
                self.tree = etree.fromstring(self.title_search_results.records)

            # Search 3
            else:
                self._run_full_record_search(record_title)

            self.tree = etree.fromstring(self.title_search_results.records)

            if self.search_count == 1:
                for record in self.tree:
                    
                    self.title_meta_record = MetaWos(record, record_title)
                    self.title_metadata = self.title_meta_record.compile_metadata()
                    self.title_metadata["source_id"] = self.uid
                    self.metadata_collection["hot_records"].append(self.title_metadata)

        except Exception as e:
            print "*******************ERROR*************************"
            print record_title
            print e
            print "*************************************************"

    def advanced_search(self, data, fields=["author"]):
        """
        Run search based on supplied data (containing search fields and values) and a list of terms (drawn from the data) to search on.

        args:
        data (dict) -- dictionary composed of a key (a field type to search) and value (text to search within the given field)

        kwargs:
        fields (list) -- set of fields to include in search.
        """
        field_abbrevs = {
                         "author":"AU",
                         "source":"SO",
                         "year":"PY",
        }

        return " AND ".join(["{0}={1}".format(field_abbrevs[field], data[field]) for field in fields])


    def _run_full_record_search(self, record_title, pub_year=None, journal_title=None):
        """
        Run any of 3 searches, more or less stringent, depending on parameters passed in.

        Positional arguments:
        title (str) -- only required variable, included in all searches

        Keyword arguments:
        pub_year (str) -- if present, run search 1
        journal_title (str) -- if present, run search 1 or 2
        """
        if pub_year:
            self.qp_title_search = self.query_parameters(u"TI=({0}) AND PY=({1}) AND SO=({2})".format(record_title, pub_year, journal_title), database_id="WOK")
            self.title_search_results = self.search(self.qp_title_search, self.rp_title_search, get_metadata=False)
            time.sleep(self.sleep_time)
            self.total_calls += 1
            search_count = self.search_results.recordsFound

        elif journal_title:
            self.qp_title_search = self.query_parameters(u"TI=({0}) AND SO=({1})".format(record_title, journal_title), database_id="WOK")
            self.title_search_results = self.search(self.qp_title_search, self.rp_title_search, get_metadata=False)
            time.sleep(self.sleep_time)
            self.total_calls += 1
            search_count = self.search_results.recordsFound

        else:
            self.qp_title_search = self.query_parameters(u"TI=({0})".format(record_title), database_id="WOK")
            self.title_search_results = self.search(self.qp_title_search, self.rp_title_search, get_metadata=False)
            time.sleep(self.sleep_time)
            self.total_calls += 1
            search_count = self.search_results.recordsFound

        self.search_count = search_count
        return search_count

    def _run_search(self):
        """Run search page by page until all results are retrieved."""
        self.search_results = self.search_client.service.search(self.qp, self.rp)
        if self.get_metadata and hasattr(self.search_results, "records"):
            self._get_metadata(self.query, "search_results")
        self.total_calls += 1
        time.sleep(self.sleep_time)

        self._process_results()

        if self.records_found > self.count:
            self._iterations = int(self.records_found / self.rp.count) + 1
            for i in range(1, self._iterations, 1):
                print "Getting result page {0}".format(i+1)

                self.rp = self.retrieve_parameters(first_record=1+(i)*self.count, count=self.count, 
                                                  sort_field=self.sort_field, view_field=self.view_field, option=self.option)
                self.retrieve(self.query_id, self.rp)
                if self.get_metadata:
                    self._get_metadata(self.query, "search_results")

    def _process_results(self):

        self.query_id = self.search_results.queryId
        self.records_found = self.search_results.recordsFound
        self.records_searched = self.search_results.recordsSearched
        print "Found {0} Results for {1}".format(self.records_found, self.query.encode('ascii', 'ignore'))
