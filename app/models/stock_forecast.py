from app.extensions.database import database
from sqlalchemy import Column, Integer, String, Date, Numeric, TIMESTAMP, func

class StockForecast(database.Model):
    __tablename__ = "stock_forecasts"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False)
    date = Column(Date, nullable=False)
    predicted_value = Column(Numeric, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    __table_args__ = (database.UniqueConstraint("ticker", "date", name="unique_forecast"),)
