import requests
import json

URL = "https://live.euronext.com/en/pd_es/data/stocks"
OUTPUT = "euronext_paris_stocks.json"

def format_stock_list(response):
    """ Format the response so it no longer contains HTML and useless data """
    formatted_response = { "number" : response["iTotalRecords"],
                           "stocks" : [] }
    
    for entry in response["aaData"]:
        stock_name = entry[1].split(">")[1][:-3] # Remove the HTML tags
        stock = { "name" : stock_name,
                  "isin" : entry[2],
                  "symbol" : entry[3] }
        formatted_response["stocks"].append(stock)
    
    return formatted_response


def get_stock_list():
    with open("filter.json") as f:
        filter = json.load(f)
        r = requests.post(URL, data=filter)

    # The response is the list of all the stocks
    # Save the response to a file in utf-8 encoding
    response = r.json()
    response = format_stock_list(response)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(response, f)

get_stock_list()