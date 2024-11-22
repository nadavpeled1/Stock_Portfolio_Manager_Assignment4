# controller.py
import logging

from flask import Flask, request, jsonify
from service import StockService
# /stocks is a collection of stock objects. These stocks comprise the portfolio.
# /stocks/{id} is the stock object in /stocks with the given id.
# /stock-value/{id} is the current value of the given stock in the portfolio (= current stock price times number of shares).
# /portfolio-value is the current value of the entire portfolio.

# Create a Flask app and a StockService object
app = Flask(__name__)
stock_service = StockService()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def validate_stock_data(data):
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


# TODO: TESTED for 415, 400, 500, 201
@app.route('/stocks', methods=['POST'])
def add_stock():
    """
     POST: The POST request provides a JSON object payload that must contain: 'symbol', 'purchase price', 'shares' fields.
     Optionally it can also provide the ‘name’ and 'purchase date' of the stock.
     If successful, it returns the JSON for the id * assigned to that object with status code 201.
     Possible error status codes returned: 400, 415, 500.
    """
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({'error': 'Expected application/json media type'}), 415
        data = request.get_json()

        if not validate_stock_data(data):
            return jsonify({'error': 'Malformed data'}), 400

        name = data.get('name', 'NA')
        symbol = data['symbol']
        purchase_price = data['purchase_price']
        purchase_date = data.get('purchase_date', 'NA')
        shares = data['shares']

        # note: id is generated in the service layer
        stock = stock_service.add_stock(symbol, purchase_price, shares, name, purchase_date)
        return jsonify({'id': stock.id}), 201
    except Exception as e:
        return jsonify({'server error': str(e)}), 500


'''
GET: If successful, it returns a JSON array of stock objects with status code 200.
Possible error status codes returned: 500. For this assignment, you need to
support query strings of the form <field>=<value>.
'''
@app.route('/stocks', methods=['GET'])
#TESTED for 200, 500
def get_stocks():
    try:
        return jsonify(stock_service.get_stocks()), 200
    except Exception as e:
        return jsonify({'server error': str(e)}), 500


@app.route('/stocks/<string:stock_id>', methods=['GET'])
#TESTED for 200, 404,
def get_stock(stock_id):
    try:
        stock = stock_service.get_stock(stock_id)
        return jsonify(stock.__dict__), 200
    except ValueError as e:
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'server error': str(e)}), 500


@app.route('/stock/<string:symbol>', methods=['DELETE'])
def remove_stock(symbol):
    pass

@app.route('/stock-value/<string:symbol>', methods=['GET'])
#TESTED for a valid stock in the portfolio. TODO: check what expected from a stock not in the portfolio
def stock_value(symbol):
    # check valid symbol
    #TODO: the ninja api accepts also lower case symbols. should we check for that?
    if not symbol:
        return jsonify({'error': 'Malformed data'}), 400

    # get current value from service
    value = stock_service.get_stock_value(symbol)
    return jsonify({'value': value}), 200


@app.route('/portfolio-value', methods=['GET'])
def portfolio_value():
    pass


if __name__ == '__main__':
    app.run(debug=True)