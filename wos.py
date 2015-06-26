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

from suds.client import Client
from suds.transport.http import HttpTransport
from datetime import date
import urllib2

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
        else: 
            self.search_client = Client(self.search_lite_url, transport=http)

    def PrintWsdl(self):
        if self.search_client:
            print self.search_client
        else:
            print "Search client not established"

    def Search(self, qp, rp):
        self.search_results = self.search_client.service.search(qp, rp)
        self.query_id = self.search_results.queryId
        self.records_returned = self.search_results.records
        self.records_found = self.search_results.recordsFound
        self.records_searched = self.search_results.recordsSearched
        self.uids = [i.uid for i in self.search_results.records]
        self._MakeDict()
        return self.search_results

    def QueryParameters(self, query, time_begin="1900-01-01", time_end=None, database_id="WOS", query_language="en", symbolic_timespan=None, editions=None):
        self.qp = self.search_client.factory.create("queryParameters")
        self.qp.userQuery = query
        if symbolic_timespan is None:
            self.qp.timeSpan = self._TimeSpan(time_begin, time_end)
        else:
            self.qp.symbolicTimeSpan = self.symbolic_timespan
        self.qp.databaseId = database_id
        self.qp.queryLanguage = query_language
        return self.qp

    def _MakeDict(self):
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
        self.rp = self.search_client.factory.create("retrieveParameters")
        self.rp.firstRecord = first_record
        self.rp.count = count
        return self.rp

    def RetrieveById(self, uid, rp, query_language="en", database_id="WOS"):
        self.item = self.search_client.service.retrieveById(database_id, uid, query_language, rp)
        return self.item



