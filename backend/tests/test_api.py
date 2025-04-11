from connectors.maximo_connector import MaximoConnector

def test_get_maximo_data():
    connector = MaximoConnector()
    params = {
            "oslc.where": "wonum=5012",
            "oslc.select": "wonum,description,wopriority,createdby,workorderid,status,siteid",
            "lean": 1,
            "ignorecollectionref": 1
        }
    # params = {'oslc.where': 'wonum=5012', 'oslc.select': 'description,wopriority,status', 'lean': '1', 'ignorecollectionref': '1'}
    data = connector.get_workorder_details(params)
    print(data)
    breakpoint()
    assert data is not None
    assert isinstance(data, list)
    assert len(data) > 0
    print("Test passed! Get request successfully returned data.")