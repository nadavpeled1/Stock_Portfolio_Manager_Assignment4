import time
import requests
from requests import RequestException
from bson import ObjectId
from stock import Stock

NINJA_API_KEY = "t7kGKURsW31xlUX9jhmX6Q==JKxHUYND1othy0fC"
API_URL = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'


class StockService:
    def __init__(self, stocks_collection):
        self.stocks_collection = stocks_collection

    def add_stock(self, symbol: str, purchase_price: float, shares: int,
                  name: str = 'NA', purchase_date: str = 'NA') -> dict:
        """
         Inserts a new stock into the MongoDB collection.
         """
        new_stock = {
            "name": name,
            "symbol": symbol,
            "purchase_price": round(purchase_price, 2),
            "purchase_date": purchase_date,
            "shares": shares
        }
        result = self.stocks_collection.insert_one(new_stock)
        return self.stocks_collection.find_one({"_id": result.inserted_id})

    def get_stock_by_id(self, stock_id: str) -> dict:
        try:
            stock = self.stocks_collection.find_one({"_id": self.convert_to_object_id(stock_id)})
            if not stock:
                raise KeyError(f"Stock with id '{stock_id}' not found in the portfolio.")
            return stock
        except Exception as e:
            raise KeyError(f"Stock with id '{stock_id}' not found. Ensure the ID is correct: {e}.")

    def delete_stock(self, stock_id: str) -> int:
        """
         Deletes a stock by its ID.
         Returns: The number of documents deleted (0 or 1).
         """
        try:
            result = self.stocks_collection.delete_one({"_id": self.convert_to_object_id(stock_id)})
            return result.deleted_count
        except Exception as e:
            raise KeyError(f"Error deleting stock with id '{stock_id}': {e}")

    def update_stock(self, stock_id: str, updated_data: dict) -> int:
        """
        Updates a stock's fields by its ID.
        Returns: The number of documents updated (0 or 1).
        """
        try:
            result = self.stocks_collection.update_one(
                {"_id": self.convert_to_object_id(stock_id)},
                {"$set": updated_data}
            )
            return result.modified_count
        except Exception as e:
            raise KeyError(f"Stock with id '{stock_id}' not found. Ensure the ID is correct: {e}.")

    @staticmethod
    def fetch_stock_current_price(symbol: str, retries=3, delay=2) -> float:
        """
        For more info: https://api-ninjas.com/api/stockprice
        """
        for attempt in range(retries):
            try:
                # Ensure the symbol is valid and properly formatted
                symbol = symbol.strip().upper()
                response = requests.get(API_URL.format(symbol), headers={'X-Api-Key': NINJA_API_KEY}, timeout=10)

                if response.status_code == requests.codes.ok:
                    response_json = response.json()
                    if 'price' in response_json:
                        return response_json['price']
                    else:
                        # Treat empty or unexpected responses as invalid symbols
                        raise ValueError(f"Invalid stock symbol: {symbol}")
                else:
                    raise ValueError(f"Unexpected status code: {response.status_code}")

            except RequestException as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise ValueError(f"API request failed after {retries} attempts: {str(e)}")

    def get_stock_value(self, stock_id: str) -> dict:
        try:
            stock = self.get_stock_by_id(stock_id)
        except KeyError:
            raise KeyError(f"Stock with ID '{stock_id}' not found.")
        try:
            current_price = round(self.fetch_stock_current_price(stock.symbol), 2)
            stock_value = round(stock.shares * current_price, 2)

            # Return the required data as a dictionary
            return {
                "symbol": stock.symbol,
                "ticker": current_price,
                "stock value": stock_value
            }
        except Exception as e:
            raise ValueError(f"Error fetching stock value for '{stock.symbol}': {str(e)}")

    def get_stocks(self) -> list[dict[str, any]]:
        """
        Returns:
            A list of stock objects represented as dictionaries.
        """
        if not self.portfolio or not isinstance(self.portfolio, dict):
            return []

        return [stock.to_dict() for stock in self.portfolio.values()]

    def get_portfolio_value(self) -> float:
        total_value = 0.0
        try:
            for stock in self.portfolio.values():
                current_price = self.fetch_stock_current_price(stock.symbol)
                if current_price:
                    total_value += stock.shares * current_price
                else:
                    raise ValueError(f"Price for stock '{stock.symbol}' (id: {stock.id}) "
                                     f"is not available. Please update the symbol.")
            return round(total_value, 2)
        except Exception as e:
            raise ValueError(f"Error calculating portfolio value: {str(e)}")

    def symbol_exists(self, symbol: str) -> bool:
        return any(stock.symbol == symbol for stock in self.portfolio.values())

    def stock_id_exists(self, stock_id: str) -> bool:
        return stock_id in self.portfolio

    @staticmethod
    def convert_to_object_id(stock_id: str) -> ObjectId:
        try:
            return ObjectId(stock_id)
        except Exception:
            raise ValueError(f"Invalid stock ID format: '{stock_id}'")
