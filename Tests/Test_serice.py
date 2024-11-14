# Tests/test_service.py

import unittest
from service import StockService
from stock import Stock

class TestStockService(unittest.TestCase):
    def setUp(self):
        self.service = StockService()

    def test_add_stock(self):
        stock = self.service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
        self.assertEqual(stock.name, "Apple")
        self.assertEqual(stock.symbol, "AAPL")
        self.assertEqual(stock.purchase_price, 150.0)
        self.assertEqual(stock.purchase_date, "2023-01-01")
        self.assertEqual(stock.shares, 10)

    def test_get_stock(self):
        stock = self.service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
        retrieved_stock = self.service.get_stock(stock.id)
        self.assertEqual(retrieved_stock, stock)

    def test_remove_stock(self):
        stock = self.service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
        self.service.remove_stock(stock.id)
        with self.assertRaises(ValueError):
            self.service.get_stock(stock.id)

    def test_get_stock_value(self):
        stock = self.service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
        self.service.get_stock_current_price = lambda symbol: 200.0  # Mocking the current price
        stock_value = self.service.get_stock_value(stock.id)
        self.assertEqual(stock_value, 2000.0)

    def test_get_portfolio_value(self):
        self.service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
        self.service.add_stock("Google", "GOOGL", 100.0, "2023-01-01", 5)
        self.service.get_stock_current_price = lambda symbol: 200.0  # Mocking the current price
        portfolio_value = self.service.get_portfolio_value()
        self.assertEqual(portfolio_value, 3000.0)

if __name__ == '__main__':
    unittest.main()