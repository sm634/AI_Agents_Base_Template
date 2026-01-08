import requests
import os
from typing import Dict


class MaximoConnector():

    def __init__(self):
        
        self.url_get = os.environ['MAXIMO_GET_URL']
        self.url_post = os.environ['MAXIMO_POST_URL']
        self.apikey = os.environ['MAXIMO_APIKEY']


    def get_workorder_details(self, params: Dict):
        """
        :param: We expect the params to look like the following to for the get request.
        params = {
            "oslc.where": "wonum=5012",
            "oslc.select": "wonum,description,wopriority,createdby,workorderid,status,siteid",
            "lean": 1,
            "ignorecollectionref": 1
        }
        """
        headers = {
            "apikey": self.apikey
        }

        response = requests.get(self.url_get, headers=headers, params=params)
        if response.status_code == 200:
            payload = response.json()
            try:
                return payload['member']
            except KeyError:
                return payload
        else:
            return f"Error: {response}"


    def post_workorder_details(self, params: Dict) -> Dict:
        """
        :params: The payload will be passed on as the request body. It will
        look as the following:
        params = {
            "oslc.where": "wonum=2",
            "wopriority": "1",
            "siteid": "BEDFORD",
            "lean"=1
        }
        """

        # Headers
        headers = {
            "apikey": os.environ['MAXIMO_APIKEY'],
            "x-method-override": "PATCH",
            "patchtype": "MERGE",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Send the request
        response = requests.post(self.url_post, headers=headers, params=params)
        # Check the response
        if response.status_code in [200, 201, 204]:
            print("Workorder updated successfully.")        
            return response
        else:
            print(f"Failed to update workorder: {response.status_code}")
            print(response.text)
            return None