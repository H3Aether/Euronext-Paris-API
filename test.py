# Get the content of https://live.euronext.com/en/product/equities/FR0000071946-XPAR
# The price of the stock is in the span with id "header-instrument-price"
# The price is displayed using javascript

from requests_html import HTMLSession
session = HTMLSession()

r = session.get('https://live.euronext.com/en/product/equities/FR0000071946-XPAR')
r.html.render(sleep=1)
price = r.html.find('#header-instrument-price', first=True)

print(price.text)