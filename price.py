from stock_info import *
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup
from time import time

session = HTMLSession()

URL = "https://live.euronext.com/en/product/equities/"

def get_stock_details_from_loaded_page(r):
    price = r.html.find('#header-instrument-price', first=True) # Find the price
    price = float(price.text.replace(",", "")) # Remove the comma and convert to float

    table = r.html.find('#detailed-quote', first=True) # Find the table with the details
    table = table.find('.table-responsive', first=True) # Get sub div with class table-responsive

    # Finding the updated time
    date_div = table.find('.icons__wrapper', first=True)
    date = date_div.find('span', first=True).text[8:]

    # Gathering the data
    table = table.find('tr')

    currency = table[0].find('td')[1].text
    volume = int(table[1].find('td')[1].text.replace(",", ""))
    volume_date = table[1].find('td')[2].text[1:-1]
    turnover = int(table[2].find('td')[1].text.replace(",", ""))
    transactions = int(table[3].find('td')[1].text.replace(",", ""))
    vwap = float(table[4].find('td')[1].text.replace(",", ""))
    open = float(table[5].find('td')[1].text.replace(",", ""))
    high = float(table[6].find('td')[1].text.replace(",", ""))
    high_time = table[6].find('td')[2].text[1:-1]
    low = float(table[7].find('td')[1].text.replace(",", ""))
    low_time = table[7].find('td')[2].text[1:-1]
    threshold = [ float(table[8].find('td')[1].find('span')[0].text.replace(",", "")), float(table[8].find('td')[1].find('span')[1].text.replace(",", "")) ]
    previous_close = float(table[9].find('td')[1].text.replace(",", ""))
    previous_close_date = table[9].find('td')[2].text[1:-1]
    week_52 = [ float(table[10].find('td')[1].find('span')[0].text.replace(",", "")), float(table[10].find('td')[1].find('span')[1].text.replace(",", "")) ]
    market_cap = table[11].find('td')[1].text

    # Creating the dictionary
    stock_details = {   "stock" : stock,
                        "price" : price,
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
                        "update_date" : date }

    return stock_details


def get_stock_details(stock):
    stock_url = URL + stock['isin'] + "-" + "XPAR" # Create the URL
    r = session.get(stock_url) # Get the page
    r.html.render(sleep=1)

    stock_details = get_stock_details_from_loaded_page(r)
    return stock_details


def get_stock_details_fast(stock):
    url = f"https://live.euronext.com/intraday_chart/getChartData/{stock['isin']}-XPAR/intraday" # Create the URL using the isin
    last_price_info = requests.get(url).json()[-1] # Gets the list of recent info and extract the last one
    price = float(last_price_info['price']) # Get the price and convert it to float

    url = f"https://live.euronext.com/en/intraday_chart/getDetailedQuoteAjax/{stock['isin']}-XPAR/full"
    table = requests.get(url).text
    soup = BeautifulSoup(table, 'html.parser') # Parse the html

    # Finding the updated time.
    update_date = soup.find('a', class_="text-white").find('span').text[8:] # The date is inside the <a> with class "text-white", inside the <span>. The date starts at the 8th character.

    # Gathering the data from the table
    rows = soup.find_all('tr') # Get all the <tr> rows in an array

    currency = rows[0].find_all('td')[1].text.replace("\n", "").replace("\t", "")
    volume = int(rows[1].find_all('td')[1].text.replace(",", ""))
    volume_date = rows[1].find_all('td')[2].text[1:-1]
    turnover = int(rows[2].find_all('td')[1].text.replace(",", ""))
    transactions = int(rows[3].find_all('td')[1].text.replace(",", ""))
    vwap = float(rows[4].find_all('td')[1].text.replace(",", ""))
    open = float(rows[5].find_all('td')[1].text.replace(",", ""))
    high = float(rows[6].find_all('td')[1].text.replace(",", ""))
    high_time = rows[6].find_all('td')[2].text[1:-1]
    low = float(rows[7].find_all('td')[1].text.replace(",", ""))
    low_time = rows[7].find_all('td')[2].text[1:-1]
    threshold = [ float(rows[8].find_all('td')[1].find_all('span')[0].text.replace(",", "")), float(rows[8].find_all('td')[1].find_all('span')[1].text.replace(",", "")) ]
    previous_close = float(rows[9].find_all('td')[1].text.replace(",", ""))
    previous_close_date = rows[9].find_all('td')[2].text[1:-1]
    week_52 = [ float(rows[10].find_all('td')[1].find_all('span')[0].text.replace(",", "")), float(rows[10].find_all('td')[1].find_all('span')[1].text.replace(",", "")) ]
    market_cap = rows[11].find_all('td')[1].text

    # Creating the dictionary
    stock_details = {   "stock" : stock,
                        "price" : price,
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
    

    


if __name__ == "__main__":
    search = "carrefour"
    
    try:
        stock = get_stock_from_name(search)
    except ValueError:
        try:
            stock = get_stock_from_symbol(search)
        except ValueError:
            try:
                stock = get_stock_from_isin(search)
            except ValueError as ve:
                print(search.upper() + " " + str(ve))
                exit()
    
    start = time()
    stock_details = get_stock_details_fast(stock)
    print(f"TIME : {time() - start}\n")
    print(stock_details)

    start = time()
    stock_details = get_stock_details(stock)
    print(f"\nTIME : {time() - start}\n")
    print(stock_details)