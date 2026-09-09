import os
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.environ['STOCK_DATA_DIR'])



def fetch_price_data(ticker, period='1mo'):
    data = yf.download(
        ticker,
        period = period,
        interval = '1d',
        auto_adjust = True,
        progress = False,
    )

    return data



def process_price_data(data):
    if(isinstance(data.columns, pd.MultiIndex)):
        data.columns = data.columns.droplevel('Ticker')

    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

    return data


def save_price_data(data, ticker):
    output_dir = DATA_DIR / 'prices'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f'{ticker}.csv'
    data.to_csv(output_path)


    print(f'Saved: {output_path}')



def main():
    ticker = 'ASTS'

    data = fetch_price_data(ticker)
    data = process_price_data(data)
    save_price_data(data, ticker)


if __name__ == '__main__':
    main()
