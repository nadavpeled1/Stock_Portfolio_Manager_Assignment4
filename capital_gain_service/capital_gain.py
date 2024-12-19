import os

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Read stock service URLs from environment variables
STOCK_SERVICE_1_URL = os.getenv("STOCK_SERVICE_1_URL", "http://stock_service-container-1:8000/stocks")
STOCK_SERVICE_2_URL = os.getenv("STOCK_SERVICE_2_URL", "http://stock_service-container-2:8000/stocks")


@app.route('/capital-gains', methods=['GET'])
def get_capital_gains():
    # Query parameters
    portfolio = request.args.get('portfolio')
    numsharesgt = request.args.get('numsharesgt', type=int)
    numshareslt = request.args.get('numshareslt', type=int)

    # Fetch data from stock services
    stock_data = []
    if not portfolio or portfolio == "stocks1":
        stock_data += requests.get(STOCK_SERVICE_1_URL).json()
    if not portfolio or portfolio == "stocks2":
        stock_data += requests.get(STOCK_SERVICE_2_URL).json()

    # Filter stocks
    filtered_stocks = [
        stock for stock in stock_data
        if (numsharesgt is None or stock['num_shares'] > numsharesgt) and
           (numshareslt is None or stock['num_shares'] < numshareslt)
    ]

    # Calculate capital gains
    capital_gains = sum(
        (stock['current_price'] - stock['purchase_price']) * stock['num_shares'] for stock in filtered_stocks)
    return jsonify({"capital_gains": capital_gains})


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT"))
    app.run(host='0.0.0.0', port=port)
