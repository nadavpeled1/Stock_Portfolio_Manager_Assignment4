import unittest
import json
from unittest.mock import patch
from controller import app
import requests

from service import StockService


class TestController(unittest.TestCase):
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

    #TODO: did i made a working test?
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


    # GET /stocks tests
    # If successful, it returns a JSON array of stock objects with a status code of 200.
    # Possible error status codes returned: 500.
    # The endpoint should support query strings of the form <field>=<value>.
    def test_get_stocks(self):
        # add manually a 2 stocks to simulate a service wiht 2 stocks
        stock_service = StockService()
        stock_service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
        stock_service.add_stock("Google", "GOOGL", 100.0, "2023-01-01", 5)
        print("added 2 stocks successfully")
        # Make a GET request to get the stocks
        response = self.app.get('/stocks')

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Check the response data
        response_data = json.loads(response.data)
        self.assertIsInstance(response_data, list)
        self.assertEqual(len(response_data), 2)
        self.assertEqual(response_data[0]['name'], 'Apple')
        self.assertEqual(response_data[1]['name'], 'Google')

#TODO: did i made a working test?
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