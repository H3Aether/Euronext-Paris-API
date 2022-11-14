import os
import requests
import json

URL = "https://live.euronext.com/en/pd_es/data/stocks"
FILTER = os.path.join(os.path.dirname(__file__), "filter.json")

def format_stock_list(response):
    """ Format the response so it no longer contains HTML and useless data """
    formatted_response = { "number" : response["iTotalRecords"],
                           "companies" : [] }
    
    for entry in response["aaData"]:
        stock_name = entry[1].split(">")[1][:-3] # Remove the HTML tags
        stock_market = entry[1].split("-")[1][:4] # The market is in the url, after the dash. It is always 4 characters long
        company = { "name" : stock_name.upper(),
                  "isin" : entry[2],
                  "symbol" : entry[3],
                  "market" : stock_market }
        formatted_response["companies"].append(company)
    
    return formatted_response


def get():
    with open(FILTER) as f:
        filter = json.load(f)
        r = requests.post(URL, data=filter)

    # The response r is the list of all the stocks
    response = r.json()
    response = format_stock_list(response)

    return response
