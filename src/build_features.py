import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


load_dotenv()

DATA_DIR = Path(os.environ['STOCK_DATA_DIR'])


MASTER_PATH = (DATA_DIR / 'master' / 'master.csv')
PRICE_DIR = (DATA_DIR / 'prices')
OUTPUT_PATH = (DATA_DIR / 'scores' / 'features.csv')


def latest_features(data):
    latest = data.iloc[-1]

    return {
        'LatestDate': data.index[-1],
        'Close': latest['Close'],
        'Volume': latest['Volume'],
    }


def average_price(data, days):
    close = data['Close']

    if(len(close)<days):
        return {
            f'Average_{days}d': None
        }

    return {
        f'Average_{days}d': close.iloc[-days:].mean()
    }


def minmax_price(data, days):
    high = data['High']
    low = data['Low']
    if(len(data)<days):
        return {
            f'Max_{days}d': None,
            f'Min_{days}d': None,
        }

    return {
        f'Max_{days}d': high.iloc[-days:].max(),
        f'Min_{days}d': low.iloc[-days:].min(),
    }


FEATURE_FUNCTIONS = [
    (latest_features, {}),
    (average_price, {'days': 50}),
    (average_price, {'days': 150}),
    (average_price, {'days': 200}),
    (minmax_price, {'days': 240}),
]


def calculate_features(data):
    features = {}
    for function, kwargs in FEATURE_FUNCTIONS:
        features.update(
            function(data, **kwargs)
        )

    return features


def main():
    master = pd.read_csv(
        MASTER_PATH,
        encoding='utf-8',
    )

    active_tickers = (
        master.loc[
            master['Status'] == 'active',
            'Ticker',
        ].tolist()
    )

    results = []

    for i,ticker in enumerate(
        active_tickers,
        start = 1,
    ):
        price_path = (PRICE_DIR / f'{ticker}.csv')

        if not price_path.exists():
            print(
                f'Skip {ticker}: '
                f'price file not found.'
            )
            continue

        try:
            data = pd.read_csv(
                price_path,
                index_col = 'Date',
                parse_dates = True,
            )

            if(data.empty):
                print(
                    f'Skip {ticker}: '
                    f'empty price data.'
                )
                continue

            required_columns = ['Open', 'High', 'Low', 'Close']
            data = data.dropna(subset=required_columns)
            if(data.empty):
                print(
                    f'Skip {ticker}: '
                    f'no complete price data.'
                )
                continue

            features = calculate_features(data)
            features['Ticker'] = ticker
            results.append(features)

        except Exception as error:
            print(
                f'Failed {ticker}: {error}'
            )

        if(i%100==0):
            print(
                f'Processed '
                f'{i}/{len(active_tickers)}'
            )

    features_df = pd.DataFrame(results)
    features_df = (
        features_df.set_index('Ticker').sort_index()
    )

    OUTPUT_PATH.parent.mkdir(
        parents = True,
        exist_ok = True,
    )

    features_df.to_csv(
        OUTPUT_PATH,
        encoding='utf-8',
    )

    print(f'Saved features to {OUTPUT_PATH}')
    print(f'Tickers: {len(features_df)}')


if __name__ == '__main__':
    main()