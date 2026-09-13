import os
from pathlib import Path

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.environ['STOCK_DATA_DIR'])

MASTER_PATH = DATA_DIR / 'master' / 'master.csv'
PRICE_DIR = DATA_DIR / 'prices'

BATCH_SIZE = 100



def load_active_tickers():
    master = pd.read_csv(
        MASTER_PATH,
        encoding='utf-8',
    )

    active_stocks = master[
        master['Status'] == 'active'
    ]

    tickers = active_stocks['Ticker'].tolist()

    return tickers



def classify_tickers(tickers):
    new_tickers = []
    existing_tickers = []

    for ticker in tickers:
        price_path = PRICE_DIR / f'{ticker}.csv'

        if(price_path.exists()):
            existing_tickers.append(ticker)
        else:
            new_tickers.append(ticker)

    return new_tickers, existing_tickers



def split_into_batches(tickers, batch_size=BATCH_SIZE):
    for i in range(0, len(tickers), batch_size):
        yield tickers[i:i+batch_size]



def fetch_batch(tickers, period):
    if not tickers:
        return None

    data = yf.download(
        tickers,
        period = period,
        interval = '1d',
        auto_adjust = True,
        progress = False,
        group_by = 'ticker',
    )

    return data



def extract_ticker_data(data, ticker, number_of_tickers):
    if data is None or data.empty:
        return None

    if(number_of_tickers==1):
        ticker_data = data.copy()

        if isinstance(ticker_data.columns, pd.MultiIndex):
            ticker_data.columns = ticker_data.columns.droplevel('Ticker')

    else:
        try:
            ticker_data = data[ticker].copy()
        except KeyError:
            return None


    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    if not all(
        column in ticker_data.columns
        for column in required_columns
    ):
        return None

    ticker_data = ticker_data[required_columns]
    ticker_data = ticker_data.dropna(how='all')

    return ticker_data



def save_new_price_data(ticker, ticker_data):
    output_path = PRICE_DIR / f'{ticker}.csv'

    ticker_data = ticker_data.sort_index()
    ticker_data.to_csv(
        output_path,
        encoding='utf-8',
    )



def update_existing_price_data(ticker, ticker_data):
    output_path = PRICE_DIR / f'{ticker}.csv'

    old_data = pd.read_csv(
        output_path,
        index_col='Date',
        parse_dates=True,
    )

    combined_data = pd.concat([old_data, ticker_data])

    combined_data = combined_data[
        ~combined_data.index.duplicated(keep='last')
    ]

    combined_data = combined_data.sort_index()

    combined_data.to_csv(
        output_path,
        encoding='utf-8',
    )



def process_batch(tickers, period, is_new):
    if not tickers:
        return

    data = fetch_batch(
        tickers,
        period = period,
    )

    for ticker in tickers:
        try:
            ticker_data = extract_ticker_data(
                data, ticker, len(tickers)
            )

            if ticker_data is None or ticker_data.empty:
                print(f'No data: {ticker}')
                continue

            if is_new:
                save_new_price_data(ticker, ticker_data)
                print(f'Created: {ticker}')
            else:
                update_existing_price_data(ticker, ticker_data)
                print(f'Updated: {ticker}')

        except Exception as error:
            print(f'Failed: {ticker} ({error})')



def update_prices():
    PRICE_DIR.mkdir(
        parents = True,
        exist_ok = True,
    )

    tickers = load_active_tickers()
    # tickers = tickers[:10] #動作チェック
    new_tickers, existing_tickers = classify_tickers(tickers)

    print(f'Active stocks: {len(tickers)}')
    print(f'New stocks: {len(new_tickers)}')
    print(f'Existing stocks: {len(existing_tickers)}')

    print('\nUpdating new stocks ...')
    for batch in split_into_batches(new_tickers):
        print(f'Fetching batch: {len(batch)} stocks')
        process_batch(
            batch,
            period = '1y',
            is_new = True,
        )

    print('\nUpdating existing stocks ...')
    for batch in split_into_batches(existing_tickers):
        print(f'Fetching batch: {len(batch)} stocks')
        process_batch(
            batch,
            period = '5d',
            is_new = False,
        )




def main():
    update_prices()



if __name__ == '__main__':
    main()


