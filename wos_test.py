from wos import Wos
a = Wos(client="Lite")
a.Authorize()
qp = a.QueryParameters("TS=grain")
rp = a.RetrieveParameters()
results = a.Search(qp, rp)
uids = a.uids

for uid in uids:
    a.RetrieveById(uid, rp)
    
