import os

from controller import StockController
from pymongo import MongoClient


def main():
    """
    Entry point for the Stock Portfolio Manager application.
    Initializes the StockController and runs the Flask app.
    """
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri)
        db = client["stock_portfolio"]
        stocks_collection = db["stocks"]

        controller = StockController(stocks_collection)

        # Run the Flask app
        controller.app.run(host='0.0.0.0', port=5001)

    except Exception as e:
        print(f"Error starting the Stock Portfolio Manager: {str(e)}")


if __name__ == '__main__':
    main()