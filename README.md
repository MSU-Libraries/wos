
## Web of Science API
This code is designed to interact with the WOS API using "premium" or "lite" access protocols.

-    `wos.py` contains code for interacting with the API directly.
-    `woscalls.py` includes calls made to the `WOS` class
-    `metawos.py` can be used to extract metadata from search results.
-    `buildsearch.py` builds search strings from data supplied in a certain style of tsv file.

### Dependencies

-    [lxml](http://lxml.de/) for xml parsing
-    [suds](https://fedorahosted.org/suds/wiki/Documentation) for SOAP API interaction.

### The API Class

It's possible to work with the API class, `WOS`, directly using syntax like the following:


    from wos import Wos
    wos = Wos(client="Lite")

This will initiate the search client but not yet run any API calls. There are two options for the "client" keyword argument: "Search" and "Lite". The Lite API should be available to all institutions that subscribe to at least the Web of Knowledge Core Collection. Contact your representative to have access opened to your IP address, if it isn't already. [More details here](http://wokinfo.com/products_tools/products/related/webservices/). The Lite API provides basic search and basic metadata retrieval functionality, but _not_ citation retrieval.

The "Search" client is an available at an additional cost, and does provide access to both forward and backward citation data. Access is available on a project basis, or as a yearly subscription. I would recommend first requesting a trial period to work with the API.


    wos.authorize()

    Search client authorized.


The `authorize` function attempts to authenticate based on IP address. If successful, an authorization token will be attached to all future requests in the session. 


    wos.query_parameters('AU=(Peiretti AND Palmegiano) AND SO=(Animal Feed Science and Technology) AND PY=2004', database_id="WOK")




    (queryParameters){
       databaseId = "WOK"
       userQuery = "AU=(Peiretti AND Palmegiano) AND SO=(Animal Feed Science and Technology) AND PY=2004"
       editions[] = <empty>
       symbolicTimeSpan = None
       timeSpan = 
          (timeSpan){
             begin = "1900-01-01"
             end = "2015-10-01"
          }
       queryLanguage = "en"
     }



First establish the `query_parameters` object, which should include a query string along with, optionally, a set of parameters. Details on the structure of the query can be found in the API documentation (which can be requested from ThomsonReutuers, but which I'm also making available [here](https://www.msu.edu/~higgi135/WebServicesLiteguide.pdf) (in possibly an outdated version).  

Parameters can be provided as the following keyword arguments:

- **time_begin (str)** -- date in YYYY-MM-DD format.
- **time_end (str)** -- date in YYYY-MM-DD format.
- **database_id (str)** -- from the WOS set of database abbreviations. "WOS" correpsonds to the WOS core collection.
- **query_language (str)** -- "en" the only currently allowed value.
- **symbolic_timespan (str)** -- a human-readable timespan, e.g. "4weeks", must be null if time_begin and time_end used.
- **editions (list)** -- TODO list of sub-components of the selected database to use.


    wos.retrieve_parameters()




    (retrieveParameters){
       firstRecord = 1
       count = 100
       sortField[] = <empty>
     }



The `retrieve_parameters` allow for some control of the data that is returned.  

- **first_record (int)** -- The number of the first record to return in the search.
- **count (int)** -- Number of records to return (maximum 100).
- **sort_field (list)** -- TODO Field to sort by (should be WOS field abbreviation).


    wos.search(wos.qp, wos.rp)

    Found 1 Results for AU=(Peiretti AND Palmegiano) AND SO=(Animal Feed Science and Technology) AND PY=2004





    (searchResults){
       queryId = "1"
       recordsFound = 1
       recordsSearched = 198371943
       records[] = 
          (liteRecord){
             uid = "WOS:000224567700011"
             title[] = 
                (labelValuesPair){
                   label = "Title"
                   value[] = 
                      "Chemical composition, organic matter digestibility and fatty acid content of evening primrose (Oenothera paradoxa) during its growth cycle",
                },
             source[] = 
                (labelValuesPair){
                   label = "Issue"
                   value[] = 
                      "3-4",
                },
                (labelValuesPair){
                   label = "Pages"
                   value[] = 
                      "293-299",
                },
                (labelValuesPair){
                   label = "Published.BiblioDate"
                   value[] = 
                      "OCT 15",
                },
                (labelValuesPair){
                   label = "Published.BiblioYear"
                   value[] = 
                      "2004",
                },
                (labelValuesPair){
                   label = "SourceTitle"
                   value[] = 
                      "ANIMAL FEED SCIENCE AND TECHNOLOGY",
                },
                (labelValuesPair){
                   label = "Volume"
                   value[] = 
                      "116",
                },
             authors[] = 
                (labelValuesPair){
                   label = "Authors"
                   value[] = 
                      "Peiretti, PG",
                      "Palmegiano, GB",
                      "Masoero, G",
                },
             keywords[] = 
                (labelValuesPair){
                   label = "Keywords"
                   value[] = 
                      "lipids",
                      "forage",
                      "foodstuffs",
                      "ruminant",
                      "nutrition",
                },
             other[] = 
                (labelValuesPair){
                   label = "Contributor.ResearcherID.Names"
                   value[] = 
                      "Peiretti, Pier Giorgio",
                      "Peiretti, Pier Giorgio",
                },
                (labelValuesPair){
                   label = "Contributor.ResearcherID.ResearcherIDs"
                   value[] = 
                      "B-6871-2013",
                      None,
                },
                (labelValuesPair){
                   label = "Identifier.Doi"
                   value[] = 
                      "10.1016/j.anifeedsci.2004.07.001",
                },
                (labelValuesPair){
                   label = "Identifier.Ids"
                   value[] = 
                      "863ND",
                },
                (labelValuesPair){
                   label = "Identifier.Issn"
                   value[] = 
                      "0377-8401",
                },
                (labelValuesPair){
                   label = "Identifier.Xref_Doi"
                   value[] = 
                      "10.1016/j.anifeedsci.2004.07.001",
                },
                (labelValuesPair){
                   label = "ResearcherID.Disclaimer"
                   value[] = 
                      "ResearcherID data provided by Thomson Reuters",
                },
          },
     }



Run the search by calling the `search` function with the query parameters and retrieve parameters objects as arguments (`wos.qp` and `wos.rp` respectively). 

Results can be found in the `wos.search_results.records` object, if any results were returned. More generally, `wos.search_results` can be used to find info about the response, including number of results.  

Additional methods can be used to get cited references as well as citing articles if the "Search" client is used.


    from wos import Wos
    wos = Wos(client="Lite")
    wos.authorize()
    wos.query_parameters('AU=(Peiretti AND Palmegiano) AND SO=(Animal Feed Science and Technology) AND PY=2004', database_id="WOK")
    wos.retrieve_parameters(view_field=["title", "name"])
    wos.search(wos.qp, wos.rp)

The above code should return 1 result and can be used as a test to ensure code is working properly.

### Automating Searches

The `WosCalls` class provides a means of interacting with the API 1 level up. That is, lists of search strings or sets of search parameters can be provided to run in batch. This functionality is still very much work in progress.


    from woscalls import WosCalls
    wosc = WosCalls(search_queries=bs.searches, database_id="WOK")
    wosc.get_all_search_results()

    Search client authorized.
    Found 1 Results for AU=(Lambertsen) AND PY=1966 AND SO=(Acta Agric* Scand*)
    Found 1 Results for AU=(Bentes) AND PY=1986 AND SO=(Acta Amazonica)
    Found 1 Results for AU=(Maia) AND PY=1978 AND SO=(Acta Amazonica)
    Found 0 Results for AU=(Loth) AND PY=1991 AND SO=(Agrochimica)
    Found 1 Results for AU=(Jellum AND Powell) AND PY=1971 AND SO=(Agron* J*)
    Found 5 Results for AU=(Bertoni) AND PY=1994 AND SO=(An* Asoc* Quim* Argent*)
    Found 0 Results for AU=(Balnchini) AND PY=1981 AND SO=(Anal* Chem*)
    Found 1 Results for AU=(Peiretti AND Palmegiano AND Masoero) AND PY=2004 AND SO=(Animal Feed Science and Technology)
    Found 0 Results for AU=(Adhikari) AND PY=1991 AND SO=(Bangladesh J* Sci* Ind* Res*)
    Found 0 Results for AU=(Serrano AND Guzm?n) AND PY=1994 AND SO=(Biochem* Systemat* Ecology)
    Process complete.
    Returned 10 records


The `WosCalls` class is additionally a place to house content-specific methods build on `Wos`. See `run_phylo_process` method as it develops.

### Additional Information

The `BuildSearch` class is currently quite content specific but could in principle be broadened to allow for automatically generating searches from data in other formats, such as CSV or JSON. Currently the algorithm below assumes a very specific data structure to work.


    from buildsearch import BuildSearch
    bs = BuildSearch("data/ohlrogge/ohlrogge_test_10.txt")
    bs.make_search_list() # from here the object bs.searches can be used in WosCalls()

    File loaded.



    bs.searches




    [u'AU=(Lambertsen) AND PY=1966 AND SO=(Acta Agric* Scand*)',
     u'AU=(Bentes) AND PY=1986 AND SO=(Acta Amazonica)',
     u'AU=(Maia) AND PY=1978 AND SO=(Acta Amazonica)',
     u'AU=(Loth) AND PY=1991 AND SO=(Agrochimica)',
     u'AU=(Jellum AND Powell) AND PY=1971 AND SO=(Agron* J*)',
     u'AU=(Bertoni) AND PY=1994 AND SO=(An* Asoc* Quim* Argent*)',
     u'AU=(Balnchini) AND PY=1981 AND SO=(Anal* Chem*)',
     u'AU=(Peiretti AND Palmegiano AND Masoero) AND PY=2004 AND SO=(Animal Feed Science and Technology)',
     u'AU=(Adhikari) AND PY=1991 AND SO=(Bangladesh J* Sci* Ind* Res*)',
     u'AU=(Serrano AND Guzm?n) AND PY=1994 AND SO=(Biochem* Systemat* Ecology)']



The `bs.searches` object contains a list of searches, suitable to pass as an argument in the `WosCalls` class.

#### Get in touch!

If I can be of help in using this code, or if you have suggestions for improvement, please do contact me.


    
