# stock.py

class Stock:
    def __init__(self, id: str, name: str, symbol: str, purchase_price: float, purchase_date: str, shares: int):
        self.id = id  # ID will be auto-generated
        self.name = name
        self.symbol = symbol
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.shares = shares

    def __repr__(self):
        return (f"Stock(id={self.id}, name={self.name}, symbol={self.symbol}, "
                f"purchase_price={self.purchase_price}, purchase_date={self.purchase_date}, shares={self.shares})")