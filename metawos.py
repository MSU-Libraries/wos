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

class MetaWos():
    """Process individual records of WOS metadata"""

    def __init__(self, record, query):
        """Establish record."""
        self.record = record
        self.query = query
        self.xpaths = {
                       "accession_number": "UID",
                       "authors": "static_data/summary/names/name[@role='author']/full_name",
                       "title": "static_data/summary/titles/title[@type='item']",
                       "publication_name": "static_data/summary/titles/title[@type='source']",
                       "date": "static_data/summary/pub_info",
                       "abstract": "static_data/fullrecord_metadata/abstracts/abstract/abstract_text/p",
                       "doi": "dynamic_data/cluster_related/identifiers/identifier",
                       "author_address": "static_data/fullrecord_metadata/addresses/address_name/address_spec/full_address",
                       "keywords": "static_data/fullrecord_metadata/keywords/keyword",
                       "keywords_plus": "static_data/item/keywords_plus/keyword",
                       "funding_agency": "static_data/fullrecord_metadata/fund_ack/grants/grant/grant_agency",
                       "grant_id": "static_data/fullrecord_metadata/fund_ack/grants/grant/grant_ids/grant_id",
                       "times_cited": "dynamic_data/citation_related/tc_list/silo_tc",
                       "citation_count": "static_data/fullrecord_metadata/refs",
        }


    def compile_metadata(self, include_connected_uid=False, metadata_elements=["accession_number", "authors", "title", "publication_name", "date", "abstract", "doi", "author_address", 
                                                                               "keywords", "keywords_plus", "funding_agency", "grant_id", "times_cited", "citation_count"]):
        """
        Take list of desired metadata elements and compile into dictionary.

        Keyword arguments:
        metadata_elements (list) -- list of controlled metadata elements to access.
        """
        self.metadata = {"query": self.query}

        for element in metadata_elements:
            self.element = element
            self.get_data(self.xpaths[element])
            #print self.element, self.data
            self.metadata[element] = "; ".join(self.data)

        return self.metadata

    def get_data(self, xpath):

        self.data = []
        self.data_source = self.record.findall("{http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord}"+xpath.replace("/", "/{http://scientific.thomsonreuters.com/schema/wok5.4/public/FullRecord}"))
        if self.data_source <> [None]:
            self._parse_result() 

        else:
            self.data = ["NONE"]

    def _parse_result(self):
        """Get element value and store."""
        for d in self.data_source:
            if self.element == "date":
                #print d.attrib
                value = d.get("pubyear")
            elif self.element == "times_cited":
                value = d.get("local_count")
            elif self.element == "citation_count":
                value = d.get("count")
            elif self.element == "doi":
                id_result = self._get_doi(d)
                if id_result:
                    value = id_result
                else:
                    value = None
            else:
                value = d.text

            if value is not None:
                self.data.append(value.replace("\t", ""))

        if not self.data:
            self.data.append("NONE")



    def _get_doi(self, element):
        """
        Check if ID is DOI and get value if so.

        Positional arguments:
        element (lxml element) -- ID element to evaluate.
        """
        id_type = element.get("type")
        if id_type == "doi" or id_type == "xref_doi":
          
            return element.get("value")

        else:

            return 

