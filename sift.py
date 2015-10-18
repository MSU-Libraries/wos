class SiftSearchResults():
    """Sort out exact matches from WOS Lite metadata."""

    def __init__(self, original_metadata, wos_metadata):
        """Establish metadata objects for comparison.

        args:
            original_metadata (dict): data used to formulate searches.
            wos_metadata (dict): data returned from WOS searches.
        """
        self.original_metadata = original_metadata
        self.wos_metadata = wos_metadata

    def assess_match(self):
        """Check source data for match to WOS data.

        returns:
            (str): assessment of likelihood two records match.
        """
        print "----Comparing {0}".format(self.wos_metadata["wos_title"])
        vol_match = False
        page_match = False
        if "Volume" in self.wos_metadata:
            vol_match = self.check_volume() 
        #issue_match = self.check_issue()

        if "Pages" in self.wos_metadata:
            page_match = self.check_page()

        if all([vol_match, page_match]):
            return "exact_match"

        elif vol_match or page_match:
            return "probable_match"

        else:
            return "no verifiable match"

    def check_volume(self):
        """Check it issue from data sources match."""
        return self.original_metadata["volume"] == self.wos_metadata["Volume"][0]

    def check_issue(self):
        """Check it issue from data sources match."""
        return self.original_metadata["issue"] == self.wos_metadata["Issue"][0]

    def check_page(self):
        """Check it issue from data sources match."""
        page_part_match = any([page in self.wos_metadata["Pages"][0].split("-") for page in self.original_metadata["page"].split("-")])
        return self.original_metadata["page"] == self.wos_metadata["Pages"][0] or page_part_match



