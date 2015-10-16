import os
import codecs

class OhlroggeSearch():
    """Use specifically formatted bibliographic data to build a search for WOS.

    Responding to the specific formatting of data provided by Prof. Ohlrogge,
    extract data and store in format amenable to search in Wos class.

    methods:
        make_search_list: build list of search strings ready to use in WOS queries.
        make_search_dict: create list of searches stored as key:value pairs.

    """

    def __init__(self, tsv_location):
        """Initialize with location of tsv file for processing.

        args:
            tsv_location(str) -- file to open and process.
        """

        self.tsv_location = tsv_location
        self.__check_file()

        self.field_indices = {
                              "author":2,
                              "year":1,
                              "id":0,
                              "source":3,
                              "volume":5,
                              "page":6,
                              "result_count":7,
                              "plant_count":8,
                              }


    def make_search_list(self):
        """Read file to build WOS-formatted list of searches."""
        self.searches = []
        with codecs.open(self.tsv_location, "r", "latin-1") as tsv:
            # Store first line of file as headings.
            self.headings = tsv.readline()
            for line in tsv:
                self.__extract_search_terms(line)
                self.searches.append(self._build_query())

    def make_search_dict(self):
        """
        Extract data according to its position in the tab-delimited line, 
        and add to a list of dictionary of search objects.
        """
        self.search_terms = []
        i=0
        with codecs.open(self.tsv_location, "r", "latin-1") as tsv:
            for line in tsv:
                i+=1
                self.__extract_search_terms(line)
                self.search_components["query"] = self._build_query()
                self.search_terms.append(self.search_components)
        print "Extracted {0} lines".format(i)


    def __extract_search_terms(self, line):
        """
        Extract data according to its position in the tab-delimited line, and store in a list of search queries.

        args:
        line(str) -- one line of data containing tab-separated values.
        """

        self.search_components = {}

        """
        TODO: Use zip to automatically make a dict object out of each row of a TSV.

        search_components_by_heading = zip(self.headings, line.split("\t"))
        self.search_components.update(search_components_by_heading)
        """

        line_values = line.split("\t")

        # Use field_indices table above to get the appropriate index for each
        # type of data, e.g. in the list line_values, the correct index for
        # "author" should be stored in self.field_indices["author"].
        self.__get_year(line_values[self.field_indices["year"]])
        self.__get_author(line_values[self.field_indices["author"]])
        self.__get_source(line_values[self.field_indices["source"]])
        self.__get_volume(line_values[self.field_indices["volume"]])
        self.__get_page(line_values[self.field_indices["page"]])          
        self.__get_id(line_values[self.field_indices["id"]])  
        self.__get_field("result_count")
        self.__get_field("plant_count")   

    def __get_id(self, value):
        """
        Extract year from raw 'value'

        args:
            value(str) -- data from row generated in __extract_search_terms.
        """
        self.search_components["id"] = value


    def __get_year(self, value):
        """
        Extract year from raw 'value'

        args:
            value(str) -- data from row generated in __extract_search_terms.
        """
        if value.strip():
            self.search_components["year"] = value
        else:
            self.search_components["year"] = "9999"


    def __get_author(self, value):
        """
        Extract author(s) from raw value. Because of variation in formatting of initials, we will attempt to gather only author last names.

        args:
            value(str) -- data from row generated in __extract_search_terms.
        """
        # Remove extraneous punctuation from author field.
        clean_value = value.strip().replace(",", "").replace(";", "").replace(".", "***").replace("et al", "").replace('"', '')
        author_last_names = [name.replace("***", "") for name in clean_value.split() if len(name) > 2 and "***" not in name or len(name) > 10]
        self.search_components["author"] = u"({0})".format(" AND ".join(author_last_names))

    def __get_source(self, value):
        """
        Extract source title from raw value.

        args:
            value(str) -- data from row generated in __extract_search_terms.
        """
        # Replace '.' with '*' to allow for wildcard searching.
        self.search_components["source"] = u"({0})".format(" ".join([word.replace(".", "*") for word in value.split()]))

    def __get_volume(self, value):
        """
        Extract volume from raw 'value'

        args:
            value(str) -- data from row generated in __extract_search_terms.
        """
        self.search_components["volume"] = value.strip()

    def __get_page(self, value):
        """
        Extract page from raw 'value'

        args:
            value(str) -- data from row generated in __extract_search_terms.
        """
        self.search_components["page"] = value.strip()

    def _build_query(self):
        """Take created search components and merge them into 1 search string.

        This particular query structure applies principally to the Ohlrogge dataset.

        Returns:
            Search query string formatted to be included in WOS query parameters.
        """
        author_search = u"AU=" + self.search_components["author"]
        if self.search_components["year"] == "9999":
            year_search = None
        else:
            year_search = u"PY=" + self.search_components["year"]
        source_search = u"SO=" + self.search_components["source"]
        return u" AND ".join([s for s in [author_search, year_search, source_search] if s is not None])

    def __get_field(self, field):
        """Generic get field function.

        args:
            field(str): data to be added.
        """
        self.search_components[field] = self.field_indices[field]

    def __check_file(self):
        """Check if file exists."""
        if not os.path.exists(self.tsv_location):
            print "File does not exist: {0}".format(self.tsv_location)

        else:
            print "File loaded."