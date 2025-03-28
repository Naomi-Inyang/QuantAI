import schedule
import time
import logging

from app.jobs.jobs import fetch_stocks_data, preprocess_data, build_arimax_model

# Test
def job():
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

    logging.info("Scheduled job completed.")

# Schedule job every 12 hours
schedule.every(12).hours.do(job)

logging.info("Scheduler started. Running job every 12 hours...")

while True:
    schedule.run_pending()
    time.sleep(60) # Wait a min
