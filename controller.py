# controller.py

from flask import Flask, request, jsonify
from service import StockService

app = Flask(__name__)
stock_service = StockService()

# /stocks is a collection of stock objects. These stocks comprise the portfolio.
# /stocks/{id} is the stock object in /stocks with the given id.
# /stock-value/{id} is the current value of the given stock in the portfolio (= current stock price times number of shares).
# /portfolio-value is the current value of the entire portfolio.

@app.route('/stocks', methods=['POST'])
def add_stock():
    data = request.json
    stock_service.add_stock(data['symbol'], data['quantity'])
    return jsonify({"message": "Stock added successfully"}), 200

@app.route('/stock/<string:symbol>', methods=['DELETE'])
def remove_stock(symbol):
    data = request.json
    try:
        stock_service.remove_stock(symbol, data['quantity'])
        return jsonify({"message": "Stock removed successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/stock-value/<string:symbol>', methods=['GET'])
def stock_value(symbol):
    stock_prices = request.json
    try:
        value = stock_service.get_portfolio_value({symbol: stock_prices[symbol]})
        return jsonify({"stock_value": value}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/portfolio-value', methods=['GET'])
def portfolio_value():
    stock_prices = request.json
    try:
        value = stock_service.get_portfolio_value(stock_prices)
        return jsonify({"portfolio_value": value}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)