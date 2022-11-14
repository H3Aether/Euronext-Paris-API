import os, sys
# import module from parent directory subfolder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir+'\\src')
import handle_database as db
import stock_details as sd

from time import time
from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

DATABASE_UPDATE_INTERVAL = 60*60*24 # 24 hours
global last_database_update

def getCompanyFromDatabase(isin, symbol, name):
    """ Get the company from the database.
    If multiple arguments are given, the function will consider only one, in the following order: isin, symbol, name. """

    ## TRY TO UPDATE THE DATABASE
    # If the database is older than DATABASE_UPDATE_INTERVAL, update it
    global last_database_update
    if time() - last_database_update > DATABASE_UPDATE_INTERVAL:
        print("[DATABASE] Updating the database...")
        db.update()
        last_database_update = time()

    if isin: # Get the company with the isin
        try:
            company = db.selectCompany(isin)
        except:
            raise Exception("Company with isin {} does not exist".format(isin), 404)
    elif symbol: # Get the company with the symbol
        try:
            company = db.selectCompany(symbol=symbol)
        except:
            raise Exception("Company with symbol {} does not exist".format(symbol), 404)
    elif name: # Get the company with the name
        try:
            company = db.selectCompany(name=name)
        except:
            raise Exception("Company with name {} does not exist".format(name), 404)
    else:
        raise Exception("No isin, symbol or name provided", 400)
    
    return company


class Company(Resource):
    def get(self):
        isin = request.args.get('isin')
        symbol = request.args.get('symbol')
        name = request.args.get('name')

        try:
            company = getCompanyFromDatabase(isin, symbol, name)
        except Exception as e:
            return { "message": str(e.args[0]) }, e.args[1]

        data = {
            "isin": company[0],
            "name": company[1],
            "symbol": company[2],
            "market": company[3]
        }
        return data, 200


class Stock(Resource):
    def get(self):
        isin = request.args.get('isin')
        symbol = request.args.get('symbol')
        name = request.args.get('name')

        try:
            company = getCompanyFromDatabase(isin, symbol, name)
        except Exception as e:
            return { "message": str(e.args[0]) }, e.args[1]
            
        try:
            stock = sd.get(isin=company[0], market=company[3])
            company_dict = { "company" : { "isin": company[0], "name": company[1], "symbol": company[2], "market": company[3] }}
            data = company_dict | stock
            return data, 200
        except Exception as e:
            return { "message": str(e) }, 502


class StockChart(Resource):
    def get(self):
        isin = request.args.get('isin')
        symbol = request.args.get('symbol')
        name = request.args.get('name')
        period = request.args.get('period')
        if period is None:
            period = 'intraday' # Default value

        if period != 'intraday' and period != 'max':
            return { "message": "Invalid period. Valid periods are 'intraday' (default) and 'max'" }, 400

        try:
            company = getCompanyFromDatabase(isin, symbol, name)
        except Exception as e:
            return { "message": str(e.args[0]) }, e.args[1]

        try:
            chart = sd.getChart(isin=company[0], market=company[3], period=period)
        except Exception as e:
            return { "message": str(e) }, 502
        
        return chart, 200




api.add_resource(Company, "/company")
api.add_resource(Stock, "/stock")
api.add_resource(StockChart, "/stock/chart")

if __name__ == "__main__":
    db.initialize()
    last_database_update = time()
    app.run()