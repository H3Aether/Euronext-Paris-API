from stock_info import *
from requests_html import HTMLSession

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


if __name__ == "__main__":
    search = "stm"
    
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
    
    stock_details = get_stock_details(stock)
    print(stock_details)