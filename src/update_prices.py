import os
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.environ['STOCK_DATA_DIR'])



def fetch_recent_price_data(tickers, period):
    data = yf.download(
        tickers,
        period = period,
        interval = '1d',
        auto_adjust = True,
        progress = False,
        # group_by = 'ticker',
    )

    # for ticker in tickers:
    #     ticker_data = data[ticker]
    #     ticker_data = ticker_data[['Open', 'High', 'Low', 'Close', 'Volume']]

    if(isinstance(data.columns, pd.MultiIndex)):
        data.columns = data.columns.droplevel('Ticker')

    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    return data


def update_price_data(ticker):
    output_dir = DATA_DIR / 'prices'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{ticker}.csv'

    # new_data = fetch_recent_price_data(ticker, '5d')

    if(output_path.exists()):
        old_data = pd.read_csv(
            output_path,
            index_col = 'Date',
            parse_dates = True,
        )

        new_data = fetch_recent_price_data(ticker, '5d')

        data = pd.concat([old_data, new_data])
        data = data[~data.index.duplicated(keep='last')]
        data = data.sort_index()

    else:
        data = fetch_recent_price_data(ticker, '1y')

    data.to_csv(output_path)

    print(f'Updated: {ticker}')
    print(f'Latest date: {data.index[-1]}')



def main():
    update_price_data('SES')

    # update_price_data(['SNOW', 'USAR'])


if __name__ == '__main__':
    main()


