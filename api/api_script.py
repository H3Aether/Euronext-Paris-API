import os, sys
# import module from parent directory subfolder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir+'\\src')
import handle_database as db
from time import sleep


from flask import Flask, request
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

class Company(Resource):
    def get(self):
        # First check the isin, then symbol, then name
        isin = request.args.get('isin')
        symbol = request.args.get('symbol')
        name = request.args.get('name')
        

        db.start() # Start the database
        try:
            if isin: # Get the company with the isin
                company = db.selectCompany(isin)
            elif symbol: # Get the company with the symbol
                company = db.selectCompany(symbol=symbol)
            elif name: # Get the company with the name
                company = db.selectCompany(name=name)
            
            data = {
                "isin": company[0],
                "name": company[1],
                "symbol": company[2],
                "market": company[3]
            }
            db.stop() # Stop the database
            return data, 200

        except Exception as e:
            db.stop() # Stop the database
            return { "message": str(e) }, 404


class Stock(Resource):
    def get(self):
        # First check the isin, then symbol, then name
        isin = request.args.get('isin')
        symbol = request.args.get('symbol')
        name = request.args.get('name')

        db.start()
        try:
            if isin: # Get the stock with the isin
                stock = db.selectStock(isin)
                company = db.selectCompany(isin)
            elif symbol: # Get the stock with the symbol
                stock = db.selectStock(symbol=symbol)
                company = db.selectCompany(symbol=symbol)
            elif name: # Get the stock with the name
                stock = db.selectStock(name=name)
                company = db.selectCompany(name=name)
            
            data = {"company": {"isin": company[0], "name": company[1], "symbol": company[2], "market": company[3]},
                    "price" : stock[1],
                    "currency": stock[2],
                    "volume": {"value": stock[3], "date": stock[4]},
                    "turnover": stock[5],
                    "transactions": stock[6],
                    "vwap": stock[7],
                    "open": stock[8],
                    "high": {"price": stock[9], "time": stock[10]},
                    "low": {"price": stock[11], "time": stock[12]},
                    "threshold": [stock[13], stock[14]],
                    "previous_close": {"price": stock[15], "date": stock[16]},
                    "52_weeks": [stock[17], stock[18]],
                    "market_cap": stock[19],
                    "updated": stock[20]}
            db.stop()
            return data, 200
        except Exception as e:
            db.stop()
            return { "message": str(e) }, 404



api.add_resource(Company, "/company")
api.add_resource(Stock, "/stock")

if __name__ == "__main__":
    app.run(debug=True)