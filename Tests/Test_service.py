import unittest
import json
from unittest.mock import patch
from controller import app
from service import StockService
import requests

class TestController(unittest.TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.stock_service = StockService()

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # POST /stocks tests
    def test_add_valid_stock(self):
        # Define the payload
        payload = {
            "symbol": "AAPL",
            "purchase_price": 150.0,
            "shares": 10,
            "name": "Apple Inc.",
            "purchase_date": "2023-10-01"
        }

        # Make a POST request to add the stock
        response = self.app.post('/stocks', data=json.dumps(payload), content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 201)

        # Check the response data
        response_data = json.loads(response.data)
        self.assertIn('id', response_data)

    def test_add_invalid_stock(self):
        # Define the payload with missing required parameters
        payload = {
            "symbol": "AAPL",
            "purchase_price": 150.0
        }

        # Make a POST request to add the stock
        response = self.app.post('/stocks', data=json.dumps(payload), content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 400)

        # Check the response data
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    #TODO: did i make a working test?
    @patch('controller.requests.post')
    def test_add_timeout(self, mock_post):
        # Simulate a timeout
        mock_post.side_effect = requests.exceptions.Timeout

        # Define the payload
        payload = {
            "symbol": "AAPL",
            "purchase_price": 150.0,
            "shares": 10,
            "name": "Apple Inc.",
            "purchase_date": "2023-10-01"
        }

        # Make a POST request to add the stock
        response = self.app.post('/stocks', data=json.dumps(payload), content_type='application/json')

        # Check the response status code
        self.assertEqual(response.status_code, 500)

        # Check the response data
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

    #TODO: not sure about the wanted behavior of the GET stocks, do i return an array, list or dict
    # GET /stocks tests
    def test_get_stocks(self):
        # Add manually 2 stocks to simulate a service with 2 stocks
        self.stock_service.add_stock("AAPL", 150.0, 10, "Apple Inc.", "2023-01-01")
        self.stock_service.add_stock("GOOGL", 2800.0, 5, "Alphabet Inc.", "2023-01-01")

        # Call the get_stocks method
        stocks = self.stock_service.get_stocks()

        # Check that the returned value is a dictionary
        self.assertIsInstance(stocks, list)
        self.assertEqual(len(stocks), 2)
        self.assertIn("AAPL", [stock["symbol"] for stock in stocks.values()])
        self.assertIn("GOOGL", [stock["symbol"] for stock in stocks.values()])

    @patch('controller.requests.get')
    def test_get_stocks_timeout(self, mock_get):
        # Simulate a timeout
        mock_get.side_effect = requests.exceptions.Timeout

        # Make a GET request to get the stocks
        response = self.app.get('/stocks')

        # Check the response status code
        self.assertEqual(response.status_code, 500)

        # Check the response data
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)

if __name__ == '__main__':
    unittest.main()