class MetaWosLite():
    """
    Process metadata returned from WOS queries.

    Handle metadata results from the Lite access protocol,
    in python dictionary form, which is easily derived
    from the WOS result object.

    attributes:
        metadata (dict) -- complete metadata record from Lite API.
        extracted_metadata (dict) -- collection of selected metadata
            from the metadata object.

    methods:
        get_metadata: extract metadata and store in simple Python dict.
        get_authors: one in a series of simple methods to extract a single id_type
            of information from the provided metadata object.
        ...
    """

    def __init__(self, metadata):
        """Load metadata.

        args:
            metadata (dict) -- metadata as returned from WOS Lite API; see
                lite-metadata.json for details.
        """
        self.metadata = metadata
        self.extracted_metadata = {}

    def get_metadata(self):
        """Extract selected metadata elements.

        Convenience function grabbing preselected metadata elements using
        simple methods below.

        returns:
            self.extracted_metadata (dict): data to store from WOS record. 
        """
        self.extracted_metadata["wos_authors"] = self.get_authors()
        self.extracted_metadata["wos_title"] = self.get_title()
        self.extracted_metadata.update(self.get_ids())
        self.extracted_metadata["wos_uid"] = self.get_wos_uid()
        self.extracted_metadata.update(self.get_source())
        return self.extracted_metadata

    def get_authors(self):
        """Pull authors from metadata.

        returns:
            (list): containing each author name.
        """
        return unicode(self.metadata["authors"][0]["value"])

    def get_title(self):
        """Pull title from metadata.

        returns:
            (list): containing each title (usually only 1).
        """
        return unicode(self.metadata["title"][0]["value"][0])

    def get_ids(self):
        """Pull identifiers from metadata.

        returns:
            ids (dict): containing all ids.
        """
        ids = {}
        for id_type in self.metadata["other"]:
            # ID values from WOS are integers and some of those start with 0.
            # This causes a problem for Python which interprets integers
            # beginning with 0 as 'octals.' Thus, we render as strings here.
            ids[unicode(id_type["label"])] = [unicode(i) for i in id_type["value"]]
        return ids

    def get_wos_uid(self):
        """Store official WOS id.

        returns:
            (str): WOS uid, should start with "WOS:"
        """
        return unicode(self.metadata["uid"])

    def get_source(self):
        """Pull source details from metadata.

        returns:
            source_data (dict): containing all source details, e.g. journal
                name, volume, issue, page numbers.
        """
        source_data = {}
        for s in self.metadata["source"]:
            source_data[unicode(s["label"])] = [unicode(v) for v in s["value"]]
        return source_data


