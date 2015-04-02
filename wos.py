from __future__ import division
from suds.client import Client
from suds.transport.http import HttpTransport
from datetime import date
from lxml import etree
import urllib2
import time

searches = ['TS=(perennial NEAR/1 wheat)', 
            'TS=(perennial NEAR/1 grain)', 
            'TS=(perennial NEAR/1 triticum)', 
            'TS=(perennial NEAR/1 rye NOT "rye grass" NOT ryegrass NOT rye-grass)',
            'TS=(perennial NEAR/1 secale)',
            'TS=(perennial NEAR/1 "pigeon pea" OR perennial NEAR/1 pigeonpea)',
            'TS=(perennial NEAR/1 cajanus)', 
            'TS=(perennial NEAR/1 rice)',
            'TS=(perennial NEAR/1 oryza)',
            'TS=(perennial NEAR/1 sorghum)',
            'TS=(perennial NEAR/1 cassava)',
            'TS=(perennial NEAR/1 manihot)']

class Wos():
    def __init__(self, client="Search"):
        self.client = client
        self.auth_url = "http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl"
        self.search_lite_url = "http://search.webofknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl"
        self.search_url = "http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl"
        self.auth_client = None
        self.search_client = None
        self.qp = None
        self.rp = None
        self.uids = []

    def Authorize(self):
        auth_client = Client(self.auth_url)
        try:
            self.sid_token = auth_client.service.authenticate()
            self._AddSid()
            
        except Exception as e:
            print "Authentication failed."
            print e

    def _AddSid(self):
        #Create URL opener with token as header
        opener = urllib2.build_opener()
        opener.addheaders = [('Cookie', 'SID="'+self.sid_token+'"')]
        http = HttpTransport()
        http.urlopener = opener
        self._EstablishSearchClient(http)

    def _EstablishSearchClient(self, http):
        if self.client == "Search":
            self.search_client = Client(self.search_url, transport=http)
        elif self.client == "Lite": 
            self.search_client = Client(self.search_lite_url, transport=http)
        else:
            print "Invalid search client"

    def PrintWsdl(self):
        if self.search_client:
            print self.search_client
        else:
            print "Search client not established"

    def Search(self, qp, rp):
        self.qp = qp
        self.rp = rp
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

    def QueryParameters(self, query, time_begin="1900-01-01", time_end=None, database_id="WOS", query_language="en", symbolic_timespan=None, editions=None):
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
            self.qp.timeSpan = self._TimeSpan(time_begin, time_end)
        else:
            self.qp.symbolicTimeSpan = self.symbolic_timespan
        
        self.qp.databaseId = database_id
        self.qp.queryLanguage = query_language
        
        return self.qp

    def _get_uids(self):
        pass

    def _TimeSpan(self, time_begin, time_end):
        timespan = self.search_client.factory.create("timeSpan")
        timespan.begin = time_begin
        if time_end is not None:
            timespan.end = time_end
        else:
            d = date.today()
            timespan.end = d.isoformat()
        return timespan

    def RetrieveParameters(self, first_record=1, count=100, sort_field=None, view_field=None, option=None):
        self.first_record = 1
        self.count = count
        self.sort_field = sort_field
        self.view_field = view_field
        self.option = option

        self.rp = self.search_client.factory.create("retrieveParameters")
        self.rp.firstRecord = first_record
        self.rp.count = count
        
        return self.rp

    def RetrieveById(self, uid, rp, query_language="en", database_id="WOS"):
        self.item = self.search_client.service.retrieveById(database_id, uid, query_language, rp)
        return self.item

    def Retrieve(self, query_id, rp):
        self.search_results = self.search_client.service.retrieve(query_id, rp)
        time.sleep(0.5)

    def _get_uids(self):
        uid_tag = "{http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord}UID"
        tree = etree.fromstring(self.search_results.records)
        for element in tree:
            for subelement in element:
                if subelement.tag == uid_tag:
                    self.uids.append(subelement.text)

    def _run_search(self):

        self.search_results = self.search_client.service.search(self.qp, self.rp)
        time.sleep(0.5)
        self.query_id = self.search_results.queryId
        self.records_returned = self.search_results.records
        self.records_found = self.search_results.recordsFound
        self.records_searched = self.search_results.recordsSearched
        self._get_uids()
        self._iterations = int(self.records_found / self.rp.count) + 1
        for i in range(1, self._iterations, 1):
            print "Getting result page {0}".format(i)

            self.rp = self.RetrieveParameters(first_record=self.first_record+i*self.count, count=self.count, 
                                              sort_field=self.sort_field, view_field=self.view_field, option=self.option)
            self.Retrieve(self.query_id, self.rp)
            self._get_uids()



