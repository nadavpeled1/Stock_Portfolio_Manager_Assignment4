from datetime import datetime


class Stock:
    def __init__(self, built_in_id: str, name: str, symbol: str,
                 purchase_price: float, purchase_date: str, shares: int):
        self.id = built_in_id  # ID will be auto-generated in the service
        self.name = name
        self.symbol = symbol
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.shares = shares

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date,
            'shares': self.shares
        }

    def __json__(self):
        return self.to_dict()

    def __repr__(self):
        return (f"Stock(id={self.id}, name={self.name}, symbol={self.symbol}, "
                f"purchase_price={self.purchase_price}, purchase_date={self.purchase_date}, shares={self.shares})")