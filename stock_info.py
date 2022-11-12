import json

def get_stock_from_isin(isin):
    """ Get the stock from the isin """
    with open("euronext_paris_stocks.json", encoding="utf-8") as f:
        stocks = json.load(f)
        for stock in stocks["stocks"]:
            if stock["isin"] == isin.upper():
                return stock
        raise ValueError("was not found")

def get_stock_from_symbol(symbol):
    """ Get the stock from the symbol """
    with open("euronext_paris_stocks.json", encoding="utf-8") as f:
        stocks = json.load(f)
        for stock in stocks["stocks"]:
            if stock["symbol"] == symbol.upper():
                return stock
        raise ValueError("was not found")

def get_stock_from_name(name):
    """ Get the stock from the name """
    with open("euronext_paris_stocks.json", encoding="utf-8") as f:
        stocks = json.load(f)
        for stock in stocks["stocks"]:
            if stock["name"].upper() == name.upper():
                return stock
        raise ValueError("was not found")

def get_stock(search):
    """ Search a stock from the name, symbol or isin """
    try:
        stock = get_stock_from_name(search)
    except ValueError:
        try:
            stock = get_stock_from_symbol(search)
        except ValueError:
            try:
                stock = get_stock_from_isin(search)
            except ValueError as ve:
                raise ValueError(f"[ERROR] {search.upper()} was not found")
    return stock