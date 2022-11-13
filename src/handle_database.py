import os
import euronext_paris_stock_list
import stock_details
import sqlite3

### COMPANY TABLE ###
# isin      TEXT PRIMARY KEY
# name      TEXT
# symbol    TEXT
# market    TEXT

### STOCK TABLE ###
# isin                  TEXT PRIMARY KEY
# price                 REAL
# currency              TEXT
# volume                INTEGER
# volume_date           TEXT
# turnover              INTEGER
# transactions          INTEGER
# vwap                  REAL
# open                  REAL
# high                  REAL
# high_time             TEXT
# low                   REAL
# low_time              TEXT
# threshold_low         REAL
# threshold_high        REAL
# previous_close        REAL
# previous_close_date   TEXT
# week_52_low           REAL
# week_52_high          REAL
# market_cap            TEXT
# update_date           TEXT

# DB_FILE is in the same directory as this file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

class Database:
    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS company( isin TEXT PRIMARY KEY, name TEXT, symbol TEXT, market TEXT )")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stock( isin TEXT PRIMARY KEY, price REAL, currency TEXT, volume INTEGER, volume_date TEXT, turnover INTEGER, transactions INTEGER, vwap REAL, open REAL, high REAL, high_time TEXT, low REAL, low_time TEXT, threshold_low REAL, threshold_high REAL, previous_close REAL, previous_close_date TEXT, week_52_low REAL, week_52_high REAL, market_cap TEXT, update_date TEXT )")
        self.connection.commit()

    def close(self):
        self.connection.close()

    def reset(self):
        """ Reset the database """
        self.cursor.execute("DROP TABLE IF EXISTS company")
        self.cursor.execute("DROP TABLE IF EXISTS stock")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS company( isin TEXT PRIMARY KEY, name TEXT, symbol TEXT, market TEXT )")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS stock( isin TEXT PRIMARY KEY, price REAL, currency TEXT, volume INTEGER, volume_date TEXT, turnover INTEGER, transactions INTEGER, vwap REAL, open REAL, high REAL, high_time TEXT, low REAL, low_time TEXT, threshold_low REAL, threshold_high REAL, previous_close REAL, previous_close_date TEXT, week_52_low REAL, week_52_high REAL, market_cap TEXT, update_date TEXT )")
        self.connection.commit()

    def initialize(self):
        print("[RESET] Resetting the database...")
        self.reset()
        print("[INIT] Initializing the database...")
        print("[INIT] Adding companies...")
        self.__initialize_companies()
        print("[INIT] Adding stocks...")
        self.__initialize_stocks()
        print("[INIT] Done.")
    
    ## INSERTION FUNCTIONS ##
    def __initialize_companies(self):
        # Get the list of all the companies using the euronext_paris_stock_list module
        companies = euronext_paris_stock_list.get()
        # Insert the companies in the database
        self.cursor.executemany("INSERT OR IGNORE INTO company VALUES(?, ?, ?, ?)", [(company['isin'], company['name'], company['symbol'], company['market']) for company in companies['companies']])
        self.connection.commit()
    
    def __initialize_stocks(self):
        # Get the list of all isins in the database
        res = self.cursor.execute("SELECT isin, market FROM company")
        companies = res.fetchall()

        # Get the stock details for each company
        count = 0
        deleted = 0
        print(f"{count} / {len(companies) - deleted} ({round(count / (len(companies) - deleted) * 100, 2)}%)")
        for company in companies:
            try:
                stock = stock_details.get(company[0], company[1])
                self.cursor.execute("INSERT OR IGNORE INTO stock VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (company[0], stock['price'], stock['currency'], stock['volume']['value'], stock['volume']['date'], stock['turnover'], stock['transactions'], stock['vwap'], stock['open'], stock['high']['price'], stock['high'][ 'time'], stock['low']['price'], stock['low']['time'], stock['threshold'][1], stock['threshold'][0], stock['previous_close']['price'], stock['previous_close']['date'], stock['52_week'][0], stock['52_week'][1], stock['market_cap'], stock['update_date']))
            except Exception as e: # If the stock details cannot be retrieved, delete the company from the database
                print(e)
                self.cursor.execute("DELETE FROM company WHERE isin = ?", (company[0],))
                deleted += 1
            
            count += 1
            if count % 20 == 0:
                print(f"{count} / {len(companies) - deleted} ({round(count / (len(companies) - deleted) * 100, 2)}%)")

        self.connection.commit()


    ## UPDATE FUNCTIONS ##
    def updateCompanies(self):
        """ Update the companies in the database. If a new one is added, the corresponding stock is also added to the database """
        # Get the list of all the companies using the euronext_paris_stock_list module
        companies = euronext_paris_stock_list.get()
        # Insert the companies in the database
        for company in companies['companies']:
            res = self.cursor.execute("SELECT * FROM company WHERE isin = ?", (company['isin'],))
            if res.fetchone() is None: # If the company is not in the database, add it
                try: # Try to get the stock details. If it succeeds, add the company and the stock to the database
                    stock = stock_details.get(company['isin'], company['market'])
                except Exception as e: # If the stock details cannot be retrieved, skip this company
                    print(e)
                    continue
                # Insert the company and the stock in the tables
                self.cursor.execute("INSERT INTO company VALUES(?, ?, ?, ?)", (company['isin'], company['name'], company['symbol'], company['market']))
                self.cursor.execute("INSERT INTO stock VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (company['isin'], stock['price'], stock['currency'], stock['volume']['value'], stock['volume']['date'], stock['turnover'], stock['transactions'], stock['vwap'], stock['open'], stock['high']['price'], stock['high'][ 'time'], stock['low']['price'], stock['low']['time'], stock['threshold'][1], stock['threshold'][0], stock['previous_close']['price'], stock['previous_close']['date'], stock['52_week'][0], stock['52_week'][1], stock['market_cap'], stock['update_date']))





    ## SELECTION FUNCTIONS ##
    def selectCompany(self, isin=None, name=None, symbol=None):
        res = None
        if isin is not None:
            res = self.cursor.execute("SELECT * FROM company WHERE isin = ?", (isin.upper(),)).fetchone()
        elif name is not None:
            res = self.cursor.execute("SELECT * FROM company WHERE name = ?", (name.upper(),)).fetchone()
        elif symbol is not None:
            res = self.cursor.execute("SELECT * FROM company WHERE symbol = ?", (symbol.upper(),)).fetchone()
        
        if res is not None:
            return res
        else:
            raise Exception("Company {} not found".format(isin if isin is not None else name if name is not None else symbol))

    def __select_stock_from_isin(self, isin):
        self.cursor.execute("SELECT * FROM stock WHERE isin = ?", (isin,))
        return self.cursor.fetchone()
    
    def selectStock(self, isin=None, name=None, symbol=None):
        res = None
        if isin is not None:
            res = self.__select_stock_from_isin(isin)
        elif name is not None:
            try:
                company = self.selectCompany(name=name)
                res = self.__select_stock_from_isin(company[0])
            except Exception as e:
                print(e)
        elif symbol is not None:
            try:
                company = self.selectCompany(symbol=symbol)
                res = self.__select_stock_from_isin(company[0])
                print(res)
            except Exception as e:
                print(e)
        
        if res is not None:
            return res
        else:
            raise Exception("[ERROR] Stock {} not found".format(isin if isin is not None else name if name is not None else symbol))

    def test(self):
        # Print the number of companies in the database
        print(self.cursor.execute("SELECT COUNT(*) FROM company").fetchone()[0])




## GLOBAL VARIABLE ##
DB = None

## START, STOP, INIT FUNCTIONS ##
def init():
    global DB
    DB = Database(DB_FILE)
    DB.initialize()

def start():
    global DB
    DB = Database(DB_FILE)

def stop():
    global DB
    DB.close()
    DB = None

## SELECT FUNCTIONS ##

def selectCompany(isin=None, name=None, symbol=None):
    return DB.selectCompany(isin, name, symbol)

def selectStock(isin=None, name=None, symbol=None):
    return DB.selectStock(isin, name, symbol)