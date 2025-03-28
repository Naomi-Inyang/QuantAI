import logging
from app.services.stock_forecast import fetch_stocks_data, preprocess_data, build_arimax_model
from app.helpers import add_records_to_database
from app.models import StockForecast
from app.extensions import session
import jsonpickle 

# Test
def store_forecasts(app):
     with app.app_context():
        ticker_list = ['AAPL', 'GOOG', 'MSFT', 'TSLA']  
        time_period = '6m'  
        forecast_days = 7 

        logging.info("Starting scheduled pipeline job...")
        
        # Fetch and preprocess stock data
        df, retrieved_stocks = fetch_stocks_data(ticker_list, time_period)
        if df is None:
            logging.error("No data fetched. Exiting job.")
            return
        
        df_preprocessed = preprocess_data(df)
        if df_preprocessed is None:
            logging.error("Data preprocessing failed. Exiting job.")
            return
        
        # Run ARIMAX model for each stock
        results = {}
        for ticker in ticker_list:
            logging.info(f"Processing ARIMAX model for {ticker}...")
            df_ticker = df_preprocessed[df_preprocessed['Ticker'] == ticker]
            if df_ticker.empty:
                logging.warning(f"No valid data for {ticker}. Skipping.")
                continue
            
            results[ticker] = build_arimax_model(df_ticker, forecast_days)

        formatted_predictions = {}

        for ticker, data in results.items():

            formatted_predictions[ticker] = [
                {"date": date, "price": round(price, 2)}
                for date, price in zip(data["forecast_dates"], data["forecast"])
            ]

        session.query(StockForecast).delete()
        session.commit()

        stock_forecast_info = []
        for ticker in ticker_list:
            stock_forecast_info.append(StockForecast(
                ticker=ticker,
                retrieved_data=jsonpickle.encode(retrieved_stocks[ticker]),
                forecast=jsonpickle.encode(formatted_predictions[ticker])
            ))

        add_records_to_database(stock_forecast_info)
        
