import logging
from flask import Flask, request, jsonify
from service import StockService


class StockController:
    def __init__(self, app, stock_service):
        self.app = Flask(__name__)
        self.stock_service = StockService()
        self.setup_routes()

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def setup_routes(self):
        # Define the routes and bind them to class methods
        self.app.route('/stocks', methods=['POST'])(self.add_stock)
        self.app.route('/stocks', methods=['GET'])(self.get_stocks)
        self.app.route('/stocks/<string:stock_id>', methods=['GET'])(self.get_stock)
        self.app.route('/stock/<string:stock_id>', methods=['DELETE'])(self.remove_stock)
        self.app.route('/stocks/<string:stock_id>', methods=['PUT'])(self.update_stock)

        self.app.route('/stock-value/<string:symbol>', methods=['GET'])(self.stock_value)
        self.app.route('/portfolio-value', methods=['GET'])(self.portfolio_value)


    def validate_stock_data(self, data):
        required_fields = ['symbol', 'purchase_price', 'shares']
        for field in required_fields:
            # Check if the field exists and is not empty
            if field not in data or not str(data[field]).strip():
                logging.error(f"Validation failed: '{field}' is missing or empty.")
                return False

        # Validate 'symbol': must be a non-empty uppercase string
        if not isinstance(data['symbol'], str) or not data['symbol'].isupper():
            logging.error("Validation failed: 'symbol' must be an uppercase string.")
            return False

        if self.stock_service.symbol_exists(data['symbol']):
            logging.error(f"Validation failed: Stock with symbol '{data['symbol']}' already exists.")
            return False

        # Validate 'purchase_price': must be a positive float
        try:
            if float(data['purchase_price']) <= 0:
                logging.error("Validation failed: 'purchase_price' must be a positive number.")
                return False
        except (ValueError, TypeError):
            logging.error("Validation failed: 'purchase_price' must be a valid number.")
            return False

        # Validate 'shares': must be a positive integer
        try:
            if int(data['shares']) <= 0:
                logging.error("Validation failed: 'shares' must be a positive integer.")
                return False
        except (ValueError, TypeError):
            logging.error("Validation failed: 'shares' must be a valid integer.")
            return False

        logging.info("Stock data validation passed.")
        return True

    # TODO: TEST for 415, 400, 500, 201
    def add_stock(self):
        """
        POST: The POST request provides a JSON object payload that must contain: 'symbol', 'purchase price',
        'shares' fields. Optionally it can also provide the ‘name’ and 'purchase date' of the stock. If successful,
        it returns the JSON for the id * assigned to that object with status code 201. Possible error status codes
        returned: 400, 415, 500.
        """
        try:
            content_type = request.headers.get('Content-Type')
            if content_type != 'application/json':
                return jsonify({'error': 'Expected application/json media type'}), 415
            data = request.get_json()

            if not self.validate_stock_data(data):
                return jsonify({'error': 'Malformed data'}), 400

            name = data.get('name', 'NA')
            symbol = data['symbol']
            purchase_price = data['purchase_price']
            purchase_date = data.get('purchase_date', 'NA')
            shares = data['shares']

            # note: id is generated in the service layer
            stock = self.stock_service.add_stock(symbol, purchase_price, shares, name, purchase_date)
            return jsonify({'id': stock.id}), 201
        except Exception as e:
            return jsonify({'server error': str(e)}), 500


        # TODO: TESTED for 200, 500


    def get_stocks(self):
        """
        GET: If successful, it returns a JSON array of stock objects with status code 200.
        Possible error status codes returned: 500.
        For this assignment, you need to support query strings of the form <field>=<value>.
        """
        try:
            stocks = self.stock_service.get_stocks()
            query_params = request.args.to_dict()

            # Apply filters if query parameters exist
            if query_params:
                stocks = [
                    stock for stock in stocks
                    if all(str(stock.get(key, "")).lower() == str(value).lower()
                           for key, value in query_params.items() if key in stock)
                ]

        except Exception as e:
            logging.error(f"Error in get_stocks: {str(e)}")
            return jsonify({'server error': str(e)}), 500

    # TODO: TEST for 200, 404, 500
    def get_stock(self, stock_id):
        try:
            stock = self.stock_service.get_stock(stock_id)
            return jsonify(stock.__dict__), 200
        except KeyError:
            logging.error(f"DELETE request error: Stock with id '{stock_id}' not found.")
            return jsonify({"error": "Not found"}), 404
        except Exception as e:
            return jsonify({'server error': str(e)}), 500


    def remove_stock(self, stock_id):
        try:
            self.stock_service.remove_stock(stock_id)
            return '', 204
        except KeyError:
            logging.error(f"DELETE request error: Stock with id '{stock_id}' not found.")
            return jsonify({"error": "Not found"}), 404
        except Exception as e:
            logging.error(f"Error in remove_stock: {str(e)}")
            return jsonify({'server error': str(e)}), 500

    def update_stock(self, stock_id):
        try:
            content_type = request.headers.get('Content-Type')
            if content_type != 'application/json':
                return jsonify({"error": "Expected application/json media type"}), 415

            data = request.get_json()

            # Required fields for the stock object
            required_fields = ['id', 'symbol', 'name', 'purchase_price', 'purchase_date', 'shares']
            if not all(field in data for field in required_fields):
                logging.error(f"Validation failed: Missing required fields in data.")
                return jsonify({"error": "Malformed data"}), 400

            # Ensure the ID in the payload matches the stock_id in the URL
            if data['id'] != stock_id:
                logging.error(
                    f"Validation failed: Stock ID in URL '{stock_id}' does not match ID in payload '{data['id']}'.")
                return jsonify({"error": "ID mismatch"}), 400

            # Validate the payload values
            if not self.validate_stock_data(data):
                return jsonify({"error": "Invalid data"}), 400

            # Update stock in the service layer
            self.stock_service.update_stock(
                stock_id,
                {
                    'symbol': data['symbol'],
                    'name': data['name'],
                    'purchase_price': float(data['purchase_price']),
                    'purchase_date': data['purchase_date'],
                    'shares': int(data['shares'])
                }
            )

            # Prepare and return the response
            response_data = {"id": stock_id}
            return jsonify(response_data), 200

        except KeyError:
            logging.error(f"PUT error: Stock with ID '{stock_id}' not found.")
            return jsonify({"error": "Not found"}), 404
        except Exception as e:
            logging.error(f"Exception in update_stock: {str(e)}")
            return jsonify({"server error": str(e)}), 500


    # TODO: check what expected from a stock not in the portfolio
    def stock_value(self, symbol):
        # check valid symbol
        # TODO: the ninja api accepts also lower case symbols. should we check for that?
        if not symbol:
            return jsonify({'error': 'Malformed data'}), 400

        # get current value from service
        value = self.stock_service.get_stock_value(symbol)
        return jsonify({'value': value}), 200


    def portfolio_value(self):
        pass
