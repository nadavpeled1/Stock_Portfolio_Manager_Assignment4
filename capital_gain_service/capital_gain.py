import logging
import os

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG to see detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Read stock service ports from environment variables
STOCK_SERVICE_1_PORT = os.getenv("STOCK_SERVICE_1_PORT", "8000")
STOCK_SERVICE_2_PORT = os.getenv("STOCK_SERVICE_2_PORT", "8000")

# Dynamically construct URLs based on ports
STOCK_SERVICE_1_URL = f"http://stock_service-container-1:{STOCK_SERVICE_1_PORT}/stocks"
STOCK_SERVICE_2_URL = f"http://stock_service-container-2:{STOCK_SERVICE_2_PORT}/stocks"
STOCK_SERVICE_1_VALUE_URL = f"http://stock_service-container-1:{STOCK_SERVICE_1_PORT}/stock-value"
STOCK_SERVICE_2_VALUE_URL = f"http://stock_service-container-2:{STOCK_SERVICE_2_PORT}/stock-value"


@app.route('/capital-gains', methods=['GET'])
def get_capital_gains():
    logging.info("Received a request for capital gains")

    # Query parameters
    portfolio = request.args.get('portfolio')
    numSharesGt = request.args.get('numSharesGt', type=int)
    numSharesLt = request.args.get('numSharesLt', type=int)
    logging.info(f"Query parameters - portfolio: {portfolio}, numSharesGt: {numSharesGt}, numSharesLt: {numSharesLt}")


    # Fetch data from stock services
    stock_data = []
    try:
        if not portfolio or portfolio == "stocks1":
            logging.info(f"Fetching data from {STOCK_SERVICE_1_URL}")
            stock_data += requests.get(STOCK_SERVICE_1_URL).json()
        if not portfolio or portfolio == "stocks2":
            logging.info(f"Fetching data from {STOCK_SERVICE_2_URL}")
            stock_data += requests.get(STOCK_SERVICE_2_URL).json()
    except requests.RequestException as e:
        logging.error(f"Error fetching data from stock services: {e}")
        return jsonify({"error": f"Failed to fetch data from stock services: {str(e)}"}), 500

    logging.info(f"Fetched stock data: {stock_data}")

    # Filter stocks
    filtered_stocks = [
        stock for stock in stock_data
        if '_id' in stock and 'shares' in stock and 'purchase_price' in stock and
           (numSharesGt is None or stock['shares'] > numSharesGt) and
           (numSharesLt is None or stock['shares'] < numSharesLt)
    ]
    logging.info(f"Filtered stock data: {filtered_stocks}")

    # Fetch current prices and calculate capital gains
    capital_gains = 0
    for stock in filtered_stocks:
        try:
            # Determine the correct stock service for the stock
            stock_value_url = (
                f"{STOCK_SERVICE_1_VALUE_URL}/{stock['id']}"
                if portfolio == "stocks1" or stock['portfolio'] == "stocks1"
                else f"{STOCK_SERVICE_2_VALUE_URL}/{stock['id']}"
            )
            logging.info(f"Fetching current value for stock ID {stock['id']} from {stock_value_url}")
            response = requests.get(stock_value_url).json()
            current_price = response.get("current_price", 0)

            # Calculate the gain for this stock
            capital_gains += (current_price - stock['purchase_price']) * stock['shares']
        except requests.RequestException as e:
            logging.error(f"Error fetching current value for stock ID {stock['id']}: {e}")
            continue

    logging.info(f"Calculated total capital gains: {capital_gains}")

    return jsonify({"capital_gains": capital_gains})


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 8080))
    logging.info(f"Starting Capital Gain Service on port {port}")
    app.run(host='0.0.0.0', port=port)
