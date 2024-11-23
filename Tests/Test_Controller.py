import unittest
import json
from unittest.mock import patch, MagicMock
from controller import StockController
import requests


class TestController(unittest.TestCase):
    def setUp(self):
        self.controller_service = StockController()
        self.client = self.controller_service.app.test_client()

    @patch('service.StockService')  # Mock the StockService dependency
    def test_add_valid_stock(self, MockStockService):
        mock_service = MockStockService.return_value
        mock_service.symbol_exists.return_value = False
        mock_service.add_stock.return_value = MagicMock(id="stock123")

        # Define test cases
        cases = [
            {
                "description": "Complete payload, expecting 201",
                "payload": {
                    "symbol": "AAPL",
                    "purchase_price": 150.0,
                    "shares": 10,
                    "name": "Apple Inc.",
                    "purchase_date": "2023-10-01"}
            },
            {
                "description": "Partial payload, expecting 201",
                "payload": {
                    "symbol": "AAPL",
                    "purchase_price": 150.0,
                    "shares": 10}
            }
        ]

        # Run each test case
        for case in cases:
            with self.subTest(case=case["description"]):
                # Perform the POST request
                response = self.client.post(
                    '/stocks',
                    json=case["payload"],
                    content_type='application/json'
                )

                # Assert the response status and content
                self.assertEqual(response.status_code, 201)
                self.assertIn("id", response.json)

    @patch('service.StockService')  # Mock the StockService dependency
    def test_add_invalid_stock(self, MockStockService):
        mock_service = MockStockService.return_value
        mock_service.symbol_exists.return_value = False

        # Define invalid test cases
        cases = [
            {
                "description": "Missing required field 'symbol'",
                "payload": {
                    "purchase_price": 150.0,
                    "shares": 10
                },
                "expected_status": 400,
                "expected_error": "Malformed data",
            },
            {
                "description": "Negative 'purchase_price'",
                "payload": {
                    "symbol": "AAPL",
                    "purchase_price": -150.0,
                    "shares": 10
                },
                "expected_status": 400,
                "expected_error": "Malformed data",
            },
            {
                "description": "Zero 'shares'",
                "payload": {
                    "symbol": "AAPL",
                    "purchase_price": 150.0,
                    "shares": 0
                },
                "expected_status": 400,
                "expected_error": "Malformed data",
            },
            {
                "description": "Invalid content type (not JSON)",
                "payload": "Invalid payload",
                "expected_status": 415,
                "expected_error": "Expected application/json media type",
                "content_type": "text/plain"
            }
        ]

        # Run each invalid case
        for case in cases:
            with self.subTest(case=case["description"]):
                # Determine content type
                content_type = case.get("content_type", "application/json")

                # Perform the POST request
                response = self.client.post(
                    '/stocks',
                    json=case["payload"] if content_type == "application/json" else None,
                    data=case["payload"] if content_type != "application/json" else None,
                    content_type=content_type
                )

                # Assert the response
                self.assertEqual(response.status_code, case["expected_status"])
                self.assertIn("error", response.json)
                self.assertEqual(response.json["error"], case["expected_error"])

    def test_duplicate_stock_symbol(self):
        payloads = [
            {
                "symbol": "AAPL",
                "purchase_price": 150.0,
                "shares": 10,
                "name": "Apple Inc.",
                "purchase_date": "2023-10-01"
            },{
                "symbol": "AAPL",
                "purchase_price": 160.0,
                "shares": 50,
                "name": "Apple Inc.",
                "purchase_date": "2023-10-01"
            }]

        # Add the first stock
        response = self.client.post(
            '/stocks',
            json=payloads[0],
            content_type='application/json'
        )

        # Assert the first addition is successful
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.json)

        # Add the second stock with the same symbol
        response = self.client.post(
            '/stocks',
            json=payloads[1],
            content_type='application/json'
        )

        # Assert the second addition fails due to duplication
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Malformed data")





#     #TODO: did i made a working test?
#     @patch('controller.requests.post')
#     def test_add_timeout(self, mock_post):
#         # Simulate a timeout
#         mock_post.side_effect = requests.exceptions.Timeout
#
#         # Define the payload
#         payload = {
#             "symbol": "AAPL",
#             "purchase_price": 150.0,
#             "shares": 10,
#             "name": "Apple Inc.",
#             "purchase_date": "2023-10-01"
#         }
#
#         # Make a POST request to add the stock
#         response = self.app.post('/stocks', data=json.dumps(payload), content_type='application/json')
#
#         # Check the response status code
#         self.assertEqual(response.status_code, 500)
#
#         # Check the response data
#         response_data = json.loads(response.data)
#         self.assertIn('error', response_data)
#
#
#     # GET /stocks tests
#     # If successful, it returns a JSON array of stock objects with a status code of 200.
#     # Possible error status codes returned: 500.
#     # The endpoint should support query strings of the form <field>=<value>.
#     def test_get_stocks(self):
#         # add manually a 2 stocks to simulate a service wiht 2 stocks
#         stock_service = StockService()
#         stock_service.add_stock("Apple", "AAPL", 150.0, "2023-01-01", 10)
#         stock_service.add_stock("Google", "GOOGL", 100.0, "2023-01-01", 5)
#         print("added 2 stocks successfully")
#         # Make a GET request to get the stocks
#         response = self.app.get('/stocks')
#
#         # Check the response status code
#         self.assertEqual(response.status_code, 200)
#
#         # Check the response data
#         response_data = json.loads(response.data)
#         self.assertIsInstance(response_data, list)
#         self.assertEqual(len(response_data), 2)
#         self.assertEqual(response_data[0]['name'], 'Apple')
#         self.assertEqual(response_data[1]['name'], 'Google')
#
# #TODO: did i made a working test?
#     @patch('controller.requests.get')
#     def test_get_stocks_timeout(self, mock_get):
#         # Simulate a timeout
#         mock_get.side_effect = requests.exceptions.Timeout
#
#         # Make a GET request to get the stocks
#         response = self.app.get('/stocks')
#
#         # Check the response status code
#         self.assertEqual(response.status_code, 500)
#
#         # Check the response data
#         response_data = json.loads(response.data)
#         self.assertIn('error', response_data)


if __name__ == '__main__':
    unittest.main()