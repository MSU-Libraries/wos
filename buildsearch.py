import os
import codecs

class BuildSearch():
    """Use specifically formatted bibliographic data to build a search for WOS."""

    def __init__(self, tsv_location):
        """
        Initialize with location of tsv file for processing.

        args:
        tsv_location(str) -- file to open and process
        """

        self.tsv_location = tsv_location
        self.__check_file()

    def make_search_list(self):
        """Read file to build WOS-formatted list of searches."""
        self.searches = []
        with codecs.open(self.tsv_location, "r", "utf-8") as tsv:
            for line in tsv:
                self.extract_search_terms(line)
                self._build_query()

    def make_search_dict(self):
        """
        Extract data according to its position in the tab-delimited line, and store as a dictionary of search objects.

        args:
        line(str) -- one line of data containing tab-separated values.
        """
        self.search_terms = []
        with codecs.open(self.tsv_location, "r", "utf-8") as tsv:
            for line in tsv:
                self.extract_search_terms(line)
                self.searches.append(self.search_components)


    def extract_search_terms(self, line):
        """
        Extract data according to its position in the tab-delimited line, and store in a list of search queries.

        args:
        line(str) -- one line of data containing tab-separated values.
        """
        self.search_components = {}
        line_values = line.split("\t")
        # Published year value should be found in first column.
        self._get_year(line_values[0])
        # Author values should be found in second column.
        self._get_author(line_values[1])
        # Source title should be found in third column.
        self._get_source(line_values[2])
        # Volume values should be found in fourth column.
        self._get_volume(line_values[3])
        # Source title should be found in fifth column.
        self._get_page(line_values[4])          


    def _get_year(self, value):
        """
        Extract year from raw 'value'

        args:
        value(str) -- column 1 value for current line.
        """
        self.search_components["year"] = value

    def _get_author(self, value):
        """
        Extract author(s) from raw value. Because of variation in formatting of initials, we will attempt to gather only author last names.

        args:
        value(str) -- column 2 value for current line.
        """
        clean_value = value.strip().replace(",", "").replace(";", "").replace(".", "***").replace("et al", "").replace('"', '')
        author_last_names = [name for name in clean_value.split() if len(name) > 2 and "***" not in name]
        self.search_components["author"] = "({0})".format(" AND ".join(author_last_names))

    def _get_source(self, value):
        """
        Extract source title from raw value.

        args(str) -- column 3 value for current line.
        """
        # Replace '.' with '*' to allow for 
        self.search_components["source"] = "({0})".format(" ".join([word.replace(".", "*") for word in value.split()]))

    def _get_volume(self, value):
        """
        Extract volume from raw 'value'

        args:
        value(str) -- column 4 value for current line.
        """
        self.search_components["volume"] = value.strip()

    def _get_page(self, value):
        """
        Extract page from raw 'value'

        args:
        value(str) -- column 5 value for current line.
        """
        self.search_components["page"] = value.strip()

    def _build_query(self):
        """Take created search components and merge them into 1 search string."""
        author_search = "AU=" + self.search_components["author"]
        year_search = "PY=" + self.search_components["year"]
        source_search = "SO=" + self.search_components["source"]
        self.searches.append(" AND ".join([author_search, year_search, source_search]))


    def __check_file(self):
        """Check if file exists."""
        if not os.path.exists(self.tsv_location):
            print "File does not exist: {0}".format(tsv_location)

        else:
            print "File loaded."