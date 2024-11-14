# service.py
# service.py

from stock import Stock
import uuid, requests
NINJA_API_KEY = "" #TODO: Add your API key here
class StockService:
    def __init__(self):
        self.portfolio = {}

    def add_stock(self, name: str, symbol: str, purchase_price: float, purchase_date: str, shares: int) -> Stock:
        stock_id = str(uuid.uuid4())
        new_stock = Stock(stock_id, name, symbol, purchase_price, purchase_date, shares)
        self.portfolio[stock_id] = new_stock
        return new_stock

    def get_stock(self, stock_id: str) -> Stock:
        if stock_id in self.portfolio:
            return self.portfolio[stock_id]
        else:
            raise ValueError("Stock not found")

    def remove_stock(self, stock_id: str) -> None:
        if stock_id in self.portfolio:
            del self.portfolio[stock_id]
        else:
            raise ValueError("Stock not found")

    def get_stock_current_price(self, symbol: str) -> float:
        #for more info: https://api-ninjas.com/api/stockprice
        api_url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(symbol)
        response = requests.get(api_url, headers={'X-Api-Key': NINJA_API_KEY})
        if response.status_code == requests.codes.ok:
            print(response.text)
        else:
            print("Error:", response.status_code, response.text)

    def get_stock_value(self, stock_id: str) -> float:
        if stock_id in self.portfolio:
            stock = self.portfolio[stock_id]
            current_price = self.get_stock_current_price(stock.symbol)
            return stock.shares * current_price
        else:
            raise ValueError("Stock not found")

    def get_portfolio_value(self) -> float:
        total_value = 0
        for stock in self.portfolio.values():
            current_price = self.get_stock_current_price(stock.symbol)
            if current_price:
                total_value += stock.shares * current_price
            else:
                raise ValueError(f"Price for stock {stock.symbol} not available")
        return total_value

