from app.extensions import database, session
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import jsonpickle
import zlib


class StockForecast(database.Model):
    __tablename__ = "stock_forecasts"

    id = database.Column(database.Integer, primary_key=True)
    ticker = database.Column(database.String(10), nullable=False)
    retrieved_data = database.Column(database.Text, nullable=False)
    forecast = database.Column(database.Text, nullable=False)
    created_at = database.Column(database.DateTime(timezone=True), server_default=func.now())


    def __repr__(self):
        return f'<Chat {self.id}>'

    
    def serialize(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            "retrieved_data": self.deserialize_data(self.retrieved_data),
            "forecast": self.deserialize_data(self.forecast)
        }
    
    def deserialize_data(self, data):
        try:
            return jsonpickle.decode(data)
        except Exception as e:
            print(f"Error decoding data: {e}")
            return None