import logging

from app.services.stock_forecast import fetch_stocks_data, preprocess_data, build_arimax_model
from app.helpers import add_records_to_database

# Test
def store_forecasts(app):
    with app.app_context():
        ticker_list = ['AAPL', 'GOOG', 'MSFT', 'TSLA']  
        time_period = '6m'  
        forecast_days = 7 

        logging.info("Starting scheduled pipeline job...")
        
        # Fetch and preprocess stock data
        df = fetch_stocks_data(ticker_list, time_period)
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


        #TODO: Hi Vera, pls store the results in the db here using add_records_to_database function, it's imported already
        #also refer to repository.base for updating already saved stocks

        #DOING:
        for ticker, forecast_data in results.items():
            if forecast_data is not None:
                logging.info(f"Saving forecast data ...")
                forecast_records = [
                    {"ticker": ticker, "date": date, "predicted_value": value}
                    for date, value in forecast_data.items()
                ]
                add_records_to_database(ticker, forecast_records)
            else:
                logging.warning(f"No forecast generated. Skipping database update.")

        logging.info("Scheduled job completed.")

