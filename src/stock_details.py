import requests
from bs4 import BeautifulSoup

def get(isin, market):
    try:
        url = f"https://live.euronext.com/intraday_chart/getChartData/{isin}-{market}/intraday" # Create the URL using the isin
        r = requests.get(url).json()[-1] # Gets the list of recent infos and extract the last one
    except: # If it fails, raise an exception
        raise Exception(f"Could not get the stock details for {isin} on market {market}")
        

    price = float(r['price']) # Get the price and convert it to float

    url = f"https://live.euronext.com/en/intraday_chart/getDetailedQuoteAjax/{isin}-{market}/full" # Create another URL using the isin
    r = requests.get(url).text # Get the HTML code of the page
    soup = BeautifulSoup(r, 'html.parser') # Parse the html

    # Finding the updated time.
    update_date = soup.find('a', class_="text-white").find('span').text[8:] # The date is inside the <a> with class "text-white", inside the <span>. The date starts at the 8th character.

    # Gathering the data from the table
    rows = soup.find_all('tr') # Get all the <tr> rows in an array
    currency = rows[0].find_all('td')[1].text.replace("\n", "").replace("\t", "").replace(" ", "")
    volume = int(rows[1].find_all('td')[1].text.replace(",", ""))
    volume_date = rows[1].find_all('td')[2].text[1:-1]
    turnover = int(rows[2].find_all('td')[1].text.replace(",", ""))
    transactions = int(rows[3].find_all('td')[1].text.replace(",", ""))
    vwap = float(rows[4].find_all('td')[1].text.replace(",", ""))
    open = float(rows[5].find_all('td')[1].text.replace(",", ""))
    high = float(rows[6].find_all('td')[1].text.replace(",", ""))
    high_time = rows[6].find_all('td')[2].text[2:-2]
    low = float(rows[7].find_all('td')[1].text.replace(",", ""))
    low_time = rows[7].find_all('td')[2].text[2:-2]
    threshold = [ float(rows[8].find_all('td')[1].find_all('span')[0].text.replace(",", "")), float(rows[8].find_all('td')[1].find_all('span')[1].text.replace(",", "")) ]
    previous_close = float(rows[9].find_all('td')[1].text.replace(",", ""))
    previous_close_date = rows[9].find_all('td')[2].text[1:-1]
    week_52 = [ float(rows[10].find_all('td')[1].find_all('span')[0].text.replace(",", "")), float(rows[10].find_all('td')[1].find_all('span')[1].text.replace(",", "")) ]
    market_cap = rows[11].find_all('td')[1].text[1:-1]

    # Creating the dictionary
    stock_details = {   "price" : price,
                        "currency" : currency,
                        "volume" : { "value" : volume, "date" : volume_date },
                        "turnover" : turnover,
                        "transactions" : transactions,
                        "vwap" : vwap,
                        "open" : open,
                        "high" : { "price" : high, "time" : high_time },
                        "low" : { "price" : low, "time" : low_time },
                        "threshold" : threshold,
                        "previous_close" : { "price" : previous_close, "date" : previous_close_date },
                        "52_week" : week_52,
                        "market_cap" : market_cap,
                        "update_date" : update_date }

    return stock_details



def getChart(isin, market, period):
    """ Gets the chart data for a stock, on a given period.
    Period can either be intraday or max. """
    try:
        url = f"https://live.euronext.com/intraday_chart/getChartData/{isin}-{market}/{period}" # Create the URL using the isin, market, and period
        r = requests.get(url).json() # Gets the list of recent infos and extract the last one
    except: # If it fails, raise an exception
        raise Exception(f"Could not get the stock details for {isin} on market {market} for the period {period}")
    
    return r