import os
import euronext_paris_stock_list
import stock_details
import sqlite3

### COMPANY TABLE ###
# isin      TEXT PRIMARY KEY
# name      TEXT
# symbol    TEXT
# market    TEXT

# DB_FILE is in the same directory as this file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

class Database:
    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS company( isin TEXT PRIMARY KEY, name TEXT, symbol TEXT, market TEXT )")
        self.connection.commit()

    def __del__(self):
        self.connection.close()

    def reset(self):
        self.cursor.execute("DROP TABLE IF EXISTS company")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS company( isin TEXT PRIMARY KEY, name TEXT, symbol TEXT, market TEXT )")
        self.connection.commit()

    def initialize(self):
        print("[RESET] Resetting the database...")
        self.reset()
        print("[INIT] Initializing the database...")
        self.__initialize_companies()
        print("[INIT] Done.")
    
    ## INSERTION FUNCTIONS ##
    def __initialize_companies(self):
        # Get the list of all the companies using the euronext_paris_stock_list module
        companies = euronext_paris_stock_list.get()
        # Insert the companies in the database
        self.cursor.executemany("INSERT OR IGNORE INTO company VALUES(?, ?, ?, ?)", [(company['isin'], company['name'], company['symbol'], company['market']) for company in companies['companies']])
        self.connection.commit()
    
    def update(self):
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




## MODULE FUNCTIONS ##
def initialize():
    db = Database(DB_FILE)
    db.initialize()
    del db

def update():
    db = Database(DB_FILE)
    db.update()
    del db

def selectCompany(isin=None, name=None, symbol=None):
    db = Database(DB_FILE)
    res = db.selectCompany(isin, name, symbol)
    del db
    return res