# service.py
# service.py

from stock import Stock
import uuid

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

    def get_stock_value(self, stock_id: str, current_price: float) -> float:
        if stock_id in self.portfolio:
            stock = self.portfolio[stock_id]
            return stock.shares * current_price
        else:
            raise ValueError("Stock not found")

    def get_portfolio_value(self, stock_prices: dict) -> float:
        total_value = 0
        for stock in self.portfolio.values():
            if stock.symbol in stock_prices:
                total_value += stock.shares * stock_prices[stock.symbol]
            else:
                raise ValueError(f"Price for stock {stock.symbol} not available")
        return total_value