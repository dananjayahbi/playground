import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

# Function to fetch data and save to CSV
def fetch_and_save_data(ticker, start_date, end_date, interval, file_name):
    # Fetch historical data with the specified interval (e.g., '30m' for 30-minute data)
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)

    # Check if data is fetched
    if data.empty:
        print(f"No data available for {start_date} to {end_date}")
        return

    # Save data to CSV (or append to it if the file already exists)
    if not os.path.exists(file_name):
        # If file doesn't exist, create it
        data.to_csv(file_name)
    else:
        # Append new data to the existing file
        existing_data = pd.read_csv(file_name, index_col=0, parse_dates=True)
        
        # Avoid duplicates by concatenating and dropping duplicate index rows
        updated_data = pd.concat([existing_data, data])
        updated_data = updated_data[~updated_data.index.duplicated(keep='last')]

        # Save the updated data
        updated_data.to_csv(file_name)

    print(f"Data saved from {start_date} to {end_date}")

# Function to fetch data in smaller chunks (60 days at a time)
def fetch_data_in_batches(ticker, start_date, end_date, interval, file_name):
    current_start = start_date
    while current_start < end_date:
        # Calculate the end date for this chunk (60 days ahead)
        current_end = current_start + timedelta(days=60)
        if current_end > end_date:
            current_end = end_date
        
        # Fetch and save data for this chunk
        fetch_and_save_data(ticker, current_start.strftime('%Y-%m-%d'), current_end.strftime('%Y-%m-%d'), interval, file_name)
        
        # Move to the next 60-day chunk
        current_start = current_end + timedelta(days=1)

# Main execution
if __name__ == "__main__":
    ticker = 'EURUSD=X'  # EUR/USD Forex pair
    file_name = 'forex_data.csv'  # Output CSV file
    interval = '30m'  # Use 30-minute intervals for data

    # Define your start and end date here (customizable)
    start_date = datetime(2024, 6, 1)  # Example: June 1, 2024
    end_date = datetime.today()  # Current date
    
    # Fetch data in batches
    fetch_data_in_batches(ticker, start_date, end_date, interval, file_name)
