from connectors.maximo_connector import MaximoConnector

def test_get_maximo_data():
    connector = MaximoConnector()
    params = {
            "oslc.where": "wonum=5001",
            "oslc.select": "wonum,description,wopriority,createdby,workorderid,status,siteid",
            "lean": 1,
            "ignorecollectionref": 1
        }
    params = {'oslc.where': 'reportdate="1998-12-31T09:00:00+00:00"', 'oslc.select': 'description,wopriority,wonum', 'lean': '1', 'ignorecollectionref': '1'}
    params = {'oslc.where': 'wonum=5000', 'oslc.select': '*', 'lean': '1', 'ignorecollectionref': '1'}
    # params= {
	# 	"oslc.where": "reportdate>=\"1998-12-31T09:00:00\" and reportdate<=\"1998-12-31T17:00:00\"",
	# 	"oslc.select": "wonum,description,reportdate",
	# 	"lean": "1",
	# 	"ignorecollectionref": "1"
	# }
    data = connector.get_workorder_details(params)
    print(data)
    breakpoint()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0
    print("Test passed! Get request successfully returned data.")


def test_update_maximo_data():
    connector = MaximoConnector()
    params = {
            "oslc.where": "wonum=5001",
            "wopriority": "1",
            "siteid": "BEDFORD",
            "lean": 1
        }
    
    data = connector.post_workorder_details(params)
    print(data)
    breakpoint()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0
    print("Test passed! Get request successfully returned data.")