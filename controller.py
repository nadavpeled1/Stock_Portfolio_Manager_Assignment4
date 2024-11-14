# controller.py

from flask import Flask, request, jsonify
from service import StockService

app = Flask(__name__)
stock_service = StockService()

# /stocks is a collection of stock objects. These stocks comprise the portfolio.
# /stocks/{id} is the stock object in /stocks with the given id.
# /stock-value/{id} is the current value of the given stock in the portfolio (= current stock price times number of shares).
# /portfolio-value is the current value of the entire portfolio.




def validate_stock_data(data):
    #TODO: should we also check the type of the values? e.g. shares should be int. is it fine to send it as a string?
    #TODO: what is expected if a required fields is an empty string? now an empty string is considered as a valid value

    # required fields check
    if not all(
        required_param in data and data[required_param]
        for required_param in ('symbol', 'purchase_price', 'shares')
    ):
        return False
    # type checking
    if not isinstance(data['symbol'], str):
        return False
    if not isinstance(data['purchase_price'], (float, int)):
        return False
    if not isinstance(data['shares'], int):
        return False
    return True
'''
 POST: The POST request provides a JSON object payload that must contain: 'symbol', 'purchase price', 'shares' fields.
 Optionally it can also provide the ‘name’ and 'purchase date' of the stock.
 If successful, it returns the JSON for the id * assigned to that object with status code 201.
 Possible error status codes returned: 400, 415, 500.
'''
@app.route('/stocks', methods=['POST'])
def add_stock():
    try:
        if not request.is_json:
            return jsonify({'error': 'Unsupported Media Type'}), 415
        data = request.get_json()

        if not validate_stock_data(data):
                    return jsonify({'error': 'Bad Request'}), 400
        name = data.get('name', 'NA')
        purchase_date = data.get('purchase_date', 'NA')
        symbol = data['symbol']
        purchase_price = data['purchase_price']
        shares = data['shares']
        # note: id is generated in the service layer
        stock = stock_service.add_stock(symbol, purchase_price, shares, name, purchase_date)
        return jsonify({'id': stock.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

'''
GET: If successful, it returns a JSON array of stock objects with status code 200.
Possible error status codes returned: 500. For this assignment, you need to
support query strings of the form <field>=<value>.
'''
@app.route('/stocks', methods=['GET'])
def get_stocks():
    try:
        return jsonify([stock.__dict__ for stock in stock_service.portfolio.values()]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stock/<string:symbol>', methods=['DELETE'])
def remove_stock(symbol):
    pass

@app.route('/stock-value/<string:symbol>', methods=['GET'])
def stock_value(symbol):
    pass

@app.route('/portfolio-value', methods=['GET'])
def portfolio_value():
    pass

if __name__ == '__main__':
    app.run(debug=True)