import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pmdarima.arima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
import warnings
from statsmodels.tools.sm_exceptions import ConvergenceWarning

# Ignore convergence warnings from statsmodels
warnings.simplefilter("ignore", ConvergenceWarning)

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def fetch_stocks_data(ticker_list, time_period):
    """
    Fetch stock data from Yahoo Finance for multiple tickers and transform
    it into a tidy DataFrame with columns: Open, High, Low, Close, Volume, Ticker.
    The Date column will be set as the index.
    
    Parameters:
    - ticker_list: List of ticker symbols (e.g., ['AAPL', 'GOOG', 'MSFT', 'TSLA'])
    - time_period: '1m', '3m', '6m', or '1y'
    
    Returns:
    - Combined DataFrame with data for all tickers, or None if an error occurs.
    """
    logging.info("Fetching data for multiple tickers...")
    
    try:
        # Set end_date to the most recent trading day
        end_date = datetime.now()
        # Adjust end_date if today is weekend (market closed)
        if end_date.weekday() == 5:      # Saturday
            end_date -= timedelta(days=1)
        elif end_date.weekday() == 6:    # Sunday
            end_date -= timedelta(days=2)
        
        # Determine the unit and value from the custom_period string.
        # Expected formats: "15y", "6m", "30d", etc.
        unit = time_period[-1].lower()
        try:
            value = int(time_period[:-1])
        except ValueError:
            raise ValueError("Period must be a number followed by 'y', 'm', or 'd' (e.g., '15y', '6m', '30d').")
        
        # Calculate the start_date using relativedelta for years and months.
        if unit == 'y':
            start_date = end_date - relativedelta(years=value)
        elif unit == 'm':
            start_date = end_date - relativedelta(months=value)
        elif unit == 'd':
            start_date = end_date - timedelta(days=value)
        else:
            raise ValueError("Invalid period format. Use a number followed by 'y' (years), 'm' (months), or 'd' (days).")
        
        # Download data for all tickers at once
        df = yf.download(
            ticker_list,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            progress=False
        )
        
        if df.empty:
            logging.warning("No data found for provided tickers.")
            return None

        # When multiple tickers are passed, yfinance returns a MultiIndex on columns.
        # Stack the data into a long (tidy) format.
        df = df.stack(level=1, future_stack=True).rename_axis(['Date', 'Ticker']).reset_index()
        
         # Remove any unwanted column name (e.g. "Price") from the columns Index.
        df.columns.name = None
        
        # Set the Date column as the index for easier time series analysis.
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        # Optionally, reorder columns if desired (e.g., Ticker as a column, then Open, High, Low, Close, Volume)
        df = df[['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        logging.info("Successfully fetched and transformed data for multiple tickers.")
        return df
    
    except Exception as e:
        logging.error(f"Error fetching data for multiple tickers: {e}")
        return None
def preprocess_data(df):
    """
    Preprocess stock data (with Date as the index) and calculate technical indicators
    separately for each ticker. Then, standardize selected exogenous variables.
    
    Parameters:
    - df: DataFrame with Date as index and columns: Ticker, Open, High, Low, Close, Volume, 
          and additional engineered indicators.
    
    Returns:
    - DataFrame with additional technical indicator columns and standardized exogenous variables,
      or None if an error occurs.
    
    Note:
    - The grouping by 'Ticker' ensures that rolling calculations and standardization are applied
      within each stock's own time series.
    """
    logging.info("Preprocessing data and calculating technical indicators...")
    
    try:        
        # Ensure the index is a DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Forward-fill missing values
        df = df.ffill()
        
        # Define a function to compute technical indicators for a single ticker's data.
        def compute_indicators(sub_df):
            # Sort the data by index (date) for correct rolling calculations.
            sub_df = sub_df.sort_index()
            
            # Calculate moving averages (MA5, MA20) with minimum periods equal to the window size.
            sub_df['MA5'] = sub_df['Close'].rolling(window=5, min_periods=5).mean()
            sub_df['MA20'] = sub_df['Close'].rolling(window=20, min_periods=20).mean()
            
            # Calculate MACD: EMA12, EMA26, MACD, and Signal line.
            sub_df['EMA12'] = sub_df['Close'].ewm(span=12, adjust=False).mean()
            sub_df['EMA26'] = sub_df['Close'].ewm(span=26, adjust=False).mean()
            sub_df['MACD'] = sub_df['EMA12'] - sub_df['EMA26']
            sub_df['Signal'] = sub_df['MACD'].ewm(span=9, adjust=False).mean()
            
            # Calculate RSI over a 14-day window.
            delta = sub_df['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14, min_periods=14).mean()
            avg_loss = loss.rolling(window=14, min_periods=14).mean()
            rs = avg_gain / avg_loss
            sub_df['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate Daily Returns (percentage change).
            sub_df['Daily_Return'] = sub_df['Close'].pct_change() * 100
            
            # Calculate Volatility: 21-day rolling standard deviation of daily returns.
            sub_df['Volatility'] = sub_df['Daily_Return'].rolling(window=21, min_periods=21).std()
            
            # Standardize selected exogenous variables for this ticker.
            # These are the variables you'll later use as regressors in your ARIMAX model.
            exog_standard_cols = ['Open', 'Volume', 'MA20', 'Signal', 'RSI', 'Daily_Return', 'Volatility']
            scaler = StandardScaler()
            # Fit and transform only if there are enough non-NA values.
            sub_df[exog_standard_cols] = scaler.fit_transform(sub_df[exog_standard_cols])
            
            return sub_df
        
        # Group the data by 'Ticker' and apply the technical indicator calculations and standardization.
        # Using include_groups=False to avoid including the grouping column in the transformation.
        #df = df.groupby('Ticker').apply(compute_indicators, include_groups=False)
        df = df.groupby('Ticker', group_keys=False).apply(compute_indicators)
        
        # Drop rows with NaN values that result from the rolling calculations.
        df_clean = df.dropna().copy()
        
        logging.info(f"Preprocessing complete. {len(df_clean)} valid data points after calculating indicators.")
        return df_clean
    
    except Exception as e:
        logging.error(f"Error during preprocessing: {e}")
        return None
def build_arimax_model(df, forecast_days=7, exog_cols=None):
    """
    Build an ARIMAX model using specified exogenous variables (technical indicators)
    to forecast the 'Close' price for a given stock. The DataFrame should have Date as index.

    Parameters:
    - df: Preprocessed DataFrame, with Date as the index.
          It should contain the target variable 'Close' and technical indicators.
    - forecast_days: Number of days to forecast (default is 7).
    - exog_cols: List of column names to be used as exogenous regressors.
                 If None, defaults to ['RSI', 'MACD', 'Volatility'].

    Returns:
    - A dictionary containing:
      - 'forecast': The point forecasts as a NumPy array.
      - 'forecast_dates': A list of forecast dates (as strings).
      - 'confidence_intervals': A dict with 'lower' and 'upper' bounds arrays.
      - 'trend': A simple label ("UPWARD", "DOWNWARD", or "NEUTRAL") based on the forecast.
      - 'expected_return': The percentage change from current price to the forecasted price.
      - 'current_price': The last observed closing price.
      - 'model_info': A dictionary with details (order and AIC) of the fitted ARIMAX model.
    """

    logging.info("Building ARIMAX model and generating forecasts...")

    try:
        # Define default exogenous regressors if not provided.
        if exog_cols is None:
            exog_cols = ['Open', 'Volume', 'MA20', 'Signal', 'RSI', 'Daily_Return', 'Volatility']
        
        # Extract the target series (closing prices) and exogenous variables.
        y = df['Close'].values
        X = df[exog_cols].values
        
        # Use auto_arima to select the best ARIMAX model order using the exogenous regressors.
        model = auto_arima(
            y,
            exogenous=X,
            start_p=1, start_q=1,
            max_p=3, max_q=3,
            d=1,
            seasonal=False,
            trace=True,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True,
            maxiter=100,  # Increase max iterations
            method='nm'  # Try Nelder-Mead optimizer
        )
        order = model.order
        logging.info(f"Best ARIMAX model order: {order}")
        
        # Fit the ARIMAX model using the selected order.
        arimax_model = ARIMA(y, order=order, exog=X)
        arimax_result = arimax_model.fit()
        
        # For forecasting, we need exogenous values for the forecast period.
        # We assume that the exogenous variables remain constant at their last observed values.
        last_exog = X[-1, :].reshape(1, -1)  # shape (1, number_of_exog)
        forecast_exog = np.repeat(last_exog, forecast_days, axis=0)
        
        # Generate forecasts using the fitted ARIMAX model.
        forecast_results = arimax_result.get_forecast(steps=forecast_days, exog=forecast_exog)
        forecast = forecast_results.predicted_mean
        conf_int = forecast_results.conf_int(alpha=0.05)
        
        # Extract confidence intervals whether conf_int is a DataFrame or a NumPy array.
        if isinstance(conf_int, pd.DataFrame):
            lower_bounds = conf_int.iloc[:, 0].values
            upper_bounds = conf_int.iloc[:, 1].values
        else:
            lower_bounds = conf_int[:, 0]
            upper_bounds = conf_int[:, 1]
        
        # Generate forecast dates based on the last date in the DataFrame's index.
        last_date = pd.to_datetime(df.index[-1])
        forecast_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(forecast_days)]
        
        # Calculate the expected return and trend based on the last observed price.
        current_price = y[-1]
        expected_return = ((forecast[-1] - current_price) / current_price) * 100
        trend = "UPWARD" if forecast[-1] > current_price else "DOWNWARD" if forecast[-1] < current_price else "NEUTRAL"
        
        prediction_results = {
            'forecast': forecast,
            'forecast_dates': forecast_dates,
            'confidence_intervals': {
                'lower': lower_bounds,
                'upper': upper_bounds
            },
            'trend': trend,
            'expected_return': expected_return,
            'current_price': current_price,
            'model_info': {
                'arimax_order': order,
                'aic': arimax_result.aic
            }
        }
        
        logging.info(f"Forecast complete. Trend: {trend}, Expected return: {expected_return:.2f}%")
        return prediction_results

    except Exception as e:
        logging.error(f"Error during ARIMAX model building: {e}")
        return None
# ----------------------------
# Pipeline to Process and Forecast for Each Stock
# ----------------------------
def run_pipeline(ticker_list, time_period, forecast_days=7, exog_cols=None):
    """
    Complete pipeline: Fetch data, preprocess it, and build ARIMAX forecasts for each ticker.
    
    Parameters:
    - preprocessed_df: DataFrame with Date as index and columns including 'Ticker' and 'Close'.
    - forecast_days: Number of days to forecast (default is 7).
    
    Returns:
    - A dictionary where keys are ticker symbols and values are the forecast results dictionary.
    """
    # Fetch raw data
    raw_data = fetch_stocks_data(ticker_list, time_period)
    if raw_data is None:
        logging.error("No raw data fetched. Pipeline aborted.")
        return None
    
    # Preprocess data (compute indicators and standardize exogenous variables)
    preprocessed_data = preprocess_data(raw_data)
    if preprocessed_data is None:
        logging.error("Preprocessing failed. Pipeline aborted.")
        return None
        
    predictions = {}
    
    # Get the unique tickers present in the DataFrame.
    tickers = preprocessed_data['Ticker'].unique()
    
    for ticker in tickers:
        logging.info(f"Building prediction for {ticker}...")
        # Select data for the ticker.
        df_ticker = preprocessed_data[preprocessed_data['Ticker'] == ticker].copy()
        
        # Ensure the DataFrame is sorted by date.
        df_ticker = df_ticker.sort_index()
        
        # Call the prediction model function for this ticker.
        pred = build_arimax_model(df_ticker, forecast_days=forecast_days, exog_cols=exog_cols)
        predictions[ticker] = pred
        
    return predictions
TICKERS = ["AAPL", "GOOG", "MSFT", "TSLA"]
TIME_PERIOD = '13y'  # Options: '1m', '3m', '6m', '1y'
FORECAST_DAYS = 7
col = ['Open', 'Volume', 'MA20', 'Signal', 'RSI', 'Daily_Return', 'Volatility']
# Example usage:
# Assume `preprocessed_data` is your DataFrame after calling preprocess_data()
all_predictions = run_pipeline(ticker_list = TICKERS, time_period = TIME_PERIOD, exog_cols=col)

# To print the prediction for each ticker:
for ticker, prediction in all_predictions.items():
    print(f"Ticker: {ticker}")
    print(prediction)
    print("-----------------------------------------------------------------------------------------------------------------------------------")
